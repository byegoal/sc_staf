'''
Created on 2012/4/12

@author: eason_lin
'''
import ConfigParser
import string
import urllib
import logging
import re
import os
import time
from sets import Set
import threading
import staf


class MyMutex:
    config_lock = threading.Lock()
    result_lock = threading.Lock()
    downloaded_url = Set()


def get_BuildVersion(FILEPATH_LastBuildVersion, ENVIRONMENT, LOCAL_DOWNLOAD_DIR, AGENT, CheckBuildVersion="False", BUILD_SERVER_URL="http://172.18.0.10/sc/20/"):
    '''
    @return:
        2 means that there does not exist an agent build newer than the last agent build
    '''
    LastBuildVersionString = os.getenv("#SCTM_BUILD", "")
    if not LastBuildVersionString:
        strLastBuildVersion = get_config(FILEPATH_LastBuildVersion,
                                         "LastBuildVersion", ENVIRONMENT)
        if not strLastBuildVersion:
            strLastBuildVersion = "1000"
        LastBuildVersion = int(strLastBuildVersion)
    else:
        m = re.search(r"(\d{4})", LastBuildVersionString)
        LastBuildVersion = int(m.group(1)) - 1

    logging.debug("LastBuildVersion: [%i]" % LastBuildVersion)
    # If there does not exist an agent build newer than the last agent build
    # Wait 1 minute each time; 20 times at most.
    for iteration in range(20):
        BuildFile = get_config(LOCAL_DOWNLOAD_DIR + "daily_build_monitor.txt", "BuildVersion", AGENT, BUILD_SERVER_URL + "daily_build_monitor.txt")
        if BuildFile:
            m = re.search(r"(\d{4})", BuildFile)
            NowBuildVersion = int(m.group(1))
            logging.debug("NowBuildFile: [%i]" % NowBuildVersion)
            if (CheckBuildVersion == "False") or (int(LastBuildVersion) < int(NowBuildVersion)):
                replace_config(FILEPATH_LastBuildVersion, "LastBuildVersion",
                               ENVIRONMENT, str(NowBuildVersion))
                return BuildFile
        logging.info("Download Build Waiting... Times [%i]" % iteration)
        time.sleep(60.0)
    raise RuntimeError('Timeout! Get Build File failed. The build of %s not exist.' % ENVIRONMENT)


def get_config(FILEPATH_CONFIG, SECTION, OPTION, URL=None):
    if URL is not None:
        # download URL
        logging.debug("Downloading config from: " + URL)
        MyMutex.config_lock.acquire()
        if URL not in MyMutex.downloaded_url:
            urllib.urlretrieve(URL, FILEPATH_CONFIG)
            MyMutex.downloaded_url.add(URL)
        MyMutex.config_lock.release()
    # specify SECTION from FILEPATH_CONFIG
    logging.debug("get section: %s value: %s from %s ..." % (SECTION,
                                                             OPTION, FILEPATH_CONFIG))
    config = ConfigParser.ConfigParser()
    MyMutex.config_lock.acquire()
    config.read(FILEPATH_CONFIG)
    VALUE = ""
    try:
        VALUE = config.get(SECTION, OPTION)
    except ConfigParser.NoOptionError:
        # Create non-existent section
        VALUE = ""
    finally:
        MyMutex.config_lock.release()
        # SECTION: VALUE
        logging.debug("[%s.%s]" % (SECTION, VALUE))
        return VALUE


def replace_config(FILEPATH_CONFIG, SECTION, OPTION, VALUE):
    '''
    @FILEPATH_CONFIG:
        [SECTION1]
        OPTION1=VALUE1
        OPTION2=VALUE2
        [SECTION2]
        OPTION1=VALUE3
        OPTION2=VALUE4
        OPTION3=VALUE5
    '''
    # set OPTION=VALUE in SECTION of FILEPATH_CONFIG
    logging.debug("Set %s=%s in %s of %s" % (OPTION, VALUE, SECTION,
                                             FILEPATH_CONFIG))
    config = ConfigParser.ConfigParser()
    MyMutex.config_lock.acquire()
    config.read(FILEPATH_CONFIG)
    try:
        config.set(SECTION, OPTION, VALUE)
    except ConfigParser.NoSectionError:
        # Create non-existent section
        config.add_section(SECTION)
        config.set(SECTION, OPTION, VALUE)
    with open(FILEPATH_CONFIG, "w") as configfile:
        config.write(configfile)
    MyMutex.config_lock.release()


def wait_STAF_service(EndPoint, intTimes):
    return staf.wait_ready(EndPoint, intTimes)


def copy_to_local(EndPoint, REMOTE_FILEPATH, LOCAL_FILEPATH, HTTP_SERVER, TMP_FILENAME):
    # staf <Machine> fs copy FILE <Name> TOFILE <Name> TOMACHINE <Machine>
    try:
        tmp_filepath = "/var/www/html/" + TMP_FILENAME
        cmd = "staf " + EndPoint + " fs copy FILE " + REMOTE_FILEPATH + \
            " TOFILE " + tmp_filepath + " TOMACHINE " + HTTP_SERVER
        subprocess.check_call(cmd)
        logging.info("copy result: %s" % cmd)

        # wget http://HTTP_SERVER/EndPoint.tmp
        url = "http://" + HTTP_SERVER + "/" + TMP_FILENAME
        urllib.urlretrieve(url, os.path.abspath(LOCAL_FILEPATH))
        logging.info("download log" + url + " to LOCAL_MACHINE")
    except Exception, e:
        return e

    return 0

