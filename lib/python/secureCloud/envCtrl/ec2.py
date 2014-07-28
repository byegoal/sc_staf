import os
import re
import time
import logging
import boto.ec2
import testingServer
import staf


def zone2str(zone):
    m = re.search(r"Zone:(\S+)", str(zone))
    return m.group(1)


def prepareInstance(FILEPATH_REMOTEMACHINE, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AMI_ID, REGION, INSTANCE_TYPE, KEY_PAIR, ENVIRONMENT, ZONE=''):
    ## launch an EC2 instance and get the public DNS of the launched EC2 instance
    # Get EndPoint,INSTANCE_ID from configure, and launch a new instance if INSTANCE_ID is ""
    EndPoint = testingServer.get_config(
        FILEPATH_REMOTEMACHINE, "REMOTE_MACHINE", ENVIRONMENT)
    INSTANCE_ID = testingServer.get_config(
        FILEPATH_REMOTEMACHINE, "INSTANCE_ID", ENVIRONMENT)
    ONETIME = 1
    if EndPoint:
        if not testingServer.wait_STAF_service(EndPoint, ONETIME):
            return EndPoint
    if INSTANCE_ID:
        EndPoint = start_instance(AWS_ACCESS_KEY_ID,
                                  AWS_SECRET_ACCESS_KEY, REGION, INSTANCE_ID)
        testingServer.replace_config(FILEPATH_REMOTEMACHINE,
                                     "REMOTE_MACHINE", ENVIRONMENT, EndPoint)
        if EndPoint:
            return EndPoint
    # if instance not exist launch new instance
    EndPoint, NEW_INSTANCE_ID = launch_instance(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AMI_ID, REGION, INSTANCE_TYPE, KEY_PAIR, ENVIRONMENT, ZONE)
    EndPoint = EndPoint.encode('ascii', 'ignore')
    testingServer.replace_config(
        FILEPATH_REMOTEMACHINE, "REMOTE_MACHINE", ENVIRONMENT, EndPoint)
    testingServer.replace_config(FILEPATH_REMOTEMACHINE, "INSTANCE_ID",
                                 ENVIRONMENT, NEW_INSTANCE_ID)
    logging.info("Endpoint is [%s]" % EndPoint)
    return EndPoint


def teardownInstance(FILEPATH_REMOTEMACHINE, AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, REGION, ENVIRONMENT, TERMINATE=False):
    EndPoint = testingServer.get_config(
        FILEPATH_REMOTEMACHINE, "REMOTE_MACHINE", ENVIRONMENT)
    INSTANCE_ID = testingServer.get_config(
        FILEPATH_REMOTEMACHINE, "INSTANCE_ID", ENVIRONMENT)
    logging.debug("teardown instance by TEST_CASE_RESULT: %s" % TERMINATE)
    if not EndPoint:
        return -1

    # if instance_id can be found in config.ini, is an ebs instance
    if INSTANCE_ID:
        if TERMINATE:
            return_code = terminate_instance(AWS_ACCESS_KEY_ID,
                                             AWS_SECRET_ACCESS_KEY, REGION, EndPoint)
        else:
            return_code = stop_instance(AWS_ACCESS_KEY_ID,
                                        AWS_SECRET_ACCESS_KEY, REGION, EndPoint)

    else:
        return_code = terminate_instance(AWS_ACCESS_KEY_ID,
                                         AWS_SECRET_ACCESS_KEY, REGION, EndPoint)

    # clean up remote machine DNS in config
    testingServer.replace_config(
        FILEPATH_REMOTEMACHINE, "REMOTE_MACHINE", ENVIRONMENT, "")
    return return_code


