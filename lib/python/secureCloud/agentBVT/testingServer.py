import sys
import os
import time
from urllib2 import urlopen, HTTPError, URLError
import logging
import platform
import ConfigParser
import re
import threading
import urllib
import subprocess
import shutil




class MyMutex:
    config_lock = threading.Lock()
    result_lock = threading.Lock()
    downloaded_url = set()

# called
def get_latest_build_info(SERVER_URL, BUILD_TAG):
    tp = urlopen(SERVER_URL + "daily_build_monitor.ini")
    config = ConfigParser.ConfigParser()
    config.readfp(tp)


    try:
        build_name = config.get("BuildVersion", BUILD_TAG)
        build_ver = re.search(r"(\d{4})", build_name)
        build_ver = build_ver.group(1)
        build_dict = {"name": build_name, "version": build_ver,
                      "tag": BUILD_TAG}
        logging.info(build_dict)
        return build_dict

    except Exception, e:
        logging.error(e)

    return


def update_build_version(FILEPATH_LastBuildVersion, SCTM_EXEC_ID, build_version):
    config = ConfigParser.ConfigParser()
    try:
        config.readfp(open(FILEPATH_LastBuildVersion))
        if config.has_option("LastBuildVersion", SCTM_EXEC_ID):
            last_version = config.get("LastBuildVersion", SCTM_EXEC_ID)

        else:
            last_version = 1000
            config.set("LastBuildVersion", SCTM_EXEC_ID, last_version)

        if int(build_version) > int(last_version):
            config.set("LastBuildVersion", SCTM_EXEC_ID, build_version)
            logging.info("update build version: " +
                         SCTM_EXEC_ID + "=" + build_version)
        else:
            logging.info("build version < last version, no update")

        MyMutex.config_lock.acquire()
        config.write(open(FILEPATH_LastBuildVersion, 'wb'))
        MyMutex.config_lock.release()
    except Exception, e:
        logging.error(e)

    return

# called
def clean_result(FILEPATH_RESULT, SCTM_EXEC_ID):
    logging.info(
        "clean up reseult for " + FILEPATH_RESULT + ":" + SCTM_EXEC_ID)
    buffer_write = ""
    MyMutex.result_lock.acquire()
    if os.path.exists(FILEPATH_RESULT):
        fp = open(FILEPATH_RESULT, "w+")
        lines = fp.readlines()
        for line in lines:
            if string.find(line, SCTM_EXEC_ID) == -1:
                buffer_write += line
        fp.write(buffer_write)
        fp.close()
    MyMutex.result_lock.release()

#called
def copy_to_local(EndPoint, REMOTE_FILEPATH, LOCAL_FILEPATH, HTTP_SERVER, TMP_FILENAME):
    # staf <Machine> fs copy FILE <Name> TOFILE <Name> TOMACHINE <Machine>
    try:
        tmp_filepath = "/var/www/html/" + TMP_FILENAME
        cmd = "staf " + EndPoint + " fs copy FILE " + REMOTE_FILEPATH + \
            " TOFILE " + tmp_filepath + " TOMACHINE " + HTTP_SERVER
        logging.debug("copy command:" + cmd)
        result = subprocess.check_call(cmd)
        logging.info("copy result: %s" % str(result))

        # wget http://HTTP_SERVER/EndPoint.tmp
        url = "http://" + HTTP_SERVER + "/" + TMP_FILENAME
        logging.debug("download URL:" + url)
        urllib.urlretrieve(url, os.path.abspath(LOCAL_FILEPATH))
        logging.info("download log" + url + " to LOCAL_MACHINE")

    except Exception, e:
        logging.debug(e)
        return e.returncode

    return 0

