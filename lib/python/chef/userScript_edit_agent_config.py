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
    if options.userScript_type ==False:
        errorLogger.error("userScript_type is required")
        return 1    
    if options.sh_file==False:
        errorLogger.error("sh_file is required")
        return 1
        # Load global specific settings
    GLOBAL_SETTING = secureCloud.agentBVT.util.config("%s/product.ini" % MODULE_PATH)
    sc_path = secureCloud.scAgent.Agent.get_sc_root()
    stafLogger.debug("Start to edit config.xml")
    result=secureCloud.agentBVT.testingClient.update_agent_config_for_userScript(sc_path,options.userScript_type,options.sh_file)
    if result==0:
            result='pass'
            secureCloud.agentBVT.testingClient.write_report(log_path,'%s: edit agent_config for %s'%(result,options.userScript_type))
            chefLogger.info('%s: edit agent_config for %s'%(result,options.userScript_type))
    else:
            result='FAIL'
            secureCloud.agentBVT.testingClient.write_report(log_path,'%s: edit agent_config for %s'%(result,options.userScript_type)) 
            chefLogger.info('%s: edit agent_config for %s'%(result,options.userScript_type))
            retval=1
    
    stafLogger.debug("End of editing agent config for userScript")           
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
    action_group.add_option('-t', '--userScript-type', type='choice', dest='userScript_type',
                    default=False, metavar= 'userScript_type',choices=['mountComplete', 'teardown'], 
                    help='userScript type (mountComplete | teardown)')
    action_group.add_option('-f', '--sh-file', type='string', dest='sh_file',
                    default=False,metavar= 'sh_file',
                    help='sh file. ex: -f "/var/lib/securecloud/rmfile.sh"')
    parser.add_option_group(action_group)
    (options, args) = parser.parse_args(argv)  
    return options 


if __name__ == "__main__":  
    __retval__ = 0
    stafLogger.critical('*** START EDIT AGENT CONFIG FOR USERSCRIPT ***\n') 
    if __retval__ == 0:
        __options__ = _handle_options(sys.argv[1:])
        __retval__ = main(__options__)
    stafLogger.critical('*** EXIT WITH (%s) ***\n' %str(__retval__))
    if not __retval__==0:
        secureCloud.agentBVT.testingClient.write_sctm_report(log_path,"RAID Provision",1)
    sys.exit(__retval__)