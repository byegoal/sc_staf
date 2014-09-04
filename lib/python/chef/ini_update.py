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

import secureCloud.agentBVT.testingClient
import secureCloud.agentBVT.util
import secureCloud.scAgent.file
import secureCloud.scAgent.Agent
#from tmstaf.testwareConfig import TestwareConfig
#from tmstaf.productSetting import ProductSetting
#from tmstaf.testRunner import BaseTestRunner
#from tmstaf.util import getException
import threading
VERSION = 'v2.1.0'

import secureCloud.config.result_config
import secureCloud.scAgent.file
import secureCloud.managementAPI.mapi_config
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
    if options.access_key_id==False:
        errorLogger.error("[INIUPDATE] access_key_id is required")
        retval = 1
        return retval
    if options.secret_access_key==False:
        errorLogger.error("[INIUPDATE] secret_access_key is required")
        retval = 1
        return retval
    if options.account_id==False:
        errorLogger.error("[INIUPDATE] account_id is required")
        retval = 1
        return retval
    if options.passphrase==False:
        errorLogger.error("[INIUPDATE] passphrase is required")
        retval = 1
        return retval
    if options.auth_name==False:
        errorLogger.error("[INIUPDATE] auth_name is required")
        retval = 1
        return retval
    if options.auth_password==False:
        errorLogger.error("[INIUPDATE] auth_password is required")
        retval = 1
        return retval
    if options.ms_host==False:
        errorLogger.error("[INIUPDATE] MAPI URL is required")
        retval = 1
        return retval
        # Load global specific settings
    product_file_path = "%s/product.ini" % MODULE_PATH
    GLOBAL_SETTING = secureCloud.agentBVT.util.config(product_file_path)
    sc_path = secureCloud.scAgent.Agent.get_sc_root()
    broker_api_config_path = secureCloud.managementAPI.mapi_config.broker_api_config_path
    sdk_config_path = secureCloud.managementAPI.mapi_config.sdk_config_path
    stafLogger.debug("Start ini update") 
    secureCloud.agentBVT.testingClient.ini_update(broker_api_config_path, "sc", "access_key_id", options.access_key_id)
    secureCloud.agentBVT.testingClient.ini_update(broker_api_config_path, "sc", "secret_access_key", options.secret_access_key)
    secureCloud.agentBVT.testingClient.ini_update(broker_api_config_path, "sc", "api_account_id", options.account_id)
    secureCloud.agentBVT.testingClient.ini_update(broker_api_config_path, "sc", "api_passphrase", options.passphrase)
    secureCloud.agentBVT.testingClient.ini_update(sdk_config_path, "authentication", "AUTH_NAME", options.auth_name)
    secureCloud.agentBVT.testingClient.ini_update(sdk_config_path, "authentication", "AUTH_PASSWORD", options.auth_password)
    secureCloud.agentBVT.testingClient.ini_update(sdk_config_path, "authentication", "MS_HOST", options.ms_host)
    stafLogger.debug("End of ini update") 
    
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
    action_group.add_option('-a', '--access-key-id', type='string', dest='access_key_id',
                    default=False,metavar= 'access_key_id',
                    help='managementAPI access_key_id')
    action_group.add_option('-s', '--secret-access-key', type='string', dest='secret_access_key',
                    default=False,metavar= 'secret_access_key',
                    help='managementAPI secret_access_key')
    action_group.add_option('-i', '--account-id', type='string', dest='account_id',
                    default=False,metavar= 'account_id',
                    help='secure cloud account_id')
    action_group.add_option('-p', '--passphrase', type='string', dest='passphrase',
                    default=False,metavar= 'passphrase',
                    help='secure cloud account passphrase')
    action_group.add_option('-n', '--auth-name', type='string', dest='auth_name',
                    default=False,metavar= 'auth_name',
                    help='secure cloud account name')
    action_group.add_option('-w', '--auth-password', type='string', dest='auth_password',
                    default=False,metavar= 'auth_password',
                    help='secure cloud account password')
    action_group.add_option('-m', '--ms-host', type='string', dest='ms_host',
                    default=False,metavar= 'ms_host',
                    help='MAPI base url')
    parser.add_option_group(action_group)
    (options, args) = parser.parse_args(argv)  
    return options 


if __name__ == "__main__":  
    __retval__ = 0
    stafLogger.critical('*** START INI UPDATE ***\n') 
    if __retval__ == 0:
        __options__ = _handle_options(sys.argv[1:])
        __retval__ = main(__options__)
    stafLogger.critical('*** EXIT WITH (%s) ***\n' %str(__retval__))
    sys.exit(__retval__)