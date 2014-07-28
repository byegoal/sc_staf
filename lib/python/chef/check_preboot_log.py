import logging
import optparse
import os
import sys
import time
import re
import cPickle
import shutil



MODULE_PATH = os.path.dirname(__file__) or os.getcwd()
TMSTAF_PID_FILE = os.path.join(MODULE_PATH, 'tmstaf.pid')


def addTmstafLibPath():
    sys.path.insert(0, os.path.dirname(MODULE_PATH))


def addStafLibPath():
    #Todo: we should not hardcode this path! 2009-10-14 camge
    if os.name == 'nt':
        sys.path.insert(0, r'C:\Source\STAF-EC2\bin')

addStafLibPath()
addTmstafLibPath()


import tmstaf.processUtil
import secureCloud.agentBVT.testingClient
import secureCloud.agentBVT.util
from tmstaf.testwareConfig import TestwareConfig
from tmstaf.productSetting import ProductSetting
from tmstaf.testRunner import BaseTestRunner
from tmstaf.util import getException
import threading
VERSION = 'v2.1.0'

import secureCloud.config.result_config
import secureCloud.scAgent.file
log_path = secureCloud.config.result_config.result_path
chefLogger = secureCloud.config.result_config.chefLogger
stafLogger = secureCloud.config.result_config.stafLogger
errorLogger = secureCloud.config.result_config.errorLogger
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
        

if __name__ == '__main__':

    # Load global specific settings
    GLOBAL_SETTING_PATH = os.getcwd()+'product.ini'
    ENV_SETTING_PATH = os.getcwd()+'\env.ini'
    logging.debug("global setting path %s" % GLOBAL_SETTING_PATH)
    GLOBAL_SETTING = secureCloud.agentBVT.util.config(GLOBAL_SETTING_PATH)
    logging.debug("global setting:%s" % GLOBAL_SETTING)
    ENV_SETTING = secureCloud.agentBVT.util.config(ENV_SETTING_PATH)
    OS = ENV_SETTING['ENV']['os']
    OSTYPE = ENV_SETTING['ENV']['ostype']
    CSP_TYPE = ENV_SETTING['ENV']['csp_type']
    strLog='chef'
    strLogLevel=logging.INFO
  
  
    if OSTYPE=='64':
        PREBOOT_LOG=GLOBAL_SETTING[OS]["sc_agent_path_64"]+GLOBAL_SETTING[OS]["preboot_logfile"]
    else:
        PREBOOT_LOG=GLOBAL_SETTING[OS]["sc_agent_path_32"]+GLOBAL_SETTING[OS]["preboot_logfile"]

    print(PREBOOT_LOG)
    logFile=TmstafMain().setLogFile(strLog,strLogLevel)
    
        # All messages which come from "tmstaf" logger will be written into tmstaf.log
    result=secureCloud.agentBVT.testingClient.check_preboot_log(PREBOOT_LOG)

    if result==0:
        logFile.info('pass: check_preboot_log')
    else:    
        logFile.info('FAIL: check_preboot_log')
