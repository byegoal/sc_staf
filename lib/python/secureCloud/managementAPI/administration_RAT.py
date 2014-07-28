import time
import mapi_lib
import logging
import base64
import mapi_util
import urllib 

admin_log = logging.getLogger('admin_logger')
admin_log.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(levelname)s][%(filename)s][%(funcName)s][%(lineno)d]-%(message)s ')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
admin_log.addHandler(handler)



def readDSMConnSettings():
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	xml_result = broker_api_lib.readDSMConnSettings()
	if not xml_result:
		admin_log.debug("call readDSMConnSettings return False")
		return False
	
	dsm_setting = xml_result.getElementsByTagName("DSMConnSettings")[0]
	if not dsm_setting:
		admin_log.debug("no DSM setting is found")
		return False
	else:
		return True


#need to have DSM server to connect
def updateDSMConnSettings(dsm_enable, dsm_server, dsm_port, dsm_user, dsm_pass):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	#update DSM setting
	xml_result = broker_api_lib.updateDSMConnSettings(dsm_enable, dsm_server, dsm_port, dsm_user, dsm_pass)
	if not xml_result:
		return False

	#get current DSM setting
	xml_result = broker_api_lib.readDSMConnSettings()
	if not xml_result:
		return False
	
	dsm_setting = xml_result.getElementsByTagName("DSMConnSettings")[0]

	dsm_enable_node = dsm_setting.getElementsByTagName("Enabled")[0]
	current_dsm_enable = mapi_util.getText(dsm_enable_node.childNodes)

	dsm_server_node = dsm_setting.getElementsByTagName("ServerAddress")[0]
	current_dsm_server = mapi_util.getText(dsm_server_node.childNodes)

	dsm_port_node = dsm_setting.getElementsByTagName("Port")[0]
	current_dsm_port = mapi_util.getText(dsm_port_node.childNodes)

	dsm_user_node = dsm_setting.getElementsByTagName("Username")[0]
	current_dsm_user = mapi_util.getText(dsm_user_node.childNodes)

	dsm_pass_node = dsm_setting.getElementsByTagName("Password")[0]
	current_dsm_pass = mapi_util.getText(dsm_pass_node.childNodes)


	if current_dsm_enable == dsm_enable and current_dsm_server == dsm_server and current_dsm_port == dsm_port and current_dsm_user == dsm_user and current_dsm_pass == dsm_pass:
		return True
	else:
		return False



def getKmipConnectionSetting():
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	xml_result = broker_api_lib.getKmipConnectionSetting()
	if not xml_result:
		admin_log.debug("call getKmipConnectionSetting return False")
		return False
	
	kmip_setting = xml_result.getElementsByTagName("kmipConnectionSetting")[0]

	if kmip_setting:
		return True
	else:
		admin_log.debug("no kmip setting is found")
		return False


#need to have KMIP server to connect
def setKmipConnectionSetting(dsm_enable, dsm_server, dsm_port, dsm_user, dsm_pass):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	#update DSM setting
	xml_result = broker_api_lib.setKmipConnectionSetting(dsm_enable, dsm_server, dsm_port, dsm_user, dsm_pass)
	if not xml_result:
		return False

	#get current DSM setting
	xml_result = broker_api_lib.getKmipConnectionSetting()
	if not xml_result:
		return False
	
	dsm_setting = xml_result.getElementsByTagName("DSMConnSettings")[0]

	dsm_enable_node = dsm_setting.getElementsByTagName("Enabled")[0]
	current_dsm_enable = mapi_util.getText(dsm_enable_node.childNodes)

	dsm_server_node = dsm_setting.getElementsByTagName("ServerAddress")[0]
	current_dsm_server = mapi_util.getText(dsm_server_node.childNodes)

	dsm_port_node = dsm_setting.getElementsByTagName("Port")[0]
	current_dsm_port = mapi_util.getText(dsm_port_node.childNodes)

	dsm_user_node = dsm_setting.getElementsByTagName("Username")[0]
	current_dsm_user = mapi_util.getText(dsm_user_node.childNodes)

	dsm_pass_node = dsm_setting.getElementsByTagName("Password")[0]
	current_dsm_pass = mapi_util.getText(dsm_pass_node.childNodes)


	if current_dsm_enable == dsm_enable and current_dsm_server == dsm_server and current_dsm_port == dsm_port and current_dsm_user == dsm_user and current_dsm_pass == dsm_pass:
		return True
	else:
		return False



if __name__ == '__main__':

	print readDSMConnSettings()

	#dsm_enable = "true"
	#dsm_server = "172.18.0.240"
	#dsm_port = "4119"
	#dsm_user = "masteradmin"
	#dsm_pass = "Trend@123"
	#print updateDSMConnSettings(dsm_enable, dsm_server, dsm_port, dsm_user, dsm_pass)


	#print getKmipConnectionSetting()