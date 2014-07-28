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
    
 
        
def main(options):
    retval = 0
    if options.proxy_setting==False:
        errorLogger.error("[Proxy] proxy setting is required")
        retval = 1
        return retval
        # Load global specific settings
    GLOBAL_SETTING_PATH = ("%s/product.ini" % MODULE_PATH)
    ENV_SETTING_PATH = ("%s/env.ini" % MODULE_PATH)
    log_path = result_path = ("%s/result/" % MODULE_PATH)
    GLOBAL_SETTING = secureCloud.agentBVT.util.config(GLOBAL_SETTING_PATH)
    sc_path = secureCloud.scAgent.Agent.get_sc_root()
    stafLogger.debug("Start proxy setup and checking") 
    scconfig_path = secureCloud.scAgent.Agent.get_scconfig_path()
    result=secureCloud.agentBVT.testingClient.setup_proxy(scconfig_path,options.proxy_setting)
   
    if result==0:
            secureCloud.agentBVT.testingClient.write_report(log_path,'pass: proxy setup success.')
            stafLogger.critical('pass: proxy setup success.')
            retval=0
    else:
            secureCloud.agentBVT.testingClient.write_report(log_path,'FAIL: %s is not removed. tear down userScript not works.'%options.userScript_file) 
            stafLogger.critical('FAIL: proxy setup fail.')
            errorLogger.error('FAIL: proxy setup fail.')
            retval=1
    secureCloud.agentBVT.testingClient.write_sctm_report(log_path,"Proxy setup and testing",retval)
    stafLogger.debug("End of proxy setup and checking")           
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
    action_group.add_option('-y', '--proxy-setting', type='string', dest='proxy_setting',
                    default=False,metavar= 'proxy_setting',
                    help='proxy setting, ex: -y "http://user:password@proxy-host:port"')
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
    stafLogger.critical('*** START RPOXY TESTCASE ***\n') 
    if __retval__ == 0:
        __options__ = _handle_options(sys.argv[1:])
        __retval__ = main(__options__)
    stafLogger.critical('*** EXIT WITH (%s) ***\n' %str(__retval__))
    sys.exit(__retval__)