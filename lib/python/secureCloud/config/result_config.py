import logging
import platform
import secureCloud.scAgent.Agent


log_level = logging.DEBUG

os_type = platform.system()

if platform.system() == "Windows":
        result_path='C:\\STAF\\lib\\python\\secureCloud\\chef\\result\\'
else:
        result_path = '/usr/local/STAF/lib/python/chef/result/'

scprov_ini_path = '%s/scprov.ini'%secureCloud.scAgent.Agent.get_sc_root()


chefLogger = secureCloud.scAgent.file.setLogFile(("%schef.log")%result_path, logging.INFO , 'chefLogger')
stafLogger = secureCloud.scAgent.file.setLogFile(("%sstaf.log")%result_path,logging.DEBUG, 'stafLogger')
errorLogger = secureCloud.scAgent.file.setLogFile(("%serror.log")%result_path,logging.ERROR, 'errorLogger')