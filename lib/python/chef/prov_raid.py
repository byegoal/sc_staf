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
    if options.raid_fs==False:
        errorLogger.error("[RAIDFS] raid file system is required")
        retval = 1
        return retval
    if options.raid_name==False:
        errorLogger.error("[RAIDNAME] raid name is required")
        retval = 1
        return retval
        # Load global specific settings
    GLOBAL_SETTING = secureCloud.agentBVT.util.config("%s/product.ini" % MODULE_PATH)
    sc_path = secureCloud.scAgent.Agent.get_sc_root()
    
    raid_name=options.raid_name
    raid_level="RAID0"
    raid_fs = options.raid_fs
    raid_desc = "Automate RAID creation"
    mount_point = "/sc/auto_raid"
    agent_vm_guid = secureCloud.agentBVT.testingClient.get_agent_vmGuid(sc_path)
    if agent_vm_guid == False:
        errorLogger.error('FAIL: encrypt RAID fail. cannot find agent_vm_Guid')
        retval=1
    server_vm_guid = secureCloud.agentBVT.testingClient.get_server_vmGuid_by_agent_vmGuid(agent_vm_guid)
    if server_vm_guid == False:
        errorLogger.error('FAIL: encrypt RAID fail. cannot find server_vm_guid')
        return 1
    stafLogger.debug("agent_vm_guid=%s, server_vm_guid=%s \n" % (agent_vm_guid,server_vm_guid))
    stafLogger.debug("Start RAID provision") 
    result_encrypt_raid = secureCloud.agentBVT.testingClient.encrypt_RAID_server(server_vm_guid, raid_name, raid_fs, mount_point,sc_path)
    if result_encrypt_raid==0:
            stafLogger.critical('pass: encrypt RAID successful.')
    else:
            secureCloud.agentBVT.testingClient.write_report(log_path,'FAIL: encrypt RAID fail. RAID device name:%s'%raid_name) 
            stafLogger.critical('FAIL: encrypt RAID fail.')
            errorLogger.error('FAIL: encrypt RAID fail. RAID device name:%s'%raid_name)
            retval=1
    secureCloud.scAgent.file.write_sctm_report(log_path,"RAID Provision",retval)
    stafLogger.debug("End of RAID provision")     
    
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
    action_group.add_option('-n', '--raid-name', type='string', dest='raid_name',
                    default=False,metavar= 'raid_name',
                    help='RAID name, ex: -n "/dev/auto_raid"')
    action_group.add_option('-f', '--raid-filesystem', type='string', dest='raid_fs',
                    default=False,metavar= 'raid_fs',
                    help='RAID file system, ex: -f ext3')
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