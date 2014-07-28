import os
import re
import time
from urllib2 import urlopen, HTTPError, URLError
import logging
import platform
import ConfigParser
import shutil
import subprocess
#import staf

def get(url, download_file, retry_count=10):
    try:
        print "downloading %s to %s" % (url, download_file)
        req = urlopen(url)
        remote_filesize = req.info().get("Content-Length")
        logging.debug("remote file size: %s" % remote_filesize)
        try:
            local_filesize = os.path.getsize(download_file)
            logging.debug("local file size: %s" % local_filesize)
            if local_filesize == local_filesize:
                logging.info("local file size equal remote file size, skip download")
                return 0
        except Exception, e:
            # if get local file size fail, keep continuing actions..
            pass

        CHUNK = 16 * 1024
        if platform.system() == "Windows":
            download_dir = r"c:\tmp"
        else:
            download_dir = r"/tmp"

        if not os.path.exists(download_dir):
            os.makedirs(download_dir)
            print "tmp folder created"

        fp = open(download_file, 'wb')
        while True:
            chunk = req.read(CHUNK)
            if not chunk:
                break
            fp.write(chunk)
        fp.close()
        return 0

    except HTTPError, e:
        logging.error("download build fail HTTPError: " + str(
            e.code) + " " + url)
        return -1

    except URLError, e:
        print "URLError: ", e.reason, url
        logging.error("download build fail URLError: " + str(
            e.reason) + " " + url)
        logging.error("URLError: " + e.reason + " " + url)
        return -1


def ini_update(config_path, section, option, value):
    try:
        config = ConfigParser.ConfigParser()
        #confog.optionxform = str
        config.read(config_path)
        config.set(section, option, value)
        config.write(open(config_path, 'w+'))

    except Exception, e:
        logging.error(e)


def check_sc_install_dir():
    os_type = platform.system()  # Linux or Windows
    sc_install_dir = get_agent_install_path()

    if os_type == "Windows":
        logging.debug("check sc install path: %s" % sc_install_dir)
        ret = os.path.exists(sc_install_dir)
    else:
        ret = os.path.exists(sc_install_dir)

    return ret


def check_sc_service():
    os_type = platform.system()
    if os_type == "Windows":
        ret = subprocess.call("sc query c9agentsvc", shell=True)
        if ret == 0:
            return True
        else:
            return ret
    else:
        ret = os.path.exists(r'/etc/init.d/scagentd')
    return ret


def collect_latest_tmstaf_log():
    os_type = platform.system()
    if os_type == "Windows":
        base_dir = r"c:\STAF\testsuites\agentBVT\result"
        result_path = r"c:\tmp\tmstaf.log"

    else:
        base_dir = r"/usr/local/staf/testsuites/agentBVT/result"
        result_path = r"/tmp/tmstaf.log"

    dir_list = sorted(os.listdir(base_dir))
    logging.info("collect_latest_tmstaf_log() [%s]" % dir_list)

    while True:
        latest_dir = dir_list.pop()
        result_folder = os.path.join(base_dir, latest_dir)
        if os.path.isdir(result_folder):
            break

    shutil.copyfile(os.path.join(result_folder, "tmstaf.log"), result_path)


def agent_silent_provision(account_id, kms_url, passphrase, access_id=None, secret_key=None):
    os_type = platform.system()  # Linux or Windows
    if os_type == "Linux":
        scconfig_exec = os.path.join(get_agent_install_path(), "scconfig.sh")
    else: # os_type = "Windows"
        scconfig_exec = os.path.join(get_agent_install_path(), "scconfig.exe")

    # EC2 or ESX
    if access_id and secret_key:  # this is an ec2 instance
        command = "%s --register --csp-id=Amazon-AWS --options=%s,%s --guid='%s' --url='%s' --passphrase='%s' \
--publish-inventory --timeout=10 --get-device-list -q" % (scconfig_exec, access_id, secret_key, account_id, kms_url, passphrase)
    else:  # this is ec2 instance, native plugin
        command = "%s --register --csp-id=Native --guid='%s' --url='%s' --passphrase='%s' \
--publish-inventory --timeout=10 --get-device-list -q" % (scconfig_exec, account_id, kms_url, passphrase)
    logging.info(command)
    p = subprocess.call(command, shell=True)
    return p


def get_agent_install_path():
    os_type = platform.system()  # Linux or Windows
    if os_type == "Windows":
        if re.search("(.64)", platform.machine()):
            programfiles_dir = os.environ["ProgramFiles(x86)"]
        else:
            programfiles_dir = os.environ["ProgramFiles"]
        return os.path.join(programfiles_dir, "Trend Micro\\SecureCloud\\Agent")
    else:
        return "/var/lib/securecloud"


def get_cspharness_type():
    os_type = platform.system()  # Linux or Windows
    if os_type == "Windows":
        cspharness_type = "cspharness.exe"
    else:
        cspharness_type = "cspharness.sh"
    return cspharness_type


def create_cspharness_conf(csp_name="", cred_list="", map_device_list=""):
    if csp_name == "Amazon":
        plugin_path = "amazonaws.zip"
    elif csp_name == "Native":
        plugin_path = "native.zip"

    xml_str = """<config>
    <PLUGIN_PATH>%s</PLUGIN_PATH>
    <CRED_LIST>%s</CRED_LIST>
    <MAP_DEVICE_LIST>%s</MAP_DEVICE_LIST>\n</config>""" % (plugin_path, cred_list, map_device_list)

    save_path = os.path.join(get_agent_install_path(), "csp_harness.conf")

    f = open(save_path, "w")
    f.write(xml_str)
    f.close()

#def scconfig_linux(EndPoint, TC_SCCONFIG, lstArgs):
#    intExitCode, strStdout = staf.call_remote(EndPoint, "killall", ["scconfig.sh"])
#    intExitCode, strStdout = staf.call_remote(EndPoint, "killall", ["sc_config"])
#    intExitCode, strStdout = staf.call_remote(EndPoint, TC_SCCONFIG, lstArgs, {'LD_LIBRARY_PATH':""})
#    return intExitCode

#if __name__ == '__main__':
    #fp = "C:\\STAF\\data\\agentBVT\\agentInstall\\logger_linux_kh_test.ini"
    #ini_update(fp, "kh_test", "level", "1299993456")
