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
    if not options.device_name:
        errorLogger.error("[CheckEncrytped] device name is required")
        return 1
               
    GLOBAL_SETTING = secureCloud.agentBVT.util.config("%s/product.ini" % MODULE_PATH)
    sc_path = secureCloud.scAgent.Agent.get_sc_root()
    device_name = options.device_name
    agent_vm_guid = secureCloud.agentBVT.testingClient.get_agent_vmGuid(sc_path)
    server_vm_guid = secureCloud.agentBVT.testingClient.get_server_vmGuid_by_agent_vmGuid(agent_vm_guid) 
    stafLogger.debug("Start device encryption checking") 
    device_msuid = secureCloud.agentBVT.testingClient.get_device_guid_by_agent_config(sc_path,device_name)
    result=secureCloud.agentBVT.testingClient.check_device_encrypted_by_device_guid(server_vm_guid,device_msuid,sc_path,10)
    
    if result==0:
            stafLogger.critical('pass: %s is encrypted, device_msuid=%s\n'%(device_name,device_msuid))
    else:
            stafLogger.critical('FAIL: %s is NOT encrypted, device_msuid=%s\n'%(device_name,device_msuid))
            errorLogger.error('FAIL: %s is NOT encrypted, device_msuid=%s\n'%(device_name,device_msuid))
            retval=1
    secureCloud.scAgent.file.write_sctm_report(log_path,"Check RAID is Encrypted",result)
    stafLogger.debug("End of single device encryption checking")     
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
    action_group.add_option('-n', '--device-name', type='string', dest='device_name',
                    default=False,metavar= 'device_name',
                    help='device name, ex: -n "/dev/auto_raid"')
    parser.add_option_group(action_group)
    (options, args) = parser.parse_args(argv)  
    return options 


if __name__ == "__main__":  
    __retval__ = 0
    stafLogger.critical('*** START RAID PROVISION TESTCASE ***\n') 
    if __retval__ == 0:
        __options__ = _handle_options(sys.argv[1:])
        __retval__ = main(__options__)
    stafLogger.critical('*** EXIT WITH (%s) ***\n' %str(__retval__))
    sys.exit(__retval__)