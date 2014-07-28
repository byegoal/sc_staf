import logging
import optparse
import os
import sys
import time
import re
import cPickle
import shutil
from optparse import OptionParser, OptionGroup
from cookielib import logger

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
import secureCloud.scAgent.file
import secureCloud.scAgent.Agent
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
        if not os.path.exists(("%s/result/" % MODULE_PATH)):
            os.makedirs(("%s/result/" % MODULE_PATH))
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
        
    def setLogFile(self,strLog,strLogLevel,logPath):
        if not os.path.exists(logPath):
            os.makedirs(logPath)
        logFile = logging.getLogger(strLog)
        hdlr = logging.FileHandler(strLog)
        formatter = logging.Formatter('%(message)s %(asctime)s %(levelname)s %(thread)s [%(module)s.%(funcName)s]')
        hdlr.setFormatter(formatter)
        logFile.addHandler(hdlr) 
        logFile.setLevel(strLogLevel)
        return logFile
        
def main(options):
    retval = 0
    stafLogger.debug("Start to do scagent stop checking") 
    if options.userScript_file==False:
        errorLogger.error("userScript file is required")
        retval = 1
        return retval
        # Load global specific settings
    GLOBAL_SETTING_PATH = ("%s/product.ini" % MODULE_PATH)
    ENV_SETTING_PATH = ("%s/env.ini" % MODULE_PATH)
    log_path = result_path = ("%s/result/" % MODULE_PATH)
    GLOBAL_SETTING = secureCloud.agentBVT.util.config(GLOBAL_SETTING_PATH)
    sc_path = secureCloud.scAgent.Agent.get_sc_root()
    
    service_result = secureCloud.agentBVT.testingClient.is_sc_stop()
    is_file=secureCloud.agentBVT.testingClient.is_file_exist(options.userScript_file)
    if is_file ==1:
        userScript_result = 0
    else:
        userScript_result = 1
    
    if service_result==0 and userScript_result==0:
            secureCloud.agentBVT.testingClient.write_report(log_path,'pass: scagent is stopped, teardown userScript works.')
            stafLogger.critical('pass: scagent is stopped, teardown userScript works.')
            retval=0
    else:
         if not service_result==0:
            secureCloud.agentBVT.testingClient.write_report(log_path,'FAIL: scagent is NOT stopped') 
            stafLogger.critical('FAIL: scagent is NOT stopped')
            errorLogger.error('FAIL: scagent is NOT stopped')
         if not userScript_result==0:
            secureCloud.agentBVT.testingClient.write_report(log_path,'FAIL: %s is not removed. tear down userScript not works.'%options.userScript_file) 
            stafLogger.critical('FAIL: %s is not removed. tear down userScript not works.'%options.userScript_file)
            errorLogger.error('FAIL: %s is not removed. tear down userScript not works.'%options.userScript_file)
            retval=1
    
    stafLogger.debug("End of scagent stop checking")           
    return retval
        

def _handle_options(argv):
    usage_win = 'activate.py [action [parameters]]'
    usage_linux = 'python activate.py [action [parameters]]'
    if os.name == "nt":
        usage = usage_win
    else:
        usage = usage_linux

    parser = OptionParser(usage=usage)

    action_group = OptionGroup(parser, "Actions", "")
    action_group.add_option('-f', '--userScript-file', type='string', dest='userScript_file',
                    default=False,metavar= 'userScript_file',
                    help='teardown userScript file path. ex: -f "/dev/xvdi/file1')
    parser.add_option_group(action_group)
    (options, args) = parser.parse_args(argv)  
    return options 


if __name__ == "__main__":  
    __retval__ = 0
    log_path = ("%s/result/" % MODULE_PATH)
    STAF_LOG_FILENAME = ("%sstaf.log"% log_path)
    chefLogger = secureCloud.scAgent.file.setLogFile(os.path.join((log_path),("chef.log")), logging.INFO , 'chefLogger')
    stafLogger = secureCloud.scAgent.file.setLogFile(os.path.join((log_path),("staf.log")), logging.DEBUG, 'stafLogger')
    errorLogger = secureCloud.scAgent.file.setLogFile(os.path.join((log_path),("error.log")), logging.ERROR, 'errorLogger')
    stafLogger.critical('*** START SCRIPT ***\n') 
    if __retval__ == 0:
        __options__ = _handle_options(sys.argv[1:])
        __retval__ = main(__options__)
    stafLogger.critical('*** EXIT WITH (%s) ***\n' %str(__retval__))
    sys.exit(__retval__)