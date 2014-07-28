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
    if not options.device_array:
        errorLogger.error("[ServerProv] devices is required")
        retval = 1
        return retval
        # Load global specific settings
    GLOBAL_SETTING = secureCloud.agentBVT.util.config("%s/product.ini" % MODULE_PATH)
    sc_path = secureCloud.scAgent.Agent.get_sc_root()
    scprov_config_path = sc_path+'/scprov.ini'
    scprov_config = secureCloud.agentBVT.util.config(scprov_config_path)
    devices_list = options.device_array.split(',') 
    result_list =[]
    #do find device_name_list
    for devices in devices_list:
        device_name = scprov_config[devices]['device_name']
        agent_vmGuid = secureCloud.agentBVT.testingClient.get_agent_vmGuid(sc_path)
        vm_guid = secureCloud.agentBVT.testingClient.get_server_vmGuid_by_agent_vmGuid(agent_vmGuid)
        device_msuid = secureCloud.agentBVT.testingClient.get_device_guid_by_agent_config(sc_path,device_name)
        if(device_msuid)==None:
            errorLogger.error("[ServerProv] device_msuid is null,device_name=%s, agent_vm_guid=%s"%(device_name,agent_vmGuid))
            retval = 1
            secureCloud.scAgent.file.write_sctm_report(log_path,"Server Provision",retval)
            return retval
        if not scprov_config[devices].has_key('existing_data') :
            preserve_data='yes'
            file_system = ''
            mount_point= ''   
        else:
            if scprov_config[devices]['existing_data']=='erase':
                preserve_data='no'
                file_system = scprov_config[devices]['filesystem']
                mount_point= scprov_config[devices]['mount_point']
            else:
                preserve_data='yes'
                file_system = ''
                mount_point= ''            
        stafLogger.debug("Start to request server provision")
        server_prov_result=secureCloud.agentBVT.testingClient.do_server_provision(vm_guid,device_msuid,preserve_data,file_system,mount_point)
        if server_prov_result==0:
            stafLogger.critical('pass: %s is doing server provision, msuid=%s'%(device_name,device_msuid))
        else:
            stafLogger.critical('FAIL: %s can not do server provision, msuid=%s'%(device_name,device_msuid))
            errorLogger.error("[ServerProv] FAIL: %s can not do server provision, msuid=%s"%(device_name,device_msuid))
            retval=1
    secureCloud.scAgent.file.write_sctm_report(log_path,"Server Provision",retval)
    stafLogger.debug("End of server provision")           
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
    action_group.add_option('-d', '--device-array', type='string', dest='device_array',
                    default=False,metavar= 'device_array',
                    help='devices to do provision. ex: -d "Device1,Device2"')
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
    sys.exit(__retval__)