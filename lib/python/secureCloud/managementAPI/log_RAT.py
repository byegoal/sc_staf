import time
import mapi_lib
import logging
import mapi_util
import simulator_lib

log_log = logging.getLogger('log_logger')
log_log.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(levelname)s][%(filename)s][%(funcName)s][%(lineno)d]-%(message)s ')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
log_log.addHandler(handler)


def listLogGroups():
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	xml_result = broker_api_lib.listLogGroups()
	if not xml_result:
		log_log.debug("call listLogGroups return False")
		return False
	
	logGroups_node = xml_result.getElementsByTagName("logGroups")[0]
	logGroup_nodes = logGroups_node.getElementsByTagName("logGroup")
	if not logGroup_nodes:
		log_log.debug("no log groups are found")
		return False
	
	return True


def queryLog(from_time, to_time, log_type):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	#upload a device so that there is log data to query from
	config_name="queryLog"
	csp_provider="queryLog_csp"
	csp_zone="queryLog_zone"
	image_id="queryLog_image"
	device_id="queryLog_device"
	device_id_list=[device_id]

	simulator_lib.create_config(config_name, csp_provider, csp_zone, image_id, device_id_list)
	simulator_lib.upload_inventory(config_name, image_id)



	xml_result = broker_api_lib.queryLog(from_time, to_time, log_type)
	if not xml_result:
		log_log.debug("call queryLog return False")
		return False


	logGroups_node = xml_result.getElementsByTagName("log")[0]
	logGroup_nodes = logGroups_node.getElementsByTagName("logEvents")
	if not logGroup_nodes:
		log_log.debug("no log groups are found")
		return False

	return True


def exportLogQuery(from_time, to_time, log_type):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	#upload a device so that there is log data to query from
	config_name="exportLogQuery"
	csp_provider="exportLogQuery_csp"
	csp_zone="exportLogQuery_zone"
	image_id="exportLogQuery_image"
	device_id="exportLogQuery_device"
	device_id_list=[device_id]

	simulator_lib.create_config(config_name, csp_provider, csp_zone, image_id, device_id_list)
	simulator_lib.upload_inventory(config_name, image_id)

	xml_result = broker_api_lib.exportLogQuery(from_time, to_time, log_type)
	if not xml_result:
		log_log.debug("call exportLogQuery return False")
		return False


	logfile_node = xml_result.getElementsByTagName("logFile")[0]
	data_node = logfile_node.getElementsByTagName("Data")[0]
	export_data = mapi_util.getText(data_node)
	if export_data:
		return True
	else:
		log_log.debug("no export data")
		return False


def listLogArchives():
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	xml_result = broker_api_lib.listLogArchives()
	if not xml_result:
		log_log.debug("call listLogArchives return False")
		return False


	logArchives_node = xml_result.getElementsByTagName("logArchives")[0]
	if not logArchives_node:
		log_log.debug("no log archives are found")
		return False

	return True


#tobe test
def getLogArchive(log_id):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	xml_result = broker_api_lib.getLogArchive()
	if not xml_result:
		return False

#tobe test
def deleteLog(log_id):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	xml_result = broker_api_lib.deleteLog()
	if not xml_result:
		return False



if __name__ == '__main__':
	#listLogGroups()


	#from_time="2012-06-01T01:58"
	#to_time="2012-10-08T00:00"
	from_time=""
	to_time=""
	log_type="SYSTEM_EVENTS"
	#print queryLog(from_time, to_time, log_type)

	from_time=""
	to_time=""
	log_type="SYSTEM_EVENTS"
	#print exportLogQuery(from_time, to_time, log_type)

	#print listLogArchives()