def terminate_instance(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, REGION, EndPoint):
    ec2_conn = boto.ec2.connect_to_region(REGION, aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    try:
        INSTANCE_ID = _get_instance_id(AWS_ACCESS_KEY_ID,
                                       AWS_SECRET_ACCESS_KEY, REGION, EndPoint)

    except RuntimeError as e:
        logging.warn(e.message)
        return -1

    ec2_conn.terminate_instances(instance_ids=[INSTANCE_ID])
    return 0


def stop_instance(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, REGION, EndPoint):
    ec2_conn = boto.ec2.connect_to_region(REGION, aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)

    try:
        INSTANCE_ID = _get_instance_id(AWS_ACCESS_KEY_ID,
                                       AWS_SECRET_ACCESS_KEY, REGION, EndPoint)

    except RuntimeError as e:
        logging.warn(e.message)
        return -1

    ec2_conn.stop_instances(instance_ids=[INSTANCE_ID], force=True)
    return 0


def launch_instance(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AMI_ID, REGION, INSTANCE_TYPE, KEY_PAIR, ENVIRONMENT, ZONE=''):
    logging.debug("REGION:" + REGION + " AWS_ACCESS_KEY_ID:" + AWS_ACCESS_KEY_ID + " KEY_PAIR:" + KEY_PAIR + " AMI_ID:" + AMI_ID + " INSTANCE_TYPE:" + INSTANCE_TYPE + " ENVIRONMENT:" + ENVIRONMENT + " ZONE:" + ZONE)
    ec2_conn = boto.ec2.connect_to_region(REGION, aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    instance = _launch_instance(
        ec2_conn, AMI_ID, INSTANCE_TYPE, KEY_PAIR, ENVIRONMENT, ZONE)
    _wait_until_instance_running(instance)
    _set_instance_tag(ec2_conn, instance, ENVIRONMENT)
    LONGTIMES = 60
    """
    Windows2003_x86 AMI-ca4efbcd will auto reboot and change computer name when first created
    which will interrupt following testing.
    """
    if AMI_ID == "ami-ca4efbcb" or AMI_ID == "ami-2049fc21":
        logging.info("sleep 300 secs to wait for reboot finished")
        time.sleep(300)  # sec
    else:
        #experimental, wait instance boot and time synced
        time.sleep(180)  # sec

    testingServer.wait_STAF_service(instance.public_dns_name, LONGTIMES)
    return _return_instance_info(instance)


def _wait_until_instance_running(instance):
    logging.info("Wait until the EC2 instance is running ...")
    time.sleep(5.0)
    instance.update()
    while instance.state != "running":
        time.sleep(5.0)
        instance.update()
        logging.debug("Instance state changed to [" + instance.state + "]")


def _set_instance_tag(ec2_conn, instance, ENVIRONMENT):
    logging.info("Set instance TAG using boto ...")
    import socket
    hostname = socket.gethostbyname_ex(socket.gethostname())[0]
    ec2_conn.create_tags(
        [instance.id], {"Name": ENVIRONMENT + "-" + str(hostname)})


def _launch_instance(ec2_conn, AMI_ID, INSTANCE_TYPE, KEY_PAIR, ENVIRONMENT, ZONE):
    logging.info("Launch an EC2 instance using boto ...")
    if ZONE == "":
        zones = ec2_conn.get_all_zones()
        AVAILABILITY_ZONE = zone2str(zones[0])
    else:
        AVAILABILITY_ZONE = ZONE
    reservation = ec2_conn.run_instances(image_id=AMI_ID, key_name=KEY_PAIR,
                                         instance_type=INSTANCE_TYPE, placement=AVAILABILITY_ZONE)
    instance = reservation.instances[0]
    return instance


def _start_instances(ec2_conn, INSTANCE_ID):
    from boto.exception import EC2ResponseError
    try:
        instance = ec2_conn.start_instances(instance_ids=INSTANCE_ID)[0]
    except EC2ResponseError:
        import sys
        import traceback
        exc_type, exc_value, exc_traceback = sys.exc_info()
        logging.warn(repr(traceback.format_exception(
            exc_type, exc_value, exc_traceback)))
        return ""
    return instance


def _return_instance_info(instance):
    rootDeviceType = instance.root_device_type
    logging.info("The root device type of the launched EC2 instance is " +
                 rootDeviceType)
    if rootDeviceType == "ebs":
        return instance.public_dns_name, instance.id
    elif rootDeviceType == "instance-store":
        return instance.public_dns_name, ""


def start_instance(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, REGION, INSTANCE_ID):
    # start an EC2 instance using boto
    logging.info("Start an EC2 instance using boto ...")
    ec2_conn = boto.ec2.connect_to_region(REGION, aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    instance = _start_instances(ec2_conn, INSTANCE_ID)
    if not instance:
        return ""
    _wait_until_instance_running(instance)
    ## wait until STAF service is ready
    LONGTIMES = 20
    if testingServer.wait_STAF_service(instance.public_dns_name, LONGTIMES):
        return ""
    # return the public DNS of the launched EC2 instance
    logging.info("The public DNS of the started EC2 instance is " +
                 instance.public_dns_name)
    return instance.public_dns_name


def reboot_instance(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, REGION, EndPoint):
    # reboot an EC2 instance using boto
    logging.info("Reboot an EC2 instance by public dns [%s] using boto ..." %
                 EndPoint)
    ec2_conn = boto.ec2.connect_to_region(REGION, aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    rs = ec2_conn.get_all_instances()
    instances = [instance for r in rs for instance in r.instances if instance.public_dns_name == EndPoint]
    if not instances:
        logging.info('Reboot an EC2 instance by public dns [%s] using boto failed\nEndPoint does NOT exist.' % EndPoint)
        return 1
    else:
        instances[0].reboot()
        _wait_until_instance_running(instances[0])
        ## wait until STAF service is ready
        LONGTIMES = 20
        testingServer.wait_STAF_service(
            instances[0].public_dns_name, LONGTIMES)
        # return the public DNS of the launched EC2 instance
        logging.info("Reboot an EC2 instance by public dns [%s] using boto success" % instances[0].public_dns_name)
        return 0


def _get_instance_id(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, REGION, EndPoint):
    # get instance id with the public_dns_name
    logging.info(
        "Get instance id by public dns [%s] using boto ..." % EndPoint)
    # this function will not work because public_dns will change after starting a stopped instance
    ec2_conn = boto.ec2.connect_to_region(REGION, aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
    rs = ec2_conn.get_all_instances()
    instances = [instance for r in rs for instance in r.instances if instance.public_dns_name == EndPoint]
    if not instances:
        logging.info("Get instance id by public dns [%s] using boto failed\nEndPoint does NOT exist." % EndPoint)
        raise RuntimeError("Get instance id by public dns [%s] using boto failed. EndPoint does NOT exist." % EndPoint)
    instance_id = instances[0]
    logging.info("Get instance id by public dns [%s] using boto success\nReturn instance id [%s]" % (EndPoint, instance_id.id))
    return instance_id.id


def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i + n]


def cases_execute_ruby(AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, REGION, EndPoint, HTTP_SERVER, REMOTE_TESTING_DIR, REMOTE_RUBY_CONFIG, LOCAL_RUBY_CONFIG, LOCAL_RUBY_CASES, LOCAL_RUBY_CASES_PER_RUN, remote_filepath_log, local_filepath_log, tmp_filename, retry=3, DoReboot=""):
    caseList = LOCAL_RUBY_CASES.split(",")
    used_ruby_config = "%s_%s_used" % (LOCAL_RUBY_CONFIG, EndPoint)
    logging.info("The used configure for ruby is [%s]" % used_ruby_config)
    for i in range(int(retry)):
        import shutil
        import stat
        shutil.copy(LOCAL_RUBY_CONFIG, used_ruby_config)
        os.chmod(used_ruby_config, stat.S_IWRITE)
        cutedCaseList = chunks(caseList, int(LOCAL_RUBY_CASES_PER_RUN))
        for cutedCases in cutedCaseList:
            logging.info("Execute_ruby with run-cases [%s]" %
                         ",".join(cutedCases))
            testingServer.replace_config(used_ruby_config,
                                         "suite", "run-cases", ",".join(cutedCases))
            staf.call_local("staf", ["local", "fs", "copy", "FILE", used_ruby_config, "TOFILE", REMOTE_TESTING_DIR + REMOTE_RUBY_CONFIG, "TOMACHINE", EndPoint])
            try:
                testingServer.execute_ruby(EndPoint, REMOTE_TESTING_DIR)
            except RuntimeError:
                import sys
                import traceback
                exc_type, exc_value, exc_traceback = sys.exc_info()
                logging.error(repr(traceback.format_exception(
                    exc_type, exc_value, exc_traceback)))
                continue
            testingServer.copy_to_local(EndPoint, remote_filepath_log,
                                        local_filepath_log, HTTP_SERVER, tmp_filename)
            if DoReboot == "REBOOT":
                reboot_instance(AWS_ACCESS_KEY_ID,
                                AWS_SECRET_ACCESS_KEY, REGION, EndPoint)
        runed_cases = testingServer.parse_ruby_result_case(local_filepath_log)
        logging.debug("runed_cases [%s]" % ",".join(runed_cases))
        caseList = [cases for cases in caseList if cases.split(
            ".")[0] not in runed_cases]
        logging.info("rerun case [%s]" % ",".join(caseList))

if __name__ == '__main__':
    pass