# called
def parse_tmstaf_result(tmstaf_result_path, exec_result_for_sctm, sctm_exec_id):

    dir_list = sorted(os.listdir(tmstaf_result_path))
    logging.info("collect_latest_tmstaf_log() [%s]" % dir_list)

    latest_dir = ""
    while True:
        latest_dir = dir_list.pop()
        result_folder = os.path.join(tmstaf_result_path, latest_dir)
        if os.path.isdir(result_folder):
            break

    print "result folder:" + latest_dir
    result_tmstaf_log = "c:\\TMP\\"+latest_dir+"_tmstaf.log"
    shutil.copyfile(os.path.join(result_folder, "tmstaf.log"), result_tmstaf_log )


    logging.info("Fill in reseult of " + sctm_exec_id + " ...")
    MyMutex.result_lock.acquire()
    f = open(result_tmstaf_log, "r")
    lines = f.readlines()
    f.close()
    file_append = open(exec_result_for_sctm, "a")
    all_case_pass = True
    for line in lines:
        # fix windows "testrunner._runTestCase" can't be matched
        line = line.strip()
        #m = re.search(r"\[testRunner\._runTestCase\] run (\S+)\.(\S+) (\w+)", line, flags=re.IGNORECASE)
        m = re.search( r"\[testrunner\._runTestCase\]\srun (\S+)\.(\S+) (\w+)", line, flags=re.IGNORECASE )
        if m:
            logging.debug("TC result match: " + line)
            logging.debug("%s, %s, %s" % (m.group(1),m.group(2),m.group(3)))
            case_id = m.group(2).split("_")[0]
            case_result = "-"
            if m.group(3) == "Pass":
                case_result = "P"
            elif m.group(3) == "Fail":
                case_result = "F"
                all_case_pass = False
            # case_id, SCTM_EXEC_ID: case_result
            file_append.write(case_id + ", " + sctm_exec_id +
                              ": " + case_result + "\n")
        else:
            #logging.debug("TC result not match: " + line)
            pass
    file_append.close()
    MyMutex.result_lock.release()
    return all_case_pass


def wait(remote_ip):
    import secureCloud.agentBVT.staf
    staf.util.waitStafReady(remote_ip)


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')
    #get("http://211.76.133.181/sc/20/SecureCloudAgentSilentSetup_Release_Win32_en_2.0.0_1106.ex", "latest_build.exe")
    #get("http://211.76.133.181/sc/20/SecureCloudAgentSilentSetup_Release_Win32_en_2.0.0_1106.exe", "latest_build.exe")
    #get("http://dl.dropbox.com/u/60937902/20/SecureCloudAgentSilentSetup_Release_Win32_en_2.0.0_1106.exe", "latest_build.exe")
    """
    SERVER_URL = "http://172.18.0.10/sc/30/"
    BUILD_TAG = "AGENT_RHEL6x64_BIN"
    FILEPATH_LastBuildVersion = r'C:\STAF\data\agentBVT\agentInstall\last-build-version.ini'
    info = get_latest_build_info(SERVER_URL, BUILD_TAG)
    print info["version"]
    update_build_version(FILEPATH_LastBuildVersion, "ccentosx64-5.6", "999")

    FILEPATH_LOG = r"C:\tmp\172.18.0.227_agentBVT-Ubuntu10.04-x86-esx_tmstaf.log"
    FILEPATH_RESULT = r"C:\STAF\data\agentBVT\agentInstallESX\auto-result.txt"
    SCTM_EXEC_ID = "agentBVT-Ubuntu10.04-x86-esx"
    parse_tmstaf_result(FILEPATH_LOG, FILEPATH_RESULT, SCTM_EXEC_ID)

    file1 = r"C:\tmp\REDHATx86-5.5-ebs_tmstaf.log"
    parse_tmstaf_result(file1, r"C:\STAF\data\agentBVT\agentInstall\auto-result.txt", "REDHATx86-5.5-ebs")
    """

    # python C:\STAF\lib\python\secureCloud\agentBVT\testingServer.py parse_tmstaf_result C:\STAF\testsuites\agentBVT_35\result C:\STAF\data\agentBVT\agentInstall\auto-result.txt test_exec

    command = sys.argv[1]
    if command == "parse_tmstaf_result":
        tmstaf_result_path = sys.argv[2]
        exec_result_for_sctm = sys.argv[3]
        sctm_exec_id = sys.argv[4]

        result = parse_tmstaf_result(tmstaf_result_path, exec_result_for_sctm, sctm_exec_id)
        print "parse_tmstaf_result:" + str(result)



