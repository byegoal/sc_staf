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
        
def main():
    retval = 0
        # Load global specific settings
    GLOBAL_SETTING = secureCloud.agentBVT.util.config("%s/product.ini" % MODULE_PATH)
    sc_path = secureCloud.scAgent.Agent.get_sc_root()
    agent_vm_guid = secureCloud.agentBVT.testingClient.get_agent_vmGuid(sc_path)
    if agent_vm_guid == False:
        errorLogger.error('FAIL: Delete VM on SCMC fail. cannot find agent_vm_Guid')
        retval=1
    server_vm_guid = secureCloud.agentBVT.testingClient.get_server_vmGuid_by_agent_vmGuid(agent_vm_guid)
    if server_vm_guid == False:
        errorLogger.error('FAIL: Delete VM on SCMC fail. cannot find server_vm_guid')
        return 1
    stafLogger.debug("agent_vm_guid=%s, server_vm_guid=%s \n" % (agent_vm_guid,server_vm_guid))
    stafLogger.debug("Start Delete VM on SCMC") 
    result = secureCloud.agentBVT.testingClient.delete_vm_scmc(agent_vm_guid)
    if result==0:
            stafLogger.critical('pass: Delete VM on SCMC successful.')
    else:
            secureCloud.agentBVT.testingClient.write_report(log_path,'FAIL: Delete VM on SCMC fail. server_vm_guid:%s'%server_vm_guid) 
            stafLogger.critical('FAIL: Delete VM on SCMC fail.')
            errorLogger.error('FAIL: Delete VM on SCMC fail. server_vm_guid:%s'%server_vm_guid)
            retval=1
    secureCloud.scAgent.file.write_sctm_report(log_path,"Delete VM on SCMC",retval)
    stafLogger.debug("End of Delete VM on SCMC")     
    
    #secureCloud.agentBVT.testingClient.write_sctm_report(log_path,"RAID Provision",retval)      
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
    parser.add_option_group(action_group)
    (options, args) = parser.parse_args(argv)  
    return options 


if __name__ == "__main__":  
    __retval__ = 0
    stafLogger.critical('*** START DELETE VM ON SCMC ***\n') 
    if __retval__ == 0:
        __options__ = _handle_options(sys.argv[1:])
        __retval__ = main()
    stafLogger.critical('*** EXIT WITH (%s) ***\n' %str(__retval__))
    sys.exit(__retval__)