import logging
import optparse
import os
import sys
import time
import re
import cPickle
import shutil
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
    
        
def main():
    retval = 0
    GLOBAL_SETTING = secureCloud.agentBVT.util.config("%s/product.ini" % MODULE_PATH)
    sc_path = secureCloud.scAgent.Agent.get_sc_root()
    boot_device_guid = secureCloud.agentBVT.testingClient.get_boot_device_guid(sc_path)
    stafLogger.debug('Boot device_guid in config.xml: %s \n'%boot_device_guid)
        # All messages which come from "tmstaf" logger will be written into tmstaf.log
    retval=secureCloud.agentBVT.testingClient.check_device_encrypted_by_device_guid(GLOBAL_SETTING['ManagementAPI']['access_key_id'],GLOBAL_SETTING['ManagementAPI']['secret_access_key'],sc_path,boot_device_guid,360)
    
    if retval==0:
        stafLogger.critical('pass: boot is encrypted, boot_device_guid=%s'%boot_device_guid)          
    else:
        stafLogger.critical('FAIL: boot is NOT encrypted, boot_device_guid=%s'%boot_device_guid)
        errorLogger.error('FAIL: boot is NOT encrypted, boot_device_guid=%s'%boot_device_guid)
    secureCloud.scAgent.file.write_sctm_report(log_path,"Check Boot Volume Encrypted",retval)
    return retval

if __name__ == "__main__":  
    __retval__ = 0
    stafLogger.critical('*** START BOOT VOLUME ENCRYPTED CHECKING ***\n') 
    if __retval__ == 0:
        __retval__ = main()
    stafLogger.critical('*** EXIT WITH (%s) ***\n' %str(__retval__))
    sys.exit(__retval__)