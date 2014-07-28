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
import secureCloud.scAgent.Agent
from tmstaf.testwareConfig import TestwareConfig
from tmstaf.productSetting import ProductSetting
from tmstaf.testRunner import BaseTestRunner
from tmstaf.util import getException
import threading
VERSION = 'v2.1.0'

import secureCloud.config.result_config
import secureCloud.scAgent.file
import secureCloud.managementAPI.mapi_config
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
    stafLogger.debug("Start to do reboot checking") 
    if options.userScript_file==False:
        errorLogger.error("userScript file is required")
        retval = 1
        return retval
        # Load global specific settings
    product_file_path = "%s/product.ini" % MODULE_PATH
    GLOBAL_SETTING = secureCloud.agentBVT.util.config(product_file_path)
    sc_path = secureCloud.scAgent.Agent.get_sc_root()
    
    service_result = secureCloud.agentBVT.testingClient.is_sc_start()
    userScript_result=secureCloud.agentBVT.testingClient.is_file_exist(options.userScript_file)
    if service_result==0 and userScript_result==0:
            stafLogger.critical('pass: scagent is running, mountComplete userScript works.')
            retval=0
    else:
         if not service_result==0:
            stafLogger.critical('FAIL: scagent is NOT running')
            errorLogger.error('FAIL: scagent is NOT running')
         if not userScript_result==0:
            stafLogger.critical('FAIL: %s is not exist. mountComplete userScript not works.'%options.userScript_file)
            errorLogger.error('FAIL: %s is not exist. mountComplete userScript not works.'%options.userScript_file)
         retval=1
    secureCloud.scAgent.file.write_sctm_report(log_path,"Reboot Check",retval)
    stafLogger.debug("End of scagent reboot checking")           
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
                    help='mountComplete userScript file path. ex: -f "/mnt/datavolumefolder/file1')
    parser.add_option_group(action_group)
    (options, args) = parser.parse_args(argv)  
    return options 


if __name__ == "__main__":  
    __retval__ = 0
    stafLogger.critical('*** START REBOOT CHECK ***\n') 
    if __retval__ == 0:
        __options__ = _handle_options(sys.argv[1:])
        __retval__ = main(__options__)
    stafLogger.critical('*** EXIT WITH (%s) ***\n' %str(__retval__))
    sys.exit(__retval__)