import fnmatch


def search_file(search_filename, search_path):
        for root, dirnames, filenames in os.walk(search_path):
                for filename in fnmatch.filter(filenames, search_filename):
                        return os.path.join(root, filename)
        return None


def get_tmstaf_log(EndPoint, REMOTE_FILEPATH, LOCAL_FILEPATH, HTTP_SERVER, TMP_FILENAME):
    copy_to_local(EndPoint, REMOTE_FILEPATH, LOCAL_FILEPATH,
                  HTTP_SERVER, TMP_FILENAME)


def clean_result(FILEPATH_RESULT, PlatformID):
    logging.info("Clean the reseult of " + PlatformID + " ...")
    buffer_write = ""
    MyMutex.result_lock.acquire()
    try:
        file_read = open(FILEPATH_RESULT, "r")
        lines = file_read.readlines()
        for line in lines:
            if string.find(line, PlatformID) == -1:
                buffer_write += line
        file_read.close()

    except IOError as e:
        def is_no_such_file_error(errno):
            return errno == 2
        if not is_no_such_file_error(e.errno):
            raise e

    file_write = open(FILEPATH_RESULT, "w")
    file_write.write(buffer_write)
    file_write.close()
    MyMutex.result_lock.release()


def execute_ruby(EndPoint, REMOTE_TESTING_DIR):
    remote_filepath_rb = REMOTE_TESTING_DIR + "runCase.rb"
    intExitCode = staf.call_remote_async(EndPoint, "ruby", ["-C", REMOTE_TESTING_DIR, remote_filepath_rb, EndPoint, "no_smoke"], {'LD_LIBRARY_PATH': "/usr/local/staf/lib"}, None, 7200)
    return intExitCode


def call_remote(strDestIp, strExecutable, lstArgs, dicEnv={}, workdir=None):
    intExitCode, strStdout = staf.call_remote(
        strDestIp, strExecutable, lstArgs, dicEnv, workdir)
    return intExitCode


def call_remote_async(strDestIp, strExecutable, lstArgs, dicEnv={}, workdir=None):
    intExitCode, strStdout = staf.call_remote_async(
        strDestIp, strExecutable, lstArgs, dicEnv, workdir)
    return intExitCode


def parse_ruby_result_case(local_filepath_log):
    f = open(local_filepath_log, "r")
    lines = f.readlines()
    caseList = []
    for line in lines:
        m = re.search(r"\[(\w+)\]case=(\w+),", line)
        if m is not None:
            caseList.append(m.group(2))
    logging.debug("Case List is %s" % ",".join(caseList))
    f.close()
    return caseList


def parse_ruby_result(FILEPATH_CONFIG, FILEPATH_LOG, FILEPATH_RESULT, PlatformID):
    logging.info("Fill in the reseult of " + PlatformID + " ...")
    MyMutex.result_lock.acquire()
    file_append = open(FILEPATH_RESULT, "a")
    f = open(FILEPATH_LOG, "r")
    lines = f.readlines()
    for line in lines:
        m = re.search(r"\[(\w+)\]case=(\w+),", line)
        if m is not None:
            TestCaseID = get_config(FILEPATH_CONFIG, "TestCaseID", m.group(2))
            TestResult = "-"
            if m.group(1) == "Success":
                TestResult = "P"
            elif m.group(1) == "Fail":
                TestResult = "F"
            # TestCaseID,PlatformID: TestResult
            file_append.write(TestCaseID + "," + PlatformID +
                              ": " + TestResult + "\n")
    f.close()
    file_append.close()
    MyMutex.result_lock.release()


def parse_tmstaf_result(FILEPATH_CONFIG, FILEPATH_LOG, FILEPATH_RESULT, PlatformID):
    logging.info("Fill in the reseult of " + PlatformID + " ...")
    MyMutex.result_lock.acquire()
    file_append = open(FILEPATH_RESULT, "a")
    f = open(FILEPATH_LOG, "r")
    lines = f.readlines()
    Allcasepass = True
    for line in lines:
        m = re.search(r"\[testRunner\._runTestCase\]\srun (\S+)\.(\S+) (\w+)",
                      line)
        if m is not None:
            TestCaseID = get_config(FILEPATH_CONFIG, "TestCaseID", m.group(2))
            TestResult = "-"
            if m.group(3) == "Pass":
                TestResult = "P"
            elif m.group(3) == "Fail":
                TestResult = "F"
                Allcasepass = False
            # TestCaseID,PlatformID: TestResult
            file_append.write(TestCaseID + "," + PlatformID +
                              ": " + TestResult + "\n")
    f.close()
    file_append.close()
    MyMutex.result_lock.release()
    return Allcasepass


def parse_result(FILEPATH_CONFIG, FILEPATH_LOG, FILEPATH_RESULT, PlatformID):
    # clean result by PlatformID
    clean_result(FILEPATH_RESULT, PlatformID)
    # fill in result by Platform ID
    parse_ruby_result(
        FILEPATH_CONFIG, FILEPATH_LOG, FILEPATH_RESULT, PlatformID)

if __name__ == '__main__':
    pass
