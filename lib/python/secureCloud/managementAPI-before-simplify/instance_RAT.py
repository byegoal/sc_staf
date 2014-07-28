import time
import mapi_lib
import logging
import mapi_util
import mapi_config
import simulator_lib




def getDeviceKeyRequest(instance_id, create_instance=False):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")

	if create_instance:
		config_name="getDeviceKeyRequest"
		csp_provider="getDeviceKeyRequest_csp"
		csp_zone="getDeviceKeyRequest_zone"
		image_id="getDeviceKeyRequest_image"
		device_id="getDeviceKeyRequest_device"
		device_id_list=[device_id]


		simulator_lib.create_config(config_name, csp_provider, csp_zone, image_id, device_id_list)
		simulator_lib.upload_inventory(config_name, image_id)

		device_msuid = broker_api_lib.get_device_msuid_from_device_id(device_id)
		if not device_msuid:
			logging.error("Failed to get source device msuid")
			return False


		#configure device
		device_name=device_id
		device_os="windows"
		device_fs="ntfs"
		write_permission="true"
		device_desc="this is getDeviceKeyRequest"
		device_mount_point="H"
		device_key_size="128"
		xml_result = broker_api_lib.updateDevice(device_msuid, device_id, device_name, device_os, device_fs, write_permission, device_desc, device_mount_point, device_key_size, image_id)
		if not xml_result:
			logging.error("call updateDevice return False")
			return False

		xml_result = broker_api_lib.encryptDevice(device_msuid)
		if not xml_result:
			logging.error("call encryptDevice return False")
			return False

		simulator_lib.encrypt_device(config_name, image_id, [device_id])

		simulator_lib.create_instance(config_name, image_id, instance_id)

		dkr_id = broker_api_lib.get_dkr_id_from_instance_id(instance_id)
		if not dkr_id:
			logging.error("instance msuid is not found")
			return False
	else:
		dkr_id = instance_id


	xml_result = broker_api_lib.getDeviceKeyRequest(dkr_id)
	if not xml_result:
		logging.error("call getInstance return False")
		return False

	return True

	"""
	instance_node = xml_result.getElementsByTagName("instance")[0]
	if instance_id == instance_node.attributes["id"].value.strip():
		return True
	else:
		logging.error("cannot find the instance")
		return False
	"""

"""
 <xs:enumeration value="approved" /> 
  <xs:enumeration value="delivered" /> 
  <xs:enumeration value="pending" /> 
  <xs:enumeration value="denied" /> 
  <xs:enumeration value="failure" /> 
  <xs:enumeration value="expired" /> 
  <xs:enumeration value="revoking" /> 
  <xs:enumeration value="revoked" /> 
  <xs:enumeration value="revoke_ignored" /> 
"""
def updateDeviceKeyRequest(new_dkr_id, dkr_status, create_instance=False, second_status=""):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")

	if create_instance:
		config_name="updateDeviceKeyRequest"
		csp_provider="updateDeviceKeyRequest_csp"
		csp_zone="updateDeviceKeyRequest_zone"
		image_id="updateDeviceKeyRequest_image"
		device_id="updateDeviceKeyRequest_device"
		device_id_list=[device_id]

		instance_id="updateDeviceKeyRequest_instance"
		
		simulator_lib.create_config(config_name, csp_provider, csp_zone, image_id, device_id_list)
		simulator_lib.upload_inventory(config_name, image_id)

		device_msuid = broker_api_lib.get_device_msuid_from_device_id(device_id)
		if not device_msuid:
			logging.error("Failed to get source device msuid")
			return False


		#configure device
		device_name=device_id
		device_os="windows"
		device_fs="ntfs"
		write_permission="true"
		device_desc="this is updateDeviceKeyRequest"
		device_mount_point="H"
		device_key_size="128"
		xml_result = broker_api_lib.updateDevice(device_msuid, device_id, device_name, device_os, device_fs, write_permission, device_desc, device_mount_point, device_key_size, image_id)
		if not xml_result:
			logging.error("call updateDevice return False")
			return False

		xml_result = broker_api_lib.encryptDevice(device_msuid)
		if not xml_result:
			logging.error("call encryptDevice return False")
			return False

		simulator_lib.encrypt_device(config_name, image_id, [device_id])

		simulator_lib.create_instance(config_name, image_id, instance_id)

		dkr_id = broker_api_lib.get_dkr_id_from_instance_id(instance_id)
		if not dkr_id:
			logging.error("instance msuid is not found")
			return False
	
	else:
		dkr_id = new_dkr_id		


	xml_result = broker_api_lib.updateDeviceKeyRequest(dkr_id, dkr_status)
	if not xml_result:
		logging.error("call updateDeviceKeyRequest return False")
		return False

	xml_result = broker_api_lib.updateDeviceKeyRequest(dkr_id, second_status)
	if not xml_result:
		logging.error("call updateDeviceKeyRequest return False")
		return False

	xml_result = broker_api_lib.getDeviceKeyRequest(dkr_id)
	if not xml_result:
		logging.error("call getDeviceKeyRequest return False")
		return False

	dkr_node = xml_result.getElementsByTagName("deviceKeyRequest")[0]
	dkr_state_node =dkr_node.getElementsByTagName("deviceKeyRequestState")[0]
	current_dkr_status = mapi_util.getText(dkr_state_node)


	if second_status:
		if second_status == current_dkr_status:
			return True
	else:
		if current_dkr_status == dkr_status:
			return True


	logging.error("device status is not updated")
	print "current dkr status:%s" % (current_dkr_status)
	return False


	"""
	if second_status:
		if second_status == current_dkr_status:
			return True
		else
			logging.error("device status is not updated")
			print "current dkr status:%s" % (current_dkr_status)
			return False
	else:
		if current_dkr_status == dkr_status:
			return True
		else:
			logging.error("device status is not updated")
			print "current dkr status:%s" % (current_dkr_status)
			return False
	"""

