import logging
import optparse
import os
import sys
import time
import re
import cPickle
import shutil
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
    
        
def main():
    retval = 0
    deviceStatus="Encrypted"
    sc_path = secureCloud.scAgent.Agent.get_sc_root()
    agent_vm_guid = testingClient.get_agent_vmGuid(sc_path)
    if agent_vm_guid is None or agent_vm_guid==False or agent_vm_guid =='':
        errorLogger.error("[main] agent_vm_guid is null in config.xml")
        return 1
    server_vm_guid = MAPI_Inventory.getImageGUID(agent_vm_guid) 
    if not server_vm_guid or server_vm_guid =='':
        errorLogger.error("[main] server_vm_guid is null by invoke listVM")
        return 1
    boot_device_guid = testingClient.get_boot_device_guid(sc_path)
    if boot_device_guid is None or boot_device_guid==False or boot_device_guid =='':
        errorLogger.error("[main] boot_device_guid is null in config.xml: %s \n"%boot_device_guid)
        return 1
        # All messages which come from "tmstaf" logger will be written into tmstaf.log
    retval=MAPI_Service.isDeviceStatus(server_vm_guid,deviceStatus,deviceGUID=boot_device_guid)
    if retval==0:
        stafLogger.critical('pass: boot is encrypted, boot_device_guid=%s'%boot_device_guid)          
    else:
        stafLogger.critical('FAIL: boot is NOT encrypted, boot_device_guid=%s'%boot_device_guid)
        errorLogger.error('FAIL: boot is NOT encrypted, boot_device_guid=%s'%boot_device_guid)
    return retval

if __name__ == "__main__":  
    __retval__ = 0
    stafLogger.critical('*** START BOOT VOLUME ENCRYPTED CHECKING ***\n') 
    if __retval__ == 0:
        __retval__ = main()
    stafLogger.critical('*** END OF BOOT VOLUME ENCRYPTED CHECKING, EXIT WITH (%s) ***\n' %str(__retval__))
    secureCloud.scAgent.file.write_sctm_report(log_path,"Check Boot Volume Encrypted",__retval__)
    sys.exit(__retval__)