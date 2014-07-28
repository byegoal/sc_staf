import logging
import logging.handlers
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
    if options.keyword==False:
        errorLogger.error("[CHECKLOG] search keyword is required")
        retval = 1
        return retval  
    if options.file_path==False:
        errorLogger.error("[CHECKLOG] log file path is required")
        retval = 1
        return retval
    if options.case_name==False:
        errorLogger.error("[CHECKLOG] test case name is required")
        retval = 1
        return retval 
    keyword=options.keyword
    agent_log_path  = options.file_path   
    case_name = options.case_name
        # Load global specific settings
    GLOBAL_SETTING = secureCloud.agentBVT.util.config("%s/product.ini" % MODULE_PATH)
    sc_path = secureCloud.scAgent.Agent.get_sc_root()
    agent_vmGuid = secureCloud.agentBVT.testingClient.get_agent_vmGuid(sc_path)
    #keyword = r"DEBUG [KMS - Status Update] Sending instance status to https://10.201.224.67/Agent/API.svc"
    retval=secureCloud.agentBVT.testingClient.check_log(agent_log_path,unicode(keyword),5)
    if retval==0:
        stafLogger.critical('pass: %s' %options.case_name)
    else:
        stafLogger.critical('FAIL: %s' %options.case_name)
        stafLogger.debug('Can not find keyword in log file')
    secureCloud.agentBVT.testingClient.write_sctm_report(log_path,options.case_name,retval)
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
    __retval__ = 0
    stafLogger.critical('*** START CHECK LOG ***\n') 
    if __retval__ == 0:
        __options__ = _handle_options(sys.argv[1:])
        __retval__ = main(__options__)
    stafLogger.critical('*** EXIT WITH (%s) ***\n' %str(__retval__))
    sys.exit(__retval__)