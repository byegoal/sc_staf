import logging
import optparse
import os
import sys
import time
import re
import cPickle
import shutil
from cookielib import logger
from optparse import OptionParser, OptionGroup

MODULE_PATH = os.path.dirname(__file__) or os.getcwd()
TMSTAF_PID_FILE = os.path.join(MODULE_PATH, 'tmstaf.pid')


def addTmstafLibPath():
    sys.path.insert(0, os.path.dirname(MODULE_PATH))


def addStafLibPath():
    #Todo: we should not hardcode this path! 2009-10-14 camge
    if os.name == 'nt':
        sys.path.insert(0, r'C:\staf\bin')
    else:
        sys.path.insert(0, r'/usr/local/STAF/bin')

addStafLibPath()
addTmstafLibPath()


import tmstaf.processUtil
import secureCloud.agentBVT.testingClient
import secureCloud.agentBVT.util
import secureCloud.scAgent.scAgent
from tmstaf.testwareConfig import TestwareConfig
from tmstaf.productSetting import ProductSetting
from tmstaf.testRunner import BaseTestRunner
from tmstaf.util import getException
import threading
VERSION = 'v2.1.0'


class TmstafMain:
    strVersion = VERSION
    strResumeDataFileName = 'resume.dat'
    strResumeDataFile = os.path.join(os.getcwd(), strResumeDataFileName)
    _dicLevel = {'critical': logging.CRITICAL,
                 'error': logging.ERROR,
                 'warning': logging.WARNING,
                 'info': logging.INFO,
                 'debug': logging.DEBUG}

    def __init__(self, intLogLevel=None):
        # set root logger's level to DEBUG
        self.resumed = False
        if intLogLevel:
            logging.getLogger().setLevel(intLogLevel)
        self.strCmdLine = ' '.join(sys.argv)
    
    def initLogFile(self, strLogFile, intLevel, mode='wb'):
        logFile = logging.FileHandler(strLogFile, mode)
        logFile.setLevel(logging.INFO)
        strFormat = '%(asctime)s %(levelname)s %(thread)s [%(module)s.%(funcName)s] %(message)s'
        logFile.setFormatter(logging.Formatter(strFormat))

        class ThreadFilter(logging.Filter):
            def filter(self, record):
                return record.thread == threading.currentThread().ident
        logFile.addFilter(ThreadFilter())
        # All messages which come from "tmstaf" logger will be written into tmstaf.log
        self.getLogger().addHandler(logFile)

    def getLogger(self):
        return logging.getLogger()
        #return logging.getLogger('tmstaf')

    def initConsoleLog(self,strLog, intLevel,logPath):
        if logging.getLogger().handlers:
            logging.getLogger().setLevel(intLevel)
            return
        console = logging.StreamHandler(sys.stdout)
        console.setLevel(intLevel)
        console.setFormatter(logging.Formatter('%(asctime)s.%(msecs)d %(levelname)s %(thread)s [%(module)s.%(funcName)s] %(message)s', '%H:%M:%S'))
        logging.getLogger(strLog).addHandler(console)
        return console
        
    def setLogFile(self,strLog,strLogLevel,logPath):
        if not os.path.exists(logPath):
            os.makedirs(logPath)
        logFile = logging.getLogger(strLog)
        hdlr = logging.FileHandler(strLog)
        formatter = logging.Formatter('%(message)s %(asctime)s %(levelname)s %(thread)s [%(module)s]')
        hdlr.setFormatter(formatter)
        logFile.addHandler(hdlr) 
        logFile.setLevel(strLogLevel)
        return logFile
        

def main():
    retval = 0
    
        # Load global specific settings
    GLOBAL_SETTING_PATH = ("%s/product.ini" % MODULE_PATH)
    ENV_SETTING_PATH = ("%s/env.ini" % MODULE_PATH)

    GLOBAL_SETTING = secureCloud.agentBVT.util.config(GLOBAL_SETTING_PATH)
    ENV_SETTING = secureCloud.agentBVT.util.config(ENV_SETTING_PATH)
    agent_vmGuid = secureCloud.agentBVT.testingClient.get_agent_vmGuid(GLOBAL_SETTING[ENV_SETTING['ENV']['os']]['sc_agent_path_64'])
    result_log_name= ("%s-chef.log" % agent_vmGuid)
    result_path = ("%s/result/" % MODULE_PATH)
    strLogLevel=logging.DEBUG
    
    TmstafMain().initConsoleLog(os.path.join((result_path),("tmstaf.log")), strLogLevel, 'ab')
    TmstafMain().initLogFile(os.path.join((result_path),("chef.log")), strLogLevel, 'ab')
    TmstafMain().setLogFile(os.path.join((result_path),("result.log")), strLogLevel, 'ab')    

    sc_path = GLOBAL_SETTING[ENV_SETTING['ENV']['os']]['sc_agent_path_64']

    sc_root = secureCloud.scAgent.scAgent.get_sc_root()
    print(sc_root)
    if retval==0:
        secureCloud.agentBVT.testingClient.write_report(result_path,('pass: %s'))
        print('pass: %s' )
        return retval
    else:
        secureCloud.agentBVT.testingClient.write_report(result_path,('FAIL: %s'))
        print('FAIL: %s' )
        return retval
    #generate xml report
    #secureCloud.agentBVT.testingClient.generateXmlReport(result_path,("%s-report.xml" % agent_vmGuid),'check_device_encrypted_by_vmGuid',result)



def _handle_options(argv):
    usage_win = 'activate.py [action [parameters]]'
    usage_linux = 'python activate.py [action [parameters]]'
    if os.name == "nt":
        usage = usage_win
    else:
        usage = usage_linux

    parser = OptionParser(usage=usage)

    action_group = OptionGroup(parser, "Actions", "")
    action_group.add_option('-k', '--keyword', type='string', dest='keyword',
                    default=False,metavar= 'keyword',
                    help='keyword to find. ex: -k "DEBUG scagent..."')
    action_group.add_option('-f', '--file-path', type='string', dest='file_path',
                    default=False, metavar= 'file_path',
                    help='log file path. ex: -f "/var/lib/secureCloud/agnet.log"')
    action_group.add_option('-n', '--case-name', type='string', dest='case_name',
                    default=False, metavar= 'file_path',
                    help='test case name. ex: check_add_hosts_file')
    parser.add_option_group(action_group)

    (options, args) = parser.parse_args(argv)
    
    return options 

    


if __name__ == "__main__":
    chef_log = ("%s/result/" % MODULE_PATH)
    logger = logging.basicConfig(filename='chef.log',
                                 level=logging.DEBUG,
                                 format='%(asctime)s %(levelname)s : %(message)s -- @(%(lineno)d)'
                                 )
    logging.critical('*** START SCRIPT ***\n')
    __retval__ = 0

    if __retval__ == 0:
        __retval__ = main()

    logging.critical('*** EXIT WITH (%s) ***\n' %str(__retval__))
    sys.exit(__retval__)