def getInstance(instance_id, create_instance=False):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")

	if create_instance:
		config_name="getInstance"
		csp_provider="getInstance_csp"
		csp_zone="getInstance_zone"
		image_id="getInstance_image"
		device_id="getInstance_device"
		device_id_list=[device_id]


		simulator_lib.create_config(config_name, csp_provider, csp_zone, image_id, device_id_list)
		simulator_lib.upload_inventory(config_name, image_id)

		device_msuid = broker_api_lib.get_device_msuid_from_device_id(device_id)
		if not device_msuid:
			logging.error("Failed to get source device msuid")
			return False


		#configure device
		device_name=device_id
		device_os="windows"
		device_fs="ntfs"
		write_permission="true"
		device_desc="this is getInstance"
		device_mount_point="H"
		device_key_size="128"
		xml_result = broker_api_lib.updateDevice(device_msuid, device_id, device_name, device_os, device_fs, write_permission, device_desc, device_mount_point, device_key_size, image_id)
		if not xml_result:
			logging.error("call updateDevice return False")
			return False

		xml_result = broker_api_lib.encryptDevice(device_msuid)
		if not xml_result:
			logging.error("call encryptDevice return False")
			return False

		simulator_lib.encrypt_device(config_name, image_id, [device_id])

		simulator_lib.create_instance(config_name, image_id, instance_id)

		instance_msuid = broker_api_lib.get_instance_msuid_from_instance_id(instance_id)
		if not instance_msuid:
			logging.error("instance msuid is not found")
			return False
	else:
		instance_msuid = instance_id

	xml_result = broker_api_lib.getInstance(instance_msuid)
	if not xml_result:
		logging.error("call getInstance return False")
		return False

	instance_node = xml_result.getElementsByTagName("instance")[0]
	if instance_id == instance_node.attributes["id"].value.strip():
		return True
	else:
		logging.error("cannot find the instance")
		return False


