import logging
import optparse
import os
import sys
import time
import re
import cPickle
import shutil
from optparse import OptionParser, OptionGroup
try:
    from cookielib import logger
except ImportError, e:
    logging.debug("import logger fail: %s" % e)

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


import sdkMapi.MAPI_Service as MAPI_Service
import sdkMapi.MAPI_Inventory as MAPI_Inventory
import secureCloud.agentBVT.testingClient as testingClient
import secureCloud.agentBVT.util
import secureCloud.scAgent.Agent
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
    if not options.device_type:
        errorLogger.error("[DestroyDeviceKey] device type is required")
        return 1
    sc_path = secureCloud.scAgent.Agent.get_sc_root()
    agent_vm_guid = testingClient.get_agent_vmGuid(sc_path)
    if agent_vm_guid is None or agent_vm_guid==False or agent_vm_guid =='':
        errorLogger.error("[main] agent_vm_guid is null in config.xml")
        return 1
    server_vm_guid = MAPI_Inventory.getImageGUID(agent_vm_guid) 
    if not server_vm_guid or server_vm_guid =='':
        errorLogger.error("[main] server_vm_guid is null by invoke listVM")
        return 1
    device_type = options.device_type
    stafLogger.debug("Start to distroy device key, agent_vm_guid=%s, server_vm_guid=%s"%(agent_vm_guid,server_vm_guid))
    if device_type=='raid':
        device_msuid = testingClient.get_encrypted_raid()
    else:
        device_msuid = testingClient.get_encrypted_single_device()
    if not device_msuid:
        errorLogger.error("[DestroyDeviceKey] no encrypted %s in this VM."%device_type)
        return 1
    # invoke API to destroy device key-----------------------------------------------------------------
    result = MAPI_Service.IsDestroyKey(server_vm_guid,device_msuid)
    if result==0:
        stafLogger.critical('pass: device msuid=%s, Invoke DestroyADeviceKey successful.'%(device_msuid))
    else:
        stafLogger.critical('FAIL: check device msuid=%s status from server FAIL, status incorrect'%(device_msuid))
        errorLogger.error("[DestroyDeviceKey] %s=%s device status incorrect on server"%(device_type,device_msuid))
        retval=1
    stafLogger.debug("End of destroy device key")           
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
    action_group.add_option('-t', '--device-type', type='choice', dest='device_type',
                    default=False, metavar= 'device_type',choices=['single', 'raid'], 
                    help='device type to destroy key (single | raid)')
    parser.add_option_group(action_group)
    (options, args) = parser.parse_args(argv)  
    return options 


if __name__ == "__main__":  
    __retval__ = 0
    stafLogger.critical('*** START SERVER PROV ***\n') 
    if __retval__ == 0:
        __options__ = _handle_options(sys.argv[1:])
        __retval__ = main(__options__)
    stafLogger.critical('*** EXIT WITH (%s) ***\n' %str(__retval__))
    secureCloud.scAgent.file.write_sctm_report(log_path,"Destroy Device Key",__retval__)
    sys.exit(__retval__)