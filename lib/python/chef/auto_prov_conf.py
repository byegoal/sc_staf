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
chefLogger = secureCloud.scAgent.file.setLogFile(("%schef.log")%log_path, logging.INFO , 'chefLogger')
stafLogger = secureCloud.scAgent.file.setLogFile(("%sstaf.log")%log_path,logging.DEBUG, 'stafLogger')
errorLogger = secureCloud.scAgent.file.setLogFile(("%serror.log")%log_path,logging.ERROR, 'errorLogger')

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
    if not options.auto_prov:
        errorLogger.error("[AutoProv] auto provision setting is required")
        return 1
        # Load global specific settings
    GLOBAL_SETTING = secureCloud.agentBVT.util.config("%s/product.ini" % MODULE_PATH)
    sc_path = secureCloud.scAgent.Agent.get_sc_root()
    auto_prov = options.auto_prov
    agent_vm_guid = secureCloud.agentBVT.testingClient.get_agent_vmGuid(sc_path)
    server_vm_guid = secureCloud.agentBVT.testingClient.get_server_vmGuid_by_agent_vmGuid(agent_vm_guid) 
    stafLogger.debug("Start to do auto-provision setting update")  
    result=secureCloud.agentBVT.testingClient.update_auto_prov(server_vm_guid,auto_prov)
    if result==0:
            stafLogger.critical('pass: auto-provision conf update successful')
    else:
            stafLogger.critical('FAIL: auto-provision conf update fail')
            retval=1
    secureCloud.scAgent.file.write_sctm_report(log_path,"Update Auto-Provision Conf",result)
    stafLogger.debug("End of auto-provision setting update")           
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
    action_group.add_option('-a', '--auto-prov', type='choice', dest='auto_prov',
                    default=False, metavar= 'auto_prov',choices=['on', 'off'], 
                    help='auto provision (on | off)')
    parser.add_option_group(action_group)
    (options, args) = parser.parse_args(argv)  
    return options 


if __name__ == "__main__":  
    __retval__ = 0
    stafLogger.critical('*** START UPDATING AUTO-PROVISION CONF ***\n') 
    if __retval__ == 0:
        __options__ = _handle_options(sys.argv[1:])
        __retval__ = main(__options__)
    stafLogger.critical('*** EXIT WITH (%s) ***\n' %str(__retval__))        
    sys.exit(__retval__)