def flatRequests():
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	config_name="flatRequests"
	csp_provider="flatRequests_csp"
	csp_zone="flatRequests_zone"
	image_id="flatRequests_image"
	device_id="flatRequests_device"
	device_id_list=[device_id]


	simulator_lib.create_config(config_name, csp_provider, csp_zone, image_id, device_id_list)
	simulator_lib.upload_inventory(config_name, image_id)

	device_msuid = broker_api_lib.get_device_msuid_from_device_id(device_id)
	if not device_msuid:
		logging.error("Failed to get source device msuid")
		return False


	#configure device
	device_name=device_id
	device_os="windows"
	device_fs="ntfs"
	write_permission="true"
	device_desc="this is flatRequests"
	device_mount_point="H"
	device_key_size="128"
	xml_result = broker_api_lib.updateDevice(device_msuid, device_id, device_name, device_os, device_fs, write_permission, device_desc, device_mount_point, device_key_size, image_id)
	if not xml_result:
		logging.error("call updateDevice return False")
		return False

	xml_result = broker_api_lib.encryptDevice(device_msuid)
	if not xml_result:
		logging.error("call encryptDevice return False")
		return False

	simulator_lib.encrypt_device(config_name, image_id, [device_id])

	simulator_lib.create_instance(config_name, image_id)

	xml_result = broker_api_lib.flatRequests()
	if not xml_result:
		return False

	keyRequestTree_node = xml_result.getElementsByTagName("keyRequestTree")[0]
	flatRequests_node = keyRequestTree_node.getElementsByTagName("flatRequests")[0]
	flatRequests = flatRequests_node.getElementsByTagName("flatRequest")

	for flatRequest in flatRequests:
		instance_id = flatRequest.attributes["instanceID"].value.strip()
		if instance_id == "inst-"+image_id:
			return True

	logging.error("assigned instance is not found")
	return False


	
def keyRequestTree(pattern):
	print "no more this API"


def listAllRuleResults(new_dkr_id, create_instance=False):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")

	if create_instance:
		config_name="listAllRuleResults"
		csp_provider="listAllRuleResults_csp"
		csp_zone="listAllRuleResults_zone"
		image_id="listAllRuleResults_image"
		device_id="listAllRuleResults_device"
		device_id_list=[device_id]

		instance_id="listAllRuleResults_instance"

		simulator_lib.create_config(config_name, csp_provider, csp_zone, image_id, device_id_list)
		simulator_lib.upload_inventory(config_name, image_id)

		device_msuid = broker_api_lib.get_device_msuid_from_device_id(device_id)
		if not device_msuid:
			logging.error("Failed to get source device msuid")
			return False


		#configure device
		device_name=device_id
		device_os="windows"
		device_fs="ntfs"
		write_permission="true"
		device_desc="this is listAllRuleResults"
		device_mount_point="H"
		device_key_size="128"
		xml_result = broker_api_lib.updateDevice(device_msuid, device_id, device_name, device_os, device_fs, write_permission, device_desc, device_mount_point, device_key_size, image_id)
		if not xml_result:
			logging.error("call updateDevice return False")
			return False

		xml_result = broker_api_lib.encryptDevice(device_msuid)
		if not xml_result:
			logging.error("call encryptDevice return False")
			return False

		simulator_lib.encrypt_device(config_name, image_id, [device_id])

		simulator_lib.create_instance(config_name, image_id, instance_id)

		dkr_id = broker_api_lib.get_dkr_id_from_instance_id(instance_id)
		if not dkr_id:
			logging.error("instance msuid is not found")
			return False
	else:
		dkr_id = new_dkr_id


	xml_result = broker_api_lib.listAllRuleResults(dkr_id)
	if not xml_result:
		logging.error("call listAllRuleResults return False")
		return False

	"""
	To-Do : validate result
	sg_rule_type_node = xml_result.getElementsByTagName("securityRuleType")[0]

	if sg_rule_type_node:
		return True
	else:
		return False
	"""

	return True


def listLimitedRuleResults(new_dkr_id, rule_pattern, create_instance=False):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")

	if create_instance:
		config_name="listLimitedRuleResults"
		csp_provider="listLimitedRuleResults_csp"
		csp_zone="listLimitedRuleResults_zone"
		image_id="listLimitedRuleResults_image"
		device_id="listLimitedRuleResults_device"
		device_id_list=[device_id]

		instance_id="listLimitedRuleResults_instance"

		simulator_lib.create_config(config_name, csp_provider, csp_zone, image_id, device_id_list)
		simulator_lib.upload_inventory(config_name, image_id)

		device_msuid = broker_api_lib.get_device_msuid_from_device_id(device_id)
		if not device_msuid:
			logging.error("Failed to get source device msuid")
			return False


		#configure device
		device_name=device_id
		device_os="windows"
		device_fs="ntfs"
		write_permission="true"
		device_desc="this is listLimitedRuleResults"
		device_mount_point="H"
		device_key_size="128"
		xml_result = broker_api_lib.updateDevice(device_msuid, device_id, device_name, device_os, device_fs, write_permission, device_desc, device_mount_point, device_key_size, image_id)
		if not xml_result:
			logging.error("call updateDevice return False")
			return False

		xml_result = broker_api_lib.encryptDevice(device_msuid)
		if not xml_result:
			logging.error("call encryptDevice return False")
			return False

		simulator_lib.encrypt_device(config_name, image_id, [device_id])

		simulator_lib.create_instance(config_name, image_id, instance_id)

		dkr_id = broker_api_lib.get_dkr_id_from_instance_id(instance_id)
		if not dkr_id:
			logging.error("instance msuid is not found")
			return False
	else:
		dkr_id = new_dkr_id



	xml_result = broker_api_lib.listLimitedRuleResults(dkr_id, rule_pattern)
	if not xml_result:
		logging.error("call listLimitedRuleResults return False")
		return False


	"""
	To-Do : validate result
	sg_rule_type_node = xml_result.getElementsByTagName("securityRuleType")[0]

	if sg_rule_type_node:
		return True
	else:
		return False
	"""

	return True



