import time
import mapi_lib
import logging
import mapi_util
import mapi_config
import simulator_lib

status_log = logging.getLogger('status_logger')
status_log.setLevel(mapi_config.log_level)
formatter = logging.Formatter('[%(levelname)s][%(filename)s][%(funcName)s][%(lineno)d]-%(message)s ')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
status_log.addHandler(handler)



def getServerData():
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	xml_result = broker_api_lib.getServerData()
	if not xml_result:
		status_log.error("call getServerData return False")
		return False

	server_node = xml_result.getElementsByTagName("serverData")[0]
	if server_node:
		return True
	else:
		status_log.error("no server data is found")
		return False


def serviceStatus():
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	xml_result = broker_api_lib.serviceStatus()
	if not xml_result:
		status_log.error("call serviceStatus return False")
		return False

	status_node = xml_result.getElementsByTagName("diagnosticReport")[0]
	if status_node:
		return True
	else:
		status_log.error("server status is not found")
		return False


def getEntryPoint():
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	xml_result = broker_api_lib.getEntryPoint()
	if not xml_result:
		status_log.error("call getEntryPoint return False")
		return False

	entryPoint_node = xml_result.getElementsByTagName("entryPoint")[0]
	if entryPoint_node:
		return True
	else:
		status_log.error("cannot find the entry point")
		return False


if __name__ == '__main__':

	#print getServerData()

	#print serviceStatus()

	print getEntryPoint()