if __name__ == '__main__':

	#staring point


	#print flatRequests()

	# --------------------------------------
	
	#instance_id = "getInstance_instance"

	#instance_id = ""
	# HTTP Error 400: Bad Request

	#instance_id = "00000000-0000-0000-0000-000000000000"
	# http 400 bad request

	#instance_id = mapi_util.random_str(36)
	# http 400 bad request

	#print getInstance(instance_id)

	# --------------------------------------

	#dkr_id = ""
	# HTTP Error 404: Not Found

	#dkr_id = "00000000-0000-0000-0000-000000000000"
	# HTTP Error 400: Bad Request

	#dkr_id = mapi_util.random_str(36)
	# HTTP Error 500: Internal Server Error

	#print getDeviceKeyRequest(dkr_id)

	# --------------------------------------

	"""
	 <xs:enumeration value="approved" /> 
	  <xs:enumeration value="delivered" /> 
	  <xs:enumeration value="pending" /> 
	  <xs:enumeration value="denied" /> 
	  <xs:enumeration value="failure" /> 
	  <xs:enumeration value="expired" /> 
	  <xs:enumeration value="revoking" /> 
	  <xs:enumeration value="revoked" /> 
	  <xs:enumeration value="revoke_ignored" /> 
	"""

	# RAT case
	"""
	dkr_id = "now_used_now"
	dkr_status = "approved"
	print updateDeviceKeyRequest(dkr_id, dkr_status, True)
	"""

	"""
	dkr_id = ""
	dkr_status = "approved"
	# HTTP Error 404: Not Found
	print updateDeviceKeyRequest(dkr_id, dkr_status)
	"""

	"""
	dkr_id = "00000000-0000-0000-0000-000000000000"
	dkr_status = "approved"
	# fail,HTTP Error 500: Internal Server Error
	print updateDeviceKeyRequest(dkr_id, dkr_status)
	"""
	
	"""
	dkr_id = mapi_util.random_str(36)
	dkr_status = "approved"
	# HTTP Error 500: Internal Server Error
	print updateDeviceKeyRequest(dkr_id, dkr_status)
	"""

	"""
	dkr_id = "now_used_now"
	dkr_status = ""
	# result:fail,HTTP Error 500: There is an error in XML document (1, 282).
	print updateDeviceKeyRequest(dkr_id, dkr_status, True)
	"""

	"""
	dkr_id = "now_used_now"
	dkr_status = "APPROVED"
	# dkr_status = "APPROVED", case sensitive
	# result:fail,HTTP Error 500: There is an error in XML document (1, 290).
	print updateDeviceKeyRequest(dkr_id, dkr_status, True)
	"""

	"""
	dkr_id = "now_used_now"
	dkr_status = mapi_util.random_str(20)
	# dkr_status = mapi_util.random_str(20)
	# result:fail,HTTP Error 500: There is an error in XML document (1, 302).
	print updateDeviceKeyRequest(dkr_id, dkr_status, True)
	"""

	"""
	# pending -> delivered
	dkr_id = "now_used_now"
	dkr_status = "delivered"
	# result:fail,HTTP Error 400: Bad Request
	print updateDeviceKeyRequest(dkr_id, dkr_status, True)
	"""

	"""
	# pending -> denied
	dkr_id = "now_used_now"
	dkr_status = "denied"
	# result:ok
	print updateDeviceKeyRequest(dkr_id, dkr_status, True)
	"""

	"""
	# pending -> failure
	dkr_id = "now_used_now"
	dkr_status = "failure"
	# result:fail,HTTP Error 400: Bad Request
	print updateDeviceKeyRequest(dkr_id, dkr_status, True)
	"""

	"""
	# pending -> expired
	dkr_id = "now_used_now"
	dkr_status = "expired"
	# result:fail,HTTP Error 400: Bad Request
	print updateDeviceKeyRequest(dkr_id, dkr_status, True)
	"""

	"""
	# pending -> revoking
	dkr_id = "now_used_now"
	dkr_status = "revoking"
	# result:fail,HTTP Error 400: Bad Request
	print updateDeviceKeyRequest(dkr_id, dkr_status, True)
	"""

	"""
	# pending -> revoked
	dkr_id = "now_used_now"
	dkr_status = "revoked"
	# result:fail,HTTP Error 500: Internal Server Error
	print updateDeviceKeyRequest(dkr_id, dkr_status, True)
	"""

	"""
	# pending -> revoke_ignored
	dkr_id = "now_used_now"
	dkr_status = "revoke_ignored"
	# result:fail,HTTP Error 500: Internal Server Error
	print updateDeviceKeyRequest(dkr_id, dkr_status, True)
	"""

	"""
	# pending -> approved -> delivered
	dkr_id = "now_used_now"
	dkr_status = "approved"
	second_status = "delivered"
	# result:fail,HTTP Error 400: Bad Request
	print updateDeviceKeyRequest(dkr_id, dkr_status, True, second_status)
	"""

	"""
	# pending -> approved -> pending
	dkr_id = "now_used_now"
	dkr_status = "approved"
	second_status = "pending"
	# result:fail,HTTP Error 400: Bad Request
	print updateDeviceKeyRequest(dkr_id, dkr_status, True, second_status)
	"""

	"""
	# pending -> approved -> denied
	dkr_id = "now_used_now"
	dkr_status = "approved"
	second_status = "denied"
	# result:ok
	print updateDeviceKeyRequest(dkr_id, dkr_status, True, second_status)
	"""

	"""
	# pending -> approved -> failure
	dkr_id = "now_used_now"
	dkr_status = "approved"
	second_status = "failure"
	# result:fail,HTTP Error 400: Bad Request
	print updateDeviceKeyRequest(dkr_id, dkr_status, True, second_status)
	"""

	"""
	# pending -> approved -> expired
	dkr_id = "now_used_now"
	dkr_status = "approved"
	second_status = "expired"
	# result:fail,HTTP Error 400: Bad Request
	print updateDeviceKeyRequest(dkr_id, dkr_status, True, second_status)
	"""

	"""
	# pending -> approved -> revoking
	dkr_id = "now_used_now"
	dkr_status = "approved"
	second_status = "revoking"
	# result:fail,HTTP Error 400: Bad Request
	print updateDeviceKeyRequest(dkr_id, dkr_status, True, second_status)
	"""

	"""
	# pending -> approved -> revoked
	dkr_id = "now_used_now"
	dkr_status = "approved"
	second_status = "revoked"
	# result:fail,HTTP Error 500: Internal Server Error
	print updateDeviceKeyRequest(dkr_id, dkr_status, True, second_status)
	"""

	"""
	# pending -> approved -> revoke_ignored
	dkr_id = "now_used_now"
	dkr_status = "approved"
	second_status = "revoke_ignored"
	# result:fail,HTTP Error 500: Internal Server Error
	print updateDeviceKeyRequest(dkr_id, dkr_status, True, second_status)
	"""

	"""
	# pending -> denied -> approved
	dkr_id = "now_used_now"
	dkr_status = "denied"
	second_status = "approved"
	# result:ok
	print updateDeviceKeyRequest(dkr_id, dkr_status, True, second_status)
	"""

	"""
	# pending -> denied -> delivered
	dkr_id = "now_used_now"
	dkr_status = "denied"
	second_status = "delivered"
	# result:fail,HTTP Error 400: Bad Request
	print updateDeviceKeyRequest(dkr_id, dkr_status, True, second_status)
	"""

	"""
	# pending -> denied -> pending
	dkr_id = "now_used_now"
	dkr_status = "denied"
	second_status = "pending"
	# result:fail,HTTP Error 400: Bad Request
	print updateDeviceKeyRequest(dkr_id, dkr_status, True, second_status)
	"""

	"""
	# pending -> denied -> failure
	dkr_id = "now_used_now"
	dkr_status = "denied"
	second_status = "failure"
	# result:fail,HTTP Error 400: Bad Request
	print updateDeviceKeyRequest(dkr_id, dkr_status, True, second_status)
	"""

	"""
	# pending -> denied -> expired
	dkr_id = "now_used_now"
	dkr_status = "denied"
	second_status = "expired"
	# result:fail,HTTP Error 400: Bad Request
	print updateDeviceKeyRequest(dkr_id, dkr_status, True, second_status)
	"""

	"""
	# pending -> denied -> revoking
	dkr_id = "now_used_now"
	dkr_status = "denied"
	second_status = "revoking"
	# result:fail,HTTP Error 400: Bad Request
	print updateDeviceKeyRequest(dkr_id, dkr_status, True, second_status)
	"""

	"""
	# pending -> denied -> revoked
	dkr_id = "now_used_now"
	dkr_status = "denied"
	second_status = "revoked"
	# result:fail,HTTP Error 500: Internal Server Error
	print updateDeviceKeyRequest(dkr_id, dkr_status, True, second_status)
	"""

	"""
	# pending -> denied -> revoke_ignored
	dkr_id = "now_used_now"
	dkr_status = "denied"
	second_status = "revoke_ignored"
	# result:fail,HTTP Error 500: Internal Server Error
	print updateDeviceKeyRequest(dkr_id, dkr_status, True, second_status)
	"""


	# --------------------------------------
	
	#dkr_id = ""
	# HTTP Error 404: Not Found

	#dkr_id = "00000000-0000-0000-0000-000000000000"
	# ok, bug should check existing or not

	#dkr_id = mapi_util.random_str(36)
	# HTTP Error 500: Internal Server Error
	
	#print listAllRuleResults(dkr_id)

	# --------------------------------------
	
	"""
	Param[1] = PFI
	Param[1] = NFPI
	Param[1] = NFI
	"""

	"""
	rule_pattern = "NPFI"
	dkr_id = "listLimitedRuleResults_instance"
	#result: ok	
	print listLimitedRuleResults(dkr_id, rule_pattern, True)
	"""

	"""	
	dkr_id = ""
	rule_pattern = "NPFI"
	# HTTP Error 500: Internal Server Error
	print listLimitedRuleResults(dkr_id, rule_pattern)
	"""

	"""
	dkr_id = "00000000-0000-0000-0000-000000000000"
	rule_pattern = "NPFI"
	# result:ok, bug should check existing or not
	print listLimitedRuleResults(dkr_id, rule_pattern)
	"""

	"""
	dkr_id = mapi_util.random_str(36)
	rule_pattern = "NPFI"
	# result:HTTP Error 500: Internal Server Error
	print listLimitedRuleResults(dkr_id, rule_pattern)
	"""

	"""
	dkr_id = "not_used_now"
	rule_pattern = "N"
	# result:ok
	print listLimitedRuleResults(dkr_id, rule_pattern, True)
	"""

	"""
	dkr_id = "not_used_now"
	rule_pattern = "P"
	# result:ok
	print listLimitedRuleResults(dkr_id, rule_pattern, True)
	"""

	"""
	dkr_id = "not_used_now"
	rule_pattern = "F"
	# result:ok
	print listLimitedRuleResults(dkr_id, rule_pattern, True)
	"""

	"""
	dkr_id = "not_used_now"
	rule_pattern = "I"
	# result:ok
	print listLimitedRuleResults(dkr_id, rule_pattern, True)
	"""

	"""
	dkr_id = "not_used_now"
	rule_pattern = "NPFI"
	# result:ok
	print listLimitedRuleResults(dkr_id, rule_pattern, True)
	"""

	"""
	dkr_id = "not_used_now"
	rule_pattern = ""
	# result:ok, same as NPFI
	print listLimitedRuleResults(dkr_id, rule_pattern, True)
	"""

	"""
	dkr_id = "not_used_now"
	rule_pattern = "ZZ"
	# result:ok, same as N
	print listLimitedRuleResults(dkr_id, rule_pattern, True)
	"""

	"""
	dkr_id = "not_used_now"
	rule_pattern = "pfi"
	# result:ok, not case sensitive
	print listLimitedRuleResults(dkr_id, rule_pattern, True)
	"""