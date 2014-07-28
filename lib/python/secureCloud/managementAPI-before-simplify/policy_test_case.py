import time
import mapi_lib
import logging
import mapi_util
import mapi_config
import simulator_lib

"""
logging = logging.getLogger('loggingger')
logging.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(levelname)s][%(filename)s][%(funcName)s][%(lineno)d]-%(message)s ')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
logging.addHandler(handler)
"""

logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)


def listAllSecurityRules():
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")

	xml_result = broker_api_lib.listAllSecurityRules()
	if not xml_result:
		logging.debug("call listAllSecurityRules return False")
		return False

	sg_rule_nodes = xml_result.getElementsByTagName("SecurityRuleTypeList")[0]
	sg_rule_type_nodes = sg_rule_nodes.getElementsByTagName("securityRuleType")

	import mapi_config

	if len(sg_rule_type_nodes) <> len(mapi_config.rule_mapping):
		logging.debug("Result security groups size is not as expected")
		return False


	for sg_rule_type_node in sg_rule_type_nodes:
		policy_name = sg_rule_type_node.attributes["name"].value.strip()
		policy_id = sg_rule_type_node.attributes["id"].value.strip()

		if mapi_config.rule_mapping[policy_name] <> policy_id:
			logging.debug("security rule ID or name is not matched")
			return False

	return True


def getSecurityRule(sr_id):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")

	xml_result = broker_api_lib.getSecurityRule(sr_id)
	if not xml_result:
		logging.debug("call getSecurityRule return False")
		return False

	"""
	sg_rule_type_node = xml_result.getElementsByTagName("securityRuleType")[0]

	if sg_rule_type_node:
		return True
	else:
		logging.debug("rule:%s is not found" % (sr_id))
		return False
	"""

def listAllSecurityGroups(policy_name):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	xml_result = broker_api_lib.listAllSecurityGroups()
	if not xml_result:
		logging.debug("call listAllSecurityGroups return False")
		return False
	
	policy_list = xml_result.getElementsByTagName("securityGroupList")[0]
	policies = policy_list.getElementsByTagName("securityGroup")
	for policy in policies:
		if policy_name == policy.attributes["name"].value.strip():
			return True

	logging.debug("cannot find default policy")
	return False


def getSecurityGroup(policy_id):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")

	"""
	policy_id = broker_api_lib.get_policy_id_from_policy_name(policy_name)
	if not policy_id:
		logging.debug("cannot find the policy ID")
		return False
	"""

	xml_result = broker_api_lib.getSecurityGroup(policy_id)
	if not xml_result:
		logging.debug("call getSecurityGroup return False")
		return False


	"""
	policy = xml_result.getElementsByTagName("securityGroup")[0]
	if policy_name == policy.attributes["name"].value.strip():
		return True
	else:
		logging.debug("fail to find the default policy")
		return False
	"""



# ToDo: for now support only auto-create 1 image with many devices
# device to be included in the policy has to be encrypted

# empty image and device, faster
def createSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					device_id_list,image_id_list, security_rule_list, upload_inventory=False, formatted_security_rule_list=None):

	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")

	# check if policy is created
	policy_id = broker_api_lib.get_policy_id_from_policy_name(policy_name)

	if policy_id:
		#delete policy
		xml_result = broker_api_lib.deleteSecurityGroup(policy_id)
		if not xml_result:
			logging.debug("call deleteSecurityGroup return False")
			return False

	if upload_inventory:

		#upload and encrypt device for policy test
		config_name="createSecurityGroup"
		csp_provider="createSecurityGroup_csp"
		csp_zone="createSecurityGroup_zone"
		image_id=image_id_list[0]

		simulator_lib.create_config(config_name, csp_provider, csp_zone, image_id, device_id_list)
		simulator_lib.upload_inventory(config_name, image_id)

		device_id = device_id_list[0]
		device_msuid = broker_api_lib.get_device_msuid_from_device_id(device_id)
		if not device_msuid:
			logging.debug("Failed to get source device msuid")
			return False


		#configure device
		device_name=device_id
		device_os="windows"
		device_fs="ntfs"
		write_permission="true"
		device_desc="this is createSecurityGroup"
		device_mount_point="H"
		device_key_size="128"
		xml_result = broker_api_lib.updateDevice(device_msuid, device_id, device_name, device_os, device_fs, write_permission, device_desc, device_mount_point, device_key_size, image_id)
		if not xml_result:
			logging.debug("call updateDevice return False")
			return False

		xml_result = broker_api_lib.encryptDevice(device_msuid)
		if not xml_result:
			logging.debug("call encryptDevice return False")
			return False

		simulator_lib.encrypt_device(config_name, image_id, [device_id])

	
	# create policy
	xml_result = broker_api_lib.createSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					device_id_list,image_id_list, security_rule_list, formatted_security_rule_list=formatted_security_rule_list)
	if not xml_result:
		logging.debug("call createSecurityGroup return False")
		return False

	# check if policy is created
	policy_id = broker_api_lib.get_policy_id_from_policy_name(policy_name)


	xml_result = broker_api_lib.getSecurityGroup(policy_id)
	if not xml_result:
		logging.debug("call getSecurityGroup return False")
		return False


	return True



def updateSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					new_device_id_list, new_image_id_list, security_rule_list, upload_inventory=False, formatted_security_rule_list=None):
	
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")

	# check if policy is created
	policy_id = broker_api_lib.get_policy_id_from_policy_name(policy_name)

	if policy_id:
		#delete policy
		xml_result = broker_api_lib.deleteSecurityGroup(policy_id)
		if not xml_result:
			logging.debug("call deleteSecurityGroup return False")
			return False


	#upload and encrypt device for policy test
	config_name="updateSecurityGroup_orig"
	csp_provider="updateSecurityGroup_orig_csp"
	csp_zone="updateSecurityGroup_orig_zone"
	device_id_list=["updateSecurityGroup_orig_device1"]
	image_id_list=["updateSecurityGroup_orig_image"]
	image_id=image_id_list[0]
		
	if upload_inventory:

		simulator_lib.create_config(config_name, csp_provider, csp_zone, image_id, device_id_list)
		simulator_lib.upload_inventory(config_name, image_id)

		device_id = device_id_list[0]
		device_msuid = broker_api_lib.get_device_msuid_from_device_id(device_id)
		if not device_msuid:
			logging.debug("Failed to get source device msuid")
			return False

		#configure device
		device_name=device_id
		device_os="windows"
		device_fs="ntfs"
		write_permission="true"
		device_desc="this is before update"
		device_mount_point="H"
		device_key_size="128"
		xml_result = broker_api_lib.updateDevice(device_msuid, device_id, device_name, device_os, device_fs, write_permission, device_desc, device_mount_point, device_key_size, image_id)
		if not xml_result:
			logging.debug("call updateDevice return False")
			return False

		xml_result = broker_api_lib.encryptDevice(device_msuid)
		if not xml_result:
			logging.debug("call encryptDevice return False")
			return False

		simulator_lib.encrypt_device(config_name, image_id, [device_id])


	EnableIC_orig="false"
	ICAction_orig="Nothing"
	PostponeEnable_orig="false"
	RevokeIntervalNumber_orig="1"
	RevokeIntervalType_orig="Hour"
	policy_name_orig="mapi_test"
	isResourcePool_orig="false"
	description_orig="this is before update"
	successAction_orig="ManualApprove"
	successActionDelay_orig="20"
	failAction_orig="Deny"
	failActionDelay_orig="1"
	security_rule_list_orig=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]


	# create policy
	xml_result = broker_api_lib.createSecurityGroup(EnableIC_orig, ICAction_orig, PostponeEnable_orig, RevokeIntervalNumber_orig, \
					RevokeIntervalType_orig, policy_name_orig, isResourcePool_orig, description_orig, \
					successAction_orig, successActionDelay_orig, failAction_orig, failActionDelay_orig, \
					device_id_list,image_id_list, security_rule_list_orig)
	if not xml_result:
		logging.debug("call createSecurityGroup return False")
		return Fals


	# find if there is such policy existing
	policy_id = broker_api_lib.get_policy_id_from_policy_name(policy_name_orig)
	if not policy_id:
		logging.debug("policy is not found after create")
		return False



	#create another device for policy update
	#upload and encrypt device for policy test
	config_name="updateSecurityGroup"
	csp_provider="updateSecurityGroup_csp"
	csp_zone="updateSecurityGroup_zone"
	image_id_list = new_image_id_list
	device_id_list = new_device_id_list
	image_id=image_id_list[0]

	if upload_inventory:
		simulator_lib.create_config(config_name, csp_provider, csp_zone, image_id, device_id_list)
		simulator_lib.upload_inventory(config_name, image_id)

		device_id = device_id_list[0]
		device_msuid = broker_api_lib.get_device_msuid_from_device_id(device_id)
		if not device_msuid:
			logging.debug("Failed to get source device msuid")
			return False


		#configure device
		device_name=device_id
		device_os="windows"
		device_fs="ntfs"
		write_permission="true"
		device_desc="after update policy"
		device_mount_point="H"
		device_key_size="128"
		xml_result = broker_api_lib.updateDevice(device_msuid, device_id, device_name, device_os, device_fs, write_permission, device_desc, device_mount_point, device_key_size, image_id)
		if not xml_result:
			logging.debug("call updateDevice return False")
			return False

		xml_result = broker_api_lib.encryptDevice(device_msuid)
		if not xml_result:
			logging.debug("call encryptDevice return False")
			return False

		simulator_lib.encrypt_device(config_name, image_id, [device_id])



	# update policy
	xml_result = broker_api_lib.updateSecurityGroup(policy_id, EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					new_device_id_list,new_image_id_list, security_rule_list, formatted_security_rule_list=formatted_security_rule_list)
	if not xml_result:
		logging.debug("call updateSecurityGroup return False")
		return False


	xml_result = broker_api_lib.getSecurityGroup(policy_id)
	if not xml_result:
		logging.debug("call getSecurityGroup return False")
		return False

	current_policy = xml_result.getElementsByTagName("securityGroup")[0]
	
	result = broker_api_lib.compare_policy(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					new_device_id_list,new_image_id_list, security_rule_list, current_policy, formatted_security_rule_list)


	if result:
		return True
	else:
		logging.debug("Values are not the same after update")



def deleteSecurityGroup(policy_id):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	#delete policy
	xml_result = broker_api_lib.deleteSecurityGroup(policy_id)
	if not xml_result:
		logging.debug("call deleteSecurityGroup return False")
		return False

	return True

	"""
	policy_id = broker_api_lib.get_policy_id_from_policy_name(policy_name)
	if not policy_id:
		return True
	else:
		logging.debug("policy still existing after deleting")
		return False
	"""

def getSecurityGroupSetting():
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	xml_result = broker_api_lib.getSecurityGroupSetting()
	if not xml_result:
		logging.debug("call getSecurityGroupSetting return False")
		return False

	#todo check settings	
	sg_setting = xml_result.getElementsByTagName("securityGroupSetting")[0]

	result = broker_api_lib.validate_SecurityGroupSetting(sg_setting)

	if result:
		return True
	else:
		logging.error("security setting is not found")
		return False


def putSecurityGroupSetting(scheduleType,
							scheduleIntervalTime,
							scheduleIntervalPeriod,
							scheduleIntervalDay,
							reAttemptInterval,
							reAttemptIntervalType,
							reAttemptICRepeat):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	xml_result = broker_api_lib.putSecurityGroupSetting(scheduleType,
														scheduleIntervalTime,
														scheduleIntervalPeriod,
														scheduleIntervalDay,
														reAttemptInterval,
														reAttemptIntervalType,
														reAttemptICRepeat)
	if not xml_result:
		logging.debug("call putSecurityGroupSetting return False")
		return False

	"""
	xml_result = broker_api_lib.getSecurityGroupSetting()
	if not xml_result:
		logging.debug("call getSecurityGroupSetting return False")
		return False

	#todo check settings	
	sg_setting = xml_result.getElementsByTagName("securityGroupSetting")[0]
	current_scheduleType = sg_setting.attributes["ScheduleType"].value.strip()
	current_scheduleIntervalTime = sg_setting.attributes["ScheduleIntervalTime"].value.strip()
	current_scheduleIntervalPeriod = sg_setting.attributes["ScheduleIntervalPeriod"].value.strip()
	current_scheduleIntervalDay = sg_setting.attributes["ScheduleIntervalDay"].value.strip()
	current_reAttemptInterval = sg_setting.attributes["ReAttemptInterval"].value.strip()
	current_reAttemptIntervalType = sg_setting.attributes["ReAttemptIntervalType"].value.strip()
	current_reAttemptICRepeat = sg_setting.attributes["ReAttemptICRepeat"].value.strip()

	if (scheduleType == current_scheduleType and \
	scheduleIntervalTime == current_scheduleIntervalTime and \
	scheduleIntervalPeriod == current_scheduleIntervalPeriod and \
	scheduleIntervalDay == current_scheduleIntervalDay and \
	reAttemptInterval == current_reAttemptInterval and \
	reAttemptIntervalType == current_reAttemptIntervalType):
	#reAttemptICRepeat won't be updated, so don't compare 
	#reAttemptICRepeat == current_reAttemptICRepeat):
		is_the_same = True
	else:
		logging.debug("some values are not the same after update")
		is_the_same = False

	scheduleType="Daily"
	scheduleIntervalTime="1:00:00"
	scheduleIntervalPeriod="PM"
	scheduleIntervalDay="Sun"
	reAttemptInterval="30"
	reAttemptIntervalType="minutes"
	reAttemptICRepeat="100"
	xml_result = broker_api_lib.putSecurityGroupSetting(scheduleType,
														scheduleIntervalTime,
														scheduleIntervalPeriod,
														scheduleIntervalDay,
														reAttemptInterval,
														reAttemptIntervalType,
														reAttemptICRepeat)
	if not xml_result:
		logging.debug("fail to change security group setting back")
		return False

	if is_the_same:
		return True
	else:
		return False
	"""

	return True



if __name__ == '__main__':

	rule_mapping ={"Device Access Type":"5d14057d-3277-4ab9-9d3e-e808acbb9c65",
				  "Device Mount Point":"c91f0521-a6cc-4e78-bb37-4a41dc378d3c",
				   "Key Request Date":"1338779b-2683-474b-a9a7-298176564a6f",
				   "Request Source IP Address":"cc0e1bfb-c670-44d1-8b83-f44d351d5285",
				   "Request Source IPv6 Address":"d6f008eb-a11b-4cb6-8cb0-63c056d27009",
				   "Instance First Seen":"4b4390c1-af4e-4c37-9ad0-24b26be2366d",
				   "Instance User Data":"e541d7c1-b681-4221-a2c0-68bfd87debaa",
				   "Instance Location":"b1ad7471-cb8b-4a78-bb56-efcb235ef1ba",
				   "OSSEC Version":"9c36a9d2-ff26-47c4-8cfa-180630c97efb",
				   "Trend Micro softwares":"6fbc0f33-d430-4a46-9b03-1dbb172c6509",
				   "Trend Micro Virus Scan Engine":"297d4d3b-c269-43d9-ad9e-6fef86fdfe5c",
				   "Trend Micro Virus Scan Pattern":"ed30599c-13c3-4fb3-ac30-2a38c0b5e45c",
				   "Guest OS Type":"e3e68188-b5b2-4e31-bcce-c4cb43d46a55",
				   "Guest OS Architecture":"b2ee4872-631b-4f57-aaff-e222cfadf588",
				   "Network Services":"0f938a58-cd0a-4dc0-b0ec-034fff98ec1a",
				   "Deep Security Status":"964ed53f-dd7c-43c6-aec5-b64df1474ff3",
				   "Deep Security Anti-Malware Status":"cfd65596-9071-4fd6-a7c5-da368d1bf3d8",
				   "Deep Security Web Reputation Status":"9637d366-95e5-4dcf-ac0a-703439aec8e9",
				   "Deep Security Firewall Status":"eaeadd52-f0a9-4f16-a293-647ef2ccd10e",
				   "Deep Security DPI Status":"c63d23e3-d00f-4ea9-a932-00086c3cb5a1",
				   "Deep Security Integrity Monitoring Status":"b64c389e-8cd9-401a-a149-28bf95154fd1",
				   "Deep Security Log Inspection Status":"de6017a8-e3a1-4a42-93bd-6aa7e783a765"}

	# -------------------------------------


	#print listAllSecurityRules()

	# -------------------------------------

	sg_id = rule_mapping["Instance First Seen"]
	#print getSecurityRule(sg_id)

	sg_id = ""
	#print getSecurityRule(sg_id)
	# empty sg_id return the whole security rule list

	sg_id = "00000000-0000-0000-0000-000000000000"
	#print getSecurityRule(sg_id)
	# http 400 bad request

	sg_id = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
	#print getSecurityRule(sg_id)
	# http 400 bad request

	sg_id = "asdfsdf5sd4f564sdf56as4df56a"
	#print getSecurityRule(sg_id)
	# http 400 bad request

	# -------------------------------------

	policy_name = "Default Policy"
	#print listAllSecurityGroups(policy_name)

	"""
	To-Do:
	test large with pagination
	"""

	# -------------------------------------

	policy_id = ""
	#print getSecurityGroup(policy_id)
	#return whole policy list

	policy_id = "00000000-0000-0000-0000-000000000000"
	#print getSecurityGroup(policy_id)
	#return http 400 bad request, Policy Invalid GUID ---> TMEG.Cloud9.Exceptions.DatabaseException: Data Error: -1301

	policy_id = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
	#print getSecurityGroup(policy_id)
	#return http 400 bad request

	policy_id = "asdfsdf5sd4f564sdf56as4df56a"
	#print getSecurityGroup(policy_id)
	#return http 400 bad request
	
	# -------------------------------------



	# EnableIC="false"
	# ICAction, PostponeEnable, RevokeIntervalNumber, RevokeIntervalType are still saved
	"""
	EnableIC="false"

	ICAction="Revoke"

	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"

	policy_name="mapi_test"
	isResourcePool="false"
	description="this is mapi test"
	successAction="Approve"
	successActionDelay=""
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""


	# EnableIC=""
	# result: empty default to false
	# ICAction, PostponeEnable, RevokeIntervalNumber, RevokeIntervalType are still saved
	"""
	EnableIC=""

	ICAction="Nothing"
	# even action is nothing, the following values are still updated
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"

	policy_name="mapi_test"
	isResourcePool="false"
	description="this is mapi test"
	successAction="Approve"
	successActionDelay=""
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""


	# EnableIC="asdfasdfasdfasdf"
	# result: HTTP Error 500: There is an error in XML document (5, 57).
	# ICAction, PostponeEnable, RevokeIntervalNumber, RevokeIntervalType are still saved
	"""
	EnableIC="asdfasdfasdfasdf"

	ICAction="Nothing"
	# even action is nothing, the following values are still updated
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"

	policy_name="mapi_test"
	isResourcePool="false"
	description="this is mapi test"
	successAction="Approve"
	successActionDelay=""
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""
	

	# EnableIC="false" and empty ICAction, PostponeEnable, RevokeIntervalNumber, RevokeIntervalType
	# result: ok
	# ICAction="Nothing", PostponeEnable="false", RevokeIntervalNumber="0", RevokeIntervalType="Hour"
	"""
	EnableIC="false"

	ICAction=""
	# even action is nothing, the following values are still updated
	PostponeEnable=""
	RevokeIntervalNumber=""
	RevokeIntervalType=""

	policy_name="mapi_test"
	isResourcePool="false"
	description="this is mapi test"
	successAction="Approve"
	successActionDelay=""
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""



	# EnableIC="true"
	# result: ok
	"""
	EnableIC="true"

	ICAction="Revoke"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"

	policy_name="mapi_test"
	isResourcePool="false"
	description="this is mapi test"
	successAction="Approve"
	successActionDelay=""
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""



	# ICAction="Revoke"
	# result: ok
	"""
	EnableIC="true"

	ICAction="Revoke"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"

	policy_name="mapi_test"
	isResourcePool="false"
	description="this is mapi test"
	successAction="Approve"
	successActionDelay=""
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""
	

	# ICAction="Nothing"
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"

	policy_name="mapi_test"
	isResourcePool="false"
	description="this is mapi test"
	successAction="Approve"
	successActionDelay=""
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""


	# ICAction=""
	# result: ok, default to false
	"""
	EnableIC="true"

	ICAction=""
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"

	policy_name="mapi_test"
	isResourcePool="false"
	description="this is mapi test"
	successAction="Approve"
	successActionDelay=""
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""



	# ICAction=random 20 chars
	# result: HTTP Error 500: There is an error in XML document (5, 57).
	"""
	EnableIC="true"

	ICAction=mapi_util.random_str(20)
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"

	policy_name="mapi_test"
	isResourcePool="false"
	description="this is mapi test"
	successAction="Approve"
	successActionDelay=""
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""



	# PostponeEnable="true"
	# result: ok
	"""
	EnableIC="true"

	ICAction="Revoke"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"

	policy_name="mapi_test"
	isResourcePool="false"
	description="this is mapi test"
	successAction="Approve"
	successActionDelay=""
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""

	# PostponeEnable="false"
	# result: ok
	"""
	EnableIC="true"

	ICAction="Revoke"
	PostponeEnable="false"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"

	policy_name="mapi_test"
	isResourcePool="false"
	description="this is mapi test"
	successAction="Approve"
	successActionDelay=""
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""

	# PostponeEnable=""
	# result: ok
	"""
	EnableIC="true"

	ICAction="Revoke"
	PostponeEnable=""
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"

	policy_name="mapi_test"
	isResourcePool="false"
	description="this is mapi test"
	successAction="Approve"
	successActionDelay=""
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""

	# PostponeEnable="aaaa"
	# result: HTTP Error 500: There is an error in XML document (5, 57).
	"""
	EnableIC="true"

	ICAction="Revoke"
	PostponeEnable="aaaa"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"

	policy_name="mapi_test"
	isResourcePool="false"
	description="this is mapi test"
	successAction="Approve"
	successActionDelay=""
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""


	# RevokeIntervalNumber="-1"
	# result: OK but really OK??
	"""
	EnableIC="true"

	ICAction="Revoke"
	PostponeEnable="true"
	RevokeIntervalNumber="-1"
	RevokeIntervalType="Hour"

	policy_name="mapi_test"
	isResourcePool="false"
	description="this is mapi test"
	successAction="Approve"
	successActionDelay=""
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""

	# RevokeIntervalNumber="aaaa"
	# HTTP Error 500: There is an error in XML document (5, 57).
	"""
	EnableIC="true"

	ICAction="Revoke"
	PostponeEnable="true"
	RevokeIntervalNumber="aaaa"
	RevokeIntervalType="Hour"

	policy_name="mapi_test"
	isResourcePool="false"
	description="this is mapi test"
	successAction="Approve"
	successActionDelay=""
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""


	# RevokeIntervalNumber="2147483647"
	# ok
	"""
	EnableIC="true"

	ICAction="Revoke"
	PostponeEnable="true"
	RevokeIntervalNumber="2147483647"
	RevokeIntervalType="Hour"

	policy_name="mapi_test"
	isResourcePool="false"
	description="this is mapi test"
	successAction="Approve"
	successActionDelay=""
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""
	

	# RevokeIntervalNumber="2147483648" 2147483647+1
	# HTTP Error 500: There is an error in XML document (5, 57).
	"""
	EnableIC="true"

	ICAction="Revoke"
	PostponeEnable="true"
	RevokeIntervalNumber="2147483648"
	RevokeIntervalType="Hour"

	policy_name="mapi_test"
	isResourcePool="false"
	description="this is mapi test"
	successAction="Approve"
	successActionDelay=""
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""
	

	# RevokeIntervalType="Hour"
	# result: ok
	"""
	EnableIC="true"

	ICAction="Revoke"
	PostponeEnable="true"
	RevokeIntervalNumber="-50"
	RevokeIntervalType="Hour"

	policy_name="mapi_test"
	isResourcePool="false"
	description="this is mapi test"
	successAction="Approve"
	successActionDelay=""
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""
	

	# RevokeIntervalType="Minute"
	# result: ok
	"""
	EnableIC="true"

	ICAction="Revoke"
	PostponeEnable="true"
	RevokeIntervalNumber="-50"
	RevokeIntervalType="Minute"

	policy_name="mapi_test"
	isResourcePool="false"
	description="this is mapi test"
	successAction="Approve"
	successActionDelay=""
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""

	# RevokeIntervalType="Day"
	# result: ok
	"""
	EnableIC="true"

	ICAction="Revoke"
	PostponeEnable="true"
	RevokeIntervalNumber="-50"
	RevokeIntervalType="Day"

	policy_name="mapi_test"
	isResourcePool="false"
	description="this is mapi test"
	successAction="Approve"
	successActionDelay=""
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""


	# RevokeIntervalType=""
	# result: ok, will default to Hour
	"""
	EnableIC="true"

	ICAction="Revoke"
	PostponeEnable="true"
	RevokeIntervalNumber="50"
	RevokeIntervalType=""

	policy_name="mapi_test"
	isResourcePool="false"
	description="this is mapi test"
	successAction="Approve"
	successActionDelay=""
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""


	# RevokeIntervalType=random 20 chars
	# result: HTTP Error 500: There is an error in XML document (5, 57).
	"""
	EnableIC="true"

	ICAction="Revoke"
	PostponeEnable="true"
	RevokeIntervalNumber="50"
	RevokeIntervalType= mapi_util.random_str(20)

	policy_name="mapi_test"
	isResourcePool="false"
	description="this is mapi test"
	successAction="Approve"
	successActionDelay=""
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""


	# RevokeIntervalType= "HOUR"
	# result: HTTP Error 500: There is an error in XML document (5, 57).
	"""
	EnableIC="true"

	ICAction="Revoke"
	PostponeEnable="true"
	RevokeIntervalNumber="50"
	RevokeIntervalType= "HOUR"

	policy_name="mapi_test"
	isResourcePool="false"
	description="this is mapi test"
	successAction="Approve"
	successActionDelay=""
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""


	# empty image list
	# result: ok
	"""
	EnableIC="true"

	ICAction="Revoke"
	PostponeEnable="true"
	RevokeIntervalNumber="50"
	RevokeIntervalType= "Hour"

	policy_name="mapi_test"
	isResourcePool="false"
	description="this is mapi test"
	successAction="Approve"
	successActionDelay=""
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=[]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""
	

	# not existing image list
	# result: fail, still create the policy?
	# HTTP Error 400: Bad Request
	# TMEG.Cloud9.Exceptions.InvalidResourceIDException: Image Invalid ID ---> TMEG.Cloud9.Exceptions.DatabaseException: Data Error: -402
	"""
	EnableIC="true"

	ICAction="Revoke"
	PostponeEnable="true"
	RevokeIntervalNumber="50"
	RevokeIntervalType= "Hour"

	policy_name="mapi_test"
	isResourcePool="false"
	description="this is mapi test"
	successAction="Approve"
	successActionDelay=""
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["not_existing_img3"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""

	# empty device list
	# result: ok
	"""
	EnableIC="true"

	ICAction="Revoke"
	PostponeEnable="true"
	RevokeIntervalNumber="50"
	RevokeIntervalType= "Hour"

	policy_name="mapi_test"
	isResourcePool="false"
	description="this is mapi test"
	successAction="Approve"
	successActionDelay=""
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=[]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""


	# non-existing device list
	# result: ok
	# HTTP Error 400: Bad Request
	# TMEG.Cloud9.Exceptions.InvalidResourceIDException: Device Invalid ID ---> TMEG.Cloud9.Exceptions.DatabaseException: Data Error: -302
	"""
	EnableIC="true"

	ICAction="Revoke"
	PostponeEnable="true"
	RevokeIntervalNumber="50"
	RevokeIntervalType= "Hour"

	policy_name="mapi_test"
	isResourcePool="false"
	description="this is mapi test"
	successAction="Approve"
	successActionDelay=""
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["non_existing_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""


	# empty policy name
	# http 400, TMEG.Cloud9.Exceptions.ValidationException: request.name: Invalid name.
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"

	policy_name=""
	isResourcePool="false"
	description="this is mapi test"
	successAction="Approve"
	successActionDelay=""
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""

	# policy name=random 32 chars, UI max 32 chars, try 32
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"

	policy_name="1234567890123456789012345679012"
	isResourcePool="false"
	description="this is mapi test"
	successAction="Approve"
	successActionDelay=""
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""


	# policy name=random 32 chars, UI max 32 chars, try 33
	# result: pass

	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"

	policy_name="12345678901234567890123456790123"
	isResourcePool="false"
	description="this is mapi test"
	successAction="Approve"
	successActionDelay=""
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""

	# db max 1024, try 1024
	# result: pass
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"

	policy_name= mapi_util.random_str(1024)
	isResourcePool="false"
	description="this is mapi test"
	successAction="Approve"
	successActionDelay=""
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""

	# db max 1024, try 1025
	# result: pass but extra char is truncated
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"

	
	policy_name= mapi_util.random_str(1025)
	print policy_name
	isResourcePool="false"
	description="this is mapi test"
	successAction="Approve"
	successActionDelay=""
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""


	# empty description
	# result: pass
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"

	
	policy_name = "mapi_test"
	#random_str = mapi_util.random_str(1025)
	isResourcePool="false"
	description= ""
	successAction="Approve"
	successActionDelay=""
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""

	# policy description, UI max 360
	# result: pass
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"

	
	policy_name = "mapi_test"
	random_str = mapi_util.random_str(360)
	isResourcePool="false"
	description= random_str
	successAction="Approve"
	successActionDelay=""
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""

	# policy description, UI max 360+1 = 361
	# result: pass
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"

	
	policy_name = "mapi_test"
	random_str = mapi_util.random_str(361)
	isResourcePool="false"
	description= random_str
	successAction="Approve"
	successActionDelay=""
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""


	# db max 2,147,483,645
	# result: later, exceed current memory
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"

	
	policy_name = "mapi_test"
	random_str = mapi_util.random_str(2147483645)
	isResourcePool="false"
	description= random_str
	successAction="Approve"
	successActionDelay=""
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""


	# description= special char
	# result: ok, but UI not allowed
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"

	
	policy_name = "mapi_test"
	isResourcePool="false"
	description= mapi_util.SPECIAL_CHARS
	successAction="Approve"
	successActionDelay=""
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""

	# successAction= ManualApprove/Approve/Deny
	# successAction="Approve"
	# result: pass, successActionDelay can still be updated
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool="false"
	description= "test description"
	successAction="Approve"
	successActionDelay="30"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""

	# successAction= ManualApprove/Approve/Deny
	# successAction="ManualApprove"
	# result: pass, successActionDelay can still be updated
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool="false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="30"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""



	# successAction= ManualApprove/Approve/Deny
	# successAction="Deny"
	# result: HTTP Error 500: There is an error in XML document (5, 146).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool="false"
	description= "test description"
	successAction="Deny"
	successActionDelay="30"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""


	# successAction= ManualApprove/Approve/Deny
	# successAction=""
	# result: HTTP Error 500: There is an error in XML document (5, 146).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool="false"
	description= "test description"
	successAction=""
	successActionDelay="30"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""
	

	# successAction= ManualApprove/Approve/Deny
	# successAction=random 20 chars (db len is 20)
	# result: HTTP Error 500: There is an error in XML document (5, 146).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool="false"
	description= "test description"
	successAction=mapi_util.random_str(20)
	successActionDelay="30"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""

	# successAction= ManualApprove/Approve/Deny
	# successActionDelay=""
	# result: "" will default to 0
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool="false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay=""
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""
	

	# successAction= ManualApprove/Approve/Deny
	# successActionDelay="0"
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool="false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="0"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""

	# successActionDelay="-1"
	# result: "-1" will default to 0
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool="false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="-1"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""

	# successActionDelay="aaa"
	# result: HTTP Error 500: There is an error in XML document (5, 156).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool="false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="aaa"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""
	

	# UI: maxlength=100, db max=2147483647, successActionDelay="2147483647"
	# result: pass
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool="false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="2147483647"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""


	# UI: maxlength=100, db max=2147483647, successActionDelay="2147483648" (2147483647+1)
	# result: fail, HTTP Error 500: There is an error in XML document (5, 163).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool="false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="2147483648"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""


	# failAction= ManualApprove/Approve/Deny
	# failAction="Deny"
	# result: pass, failActionDelay can still be updated
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool="false"
	description= "test description"
	successAction="Approve"
	successActionDelay="30"
	failAction="Deny"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""
	

	# failAction= ManualApprove/Approve/Deny
	# failAction="ManualApprove"
	# result: pass, successActionDelay can still be updated
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool="false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="30"
	failAction="ManualApprove"
	failActionDelay="30"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""



	# failAction= ManualApprove/Approve/Deny
	# failAction="Approve"
	# result: HTTP Error 500: There is an error in XML document (5, 146).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool="false"
	description= "test description"
	successAction="Deny"
	successActionDelay="30"
	failAction="Approve"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""


	# failAction= ManualApprove/Approve/Deny
	# failAction=""
	# result: HTTP Error 500: There is an error in XML document (5, 146).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool="false"
	description= "test description"
	successAction=""
	successActionDelay="30"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""
	

	# failAction= ManualApprove/Approve/Deny
	# failAction= random 20 chars (db len is 20)
	# result: HTTP Error 500: There is an error in XML document (5, 146).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool="false"
	description= "test description"
	successAction= mapi_util.random_str(20)
	successActionDelay="30"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""

	
	# failActionDelay=""
	# result: "" will default to 0
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool="false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay=""
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""
	

	# failActionDelay="0"
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool="false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="0"
	failAction="ManualApprove"
	failActionDelay="0"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""


	# failActionDelay="-1"
	# result: "-1" will default to 0
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool="false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="1"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""

	# failActionDelay="aaa"
	# result: HTTP Error 500: There is an error in XML document (5, 156).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool="false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="aaa"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""
	

	# UI: maxlength=100, db max=2147483647, failActionDelay="2147483647"
	# result: pass
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool="false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="2147483647"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""


	# UI: maxlength=100, db max=2147483647, failActionDelay="2147483648" (2147483647+1)
	# result: fail, HTTP Error 500: There is an error in XML document (5, 163).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool="false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="2147483648"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""
	

	# isResourcePool="false"
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool="false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""
	

	# isResourcePool="true"
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool="true"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""
	

	# isResourcePool=""
	# result: ok, default to false
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool=""
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""
	

	# isResourcePool=random 20 chars
	# result: HTTP Error 500: There is an error in XML document (5, 57).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = mapi_util.random_str(20)
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]
	"""

	"""
	print createSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					device_id_list,image_id_list, security_rule_list)
	"""



	# start security rules check
	#  *********************************************

	"""
	
- <xs:simpleType name="MatchType">
- <xs:restriction base="xs:string">
  <xs:enumeration value="MatchAll" /> 
  <xs:enumeration value="MatchAny" /> 


- <xs:simpleType name="EvaluatorType">
- <xs:restriction base="xs:string">
  <xs:enumeration value="equal" /> 
  <xs:enumeration value="notequal" /> 
  <xs:enumeration value="lessThan" /> 
  <xs:enumeration value="greaterThan" /> 
  <xs:enumeration value="equalLessThan" /> 
  <xs:enumeration value="equalGreaterThan" /> 
  <xs:enumeration value="information" /> 
  <xs:enumeration value="Has" /> 
  <xs:enumeration value="NotHave" /> 
  <xs:enumeration value="Containing" /> 
  <xs:enumeration value="NotContaining" /> 



	template

	# ,MatchAll, equal,
	# result:

	# ,MatchAny, equal, 
	# result:

	# ,"", equal, 
	# result:

	# ,random 20 chars, equal, 
	# result:

	# ,MatchAll, equal, 
	# result:

	# ,MatchAll, notequal, 
	# result:

	# ,MatchAll, greaterThan, 
	# result:

	# ,MatchAll, lessThan, 
	# result:

	# ,MatchAll, equalGreaterThan, 
	# result:

	# ,MatchAll, equalLessThan, 
	# result:

	# ,MatchAll, information, 
	# result:

	# ,MatchAll, Has, 
	# result:

	# ,MatchAll, NotHave, 
	# result:

	# ,MatchAll, Containing, 
	# result:

	# ,MatchAll, NotContaining, 
	# result:

	# ,MatchAll, "", 
	# result:

	# ,MatchAll, others, 
	# result:

	"""





	# no rules

	# Device Access Type,MatchAll, equal, Read Write
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Access Type", "MatchAll", "equal", "Read Write")
	security_rule_list=[security_rule]
	"""

	# Device Access Type,MatchAny, equal, Read Write
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Access Type", "MatchAny", "equal", "Read Write")
	security_rule_list=[security_rule]
	"""

	# Device Access Type,"", equal, Read Write
	# result: fail, HTTP Error 500: There is an error in XML document (5, 475).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Access Type", "", "equal", "Read Write")
	security_rule_list=[security_rule]
	"""


	# Device Access Type,matchall, equal, Read Write
	# result: fail, HTTP Error 500: There is an error in XML document (5, 483).

	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Access Type", "matchall", "equal", "Read Write")
	security_rule_list=[security_rule]




	# Device Access Type,random 20 chars, equal, Read Write
	# result: fail, HTTP Error 500: There is an error in XML document (5, 495).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Access Type", mapi_util.random_str(20), "equal", "Read Write")
	security_rule_list=[security_rule]
	"""

	# Device Access Type,MatchAll, equal, Read Write
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Access Type", "MatchAll", "equal", "Read Write")
	security_rule_list=[security_rule]
	"""

	# Device Access Type,MatchAll, notequal, Read Write
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Access Type", "MatchAll", "notequal", "Read Write")
	security_rule_list=[security_rule]
	"""

	# Device Access Type,MatchAll, greaterThan, Read Write
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Access Type", "MatchAll", "greaterThan", "Read Write")
	security_rule_list=[security_rule]
	"""

	# Device Access Type,MatchAll, lessThan, Read Write
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Access Type", "MatchAll", "lessThan", "Read Write")
	security_rule_list=[security_rule]
	"""



	# Device Access Type,MatchAll, equalGreaterThan, Read Write
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Access Type", "MatchAll", "equalGreaterThan", "Read Write")
	security_rule_list=[security_rule]
	"""

	# Device Access Type,MatchAll, equalLessThan, Read Write
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Access Type", "MatchAll", "equalLessThan", "Read Write")
	security_rule_list=[security_rule]
	"""


	# Device Access Type,MatchAll, information, Read Write
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Access Type", "MatchAll", "information", "Read Write")
	security_rule_list=[security_rule]
	"""


	# Device Access Type,MatchAll, Has, Read Write
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Access Type", "MatchAll", "Has", "Read Write")
	security_rule_list=[security_rule]
	"""

	# Device Access Type,MatchAll, NotHave, Read Write
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Access Type", "MatchAll", "NotHave", "Read Write")
	security_rule_list=[security_rule]
	"""


	# Device Access Type,MatchAll, Containing, Read Write
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Access Type", "MatchAll", "Containing", "Read Write")
	security_rule_list=[security_rule]
	"""

	# Device Access Type,MatchAll, NotContaining, Read Write
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Access Type", "MatchAll", "NotContaining", "Read Write")
	security_rule_list=[security_rule]
	"""

	# Device Access Type,MatchAll, "", Read Write
	# result: fail, HTTP Error 500: There is an error in XML document (5, 574).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Access Type", "MatchAll", "", "Read Write")
	security_rule_list=[security_rule]
	"""


	# Device Access Type,MatchAll, "EQUAL", Read Write
	# result: fail, HTTP Error 500: There is an error in XML document (5, 579).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Access Type", "MatchAll", "EQUAL", "Read Write")
	security_rule_list=[security_rule]
	"""

	# Device Access Type,MatchAll, random 20 chars, Read Write
	# result: fail, HTTP Error 500: There is an error in XML document (5, 594).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Access Type", "MatchAll", mapi_util.random_str(20), "Read Write")
	security_rule_list=[security_rule]
	"""

	# Device Access Type,MatchAll, equal, Read Write
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Access Type", "MatchAll", "equal", "Read Write")
	security_rule_list=[security_rule]
	"""

	# Device Access Type,MatchAll, equal, Read Only
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Access Type", "MatchAll", "equal", "Read Only")
	security_rule_list=[security_rule]
	"""


	# Device Access Type,MatchAll, equal, ""
	# result: ok, bug empty device type should not be allowed
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Access Type", "MatchAll", "equal", "")
	security_rule_list=[security_rule]
	"""

	# Device Access Type,MatchAll, equal, random 4000 chars
	# result: ok, bug values other than "Read Write" "Read Only" should not be allowed
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Access Type", "MatchAll", "equal", mapi_util.random_str(4000))
	security_rule_list=[security_rule]
	"""


	# Device Access Type,MatchAll, equal, random 4000+1 chars
	# result: ok, bug extra values are truncated
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Access Type", "MatchAll", "equal", mapi_util.random_str(4001))
	security_rule_list=[security_rule]
	"""

	# Device Access Type,MatchAll, equal, read write (case sensitive)
	# result: ok, bug should be case sensitive
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Access Type", "MatchAll", "equal", "read write")
	security_rule_list=[security_rule]
	"""




	# Device Mount Point,MatchAll, equal, /mnt/test
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Mount Point", "MatchAll", "equal", "/mnt/test")
	security_rule_list=[security_rule]
	"""

	# Device Mount Point,MatchAny, equal, /mnt/test
	# result: ok
	"""	
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Mount Point", "MatchAny", "equal", "/mnt/test")
	security_rule_list=[security_rule]
	"""

	# Device Mount Point,"", equal, /mnt/test
	# result: fail, HTTP Error 500: There is an error in XML document (5, 475).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Mount Point", "", "equal", "/mnt/test")
	security_rule_list=[security_rule]
	"""


	# Device Mount Point,matchall, equal, /mnt/test
	# result: fail, HTTP Error 500: There is an error in XML document (5, 483).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Mount Point", "matchall", "equal", "/mnt/test")
	security_rule_list=[security_rule]
	"""

	# Device Mount Point,random 20 chars, equal, /mnt/test
	# result: fail, HTTP Error 500: There is an error in XML document (5, 578).

	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Mount Point", mapi_util.random_str(20), "equal", "/mnt/test")
	security_rule_list=[security_rule]
	"""


	# Device Mount Point,MatchAll, equal, /mnt/test
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Mount Point", "MatchAll", "equal", "/mnt/test")
	security_rule_list=[security_rule]
	"""

	# Device Mount Point,MatchAll, notequal, /mnt/test
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Mount Point", "MatchAll", "notequal", "/mnt/test")
	security_rule_list=[security_rule]
	"""

	# Device Mount Point,MatchAll, greaterThan, /mnt/test
	# result: ok, bug not a option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Mount Point", "MatchAll", "greaterThan", "/mnt/test")
	security_rule_list=[security_rule]
	"""

	# Device Mount Point,MatchAll, lessThan, /mnt/test
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Mount Point", "MatchAll", "lessThan", "/mnt/test")
	security_rule_list=[security_rule]
	"""

	# Device Mount Point,MatchAll, equalGreaterThan, /mnt/test
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Mount Point", "MatchAll", "equalGreaterThan", "/mnt/test")
	security_rule_list=[security_rule]
	"""
	
	# Device Mount Point,MatchAll, equalLessThan, /mnt/test
	# result: ok, not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Mount Point", "MatchAll", "equalLessThan", "/mnt/test")
	security_rule_list=[security_rule]
	"""

	# Device Mount Point,MatchAll, information, /mnt/test
	# result: ok, if information, security rule is not created
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Mount Point", "MatchAll", "information", "/mnt/test")
	security_rule_list=[security_rule]
	"""


	# Device Mount Point,MatchAll, Has, /mnt/test
	# result: ok bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Mount Point", "MatchAll", "Has", "/mnt/test")
	security_rule_list=[security_rule]
	"""

	# Device Mount Point,MatchAll, NotHave, /mnt/test
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Mount Point", "MatchAll", "NotHave", "/mnt/test")
	security_rule_list=[security_rule]
	"""


	# Device Mount Point,MatchAll, Containing, /mnt/test
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Mount Point", "MatchAll", "Containing", "/mnt/test")
	security_rule_list=[security_rule]
	"""


	# Device Mount Point,MatchAll, NotContaining, /mnt/test
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Mount Point", "MatchAll", "NotContaining", "/mnt/test")
	security_rule_list=[security_rule]
	"""

	# Device Mount Point,MatchAll, "", /mnt/test
	# result: fail,HTTP Error 500: There is an error in XML document (5, 573).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Mount Point", "MatchAll", "", "/mnt/test")
	security_rule_list=[security_rule]
	"""


	# Device Mount Point,MatchAll, EQUAL, /mnt/test
	# result: fail,HTTP Error 500: There is an error in XML document (5, 578).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Mount Point", "MatchAll", "EQUAL", "/mnt/test")
	security_rule_list=[security_rule]
	"""

	# Device Mount Point,MatchAll, random 20 chars, /mnt/test
	# result: fail,HTTP Error 500: There is an error in XML document (5, 593).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Mount Point", "MatchAll", mapi_util.random_str(20), "/mnt/test")
	security_rule_list=[security_rule]
	"""

	# Device Mount Point,MatchAll, equal, UI max=256
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Mount Point", "MatchAll", "equal", mapi_util.random_str(256))
	security_rule_list=[security_rule]
	"""

	# Device Mount Point,MatchAll, equal, UI max 256+1
	# result: ok bug UI max is 256
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Mount Point", "MatchAll", "equal", mapi_util.random_str(257))
	security_rule_list=[security_rule]
	"""
	
	# Device Mount Point,MatchAll, equal, ""
	# result: ok bug cannot be empty
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Mount Point", "MatchAll", "equal", "")
	security_rule_list=[security_rule]
	"""


	# Device Mount Point,MatchAll, equal, invalid path "\\aaa\\bbb"
	# result: ok, bug invalid path
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Device Mount Point", "MatchAll", "equal", "\\aaa\\bbb")
	security_rule_list=[security_rule]
	"""
	



	# Key Request Date,MatchAll, equal, 06/01/2012
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Key Request Date", "MatchAll", "equal", "06/01/2012")
	security_rule_list=[security_rule]
	"""


	# Key Request Date,MatchAny, equal, 06/01/2012
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Key Request Date", "MatchAny", "equal", "06/01/2012")
	security_rule_list=[security_rule]
	"""

	# Key Request Date,"", equal, 06/01/2012
	# result: fail,HTTP Error 500: There is an error in XML document (5, 475).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Key Request Date", "", "equal", "06/01/2012")
	security_rule_list=[security_rule]
	"""

	# Key Request Date,matchall, equal, 06/01/2012
	# result: fail,HTTP Error 500: There is an error in XML document (5, 483).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Key Request Date", "matchall", "equal", "06/01/2012")
	security_rule_list=[security_rule]
	"""

	# Key Request Date,random 20 chars, equal, 06/01/2012
	# result: fail
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Key Request Date", mapi_util.random_str(20), "equal", "06/01/2012")
	security_rule_list=[security_rule]
	"""

	# Key Request Date,MatchAll, equal, 06/01/2012
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Key Request Date", "MatchAll", "equal", "06/01/2012")
	security_rule_list=[security_rule]
	"""

	# Key Request Date,MatchAll, notequal, 06/01/2012
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Key Request Date", "MatchAll", "notequal", "06/01/2012")
	security_rule_list=[security_rule]
	"""

	# Key Request Date,MatchAll, greaterThan, 06/01/2012
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Key Request Date", "MatchAll", "greaterThan", "06/01/2012")
	security_rule_list=[security_rule]
	"""

	# Key Request Date,MatchAll, lessThan, 06/01/2012
	# result: fail
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Key Request Date", "MatchAll", "lessThan", "06/01/2012")
	security_rule_list=[security_rule]
	"""

	# Key Request Date,MatchAll, equalGreaterThan, 06/01/2012
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Key Request Date", "MatchAll", "equalGreaterThan", "06/01/2012")
	security_rule_list=[security_rule]
	"""


	# Key Request Date,MatchAll, equalLessThan, 06/01/2012
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Key Request Date", "MatchAll", "equalLessThan", "06/01/2012")
	security_rule_list=[security_rule]
	"""


	# Key Request Date,MatchAll, information, 06/01/2012
	# result: ok, if information, no security rule is inserted
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Key Request Date", "MatchAll", "information", "06/01/2012")
	security_rule_list=[security_rule]
	"""


	# Key Request Date,MatchAll, Has, 06/01/2012
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Key Request Date", "MatchAll", "Has", "06/01/2012")
	security_rule_list=[security_rule]
	"""
	

	# Key Request Date,MatchAll, NotHave, 06/01/2012
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Key Request Date", "MatchAll", "NotHave", "06/01/2012")
	security_rule_list=[security_rule]
	"""


	# Key Request Date,MatchAll, Containing, 06/01/2012
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Key Request Date", "MatchAll", "Containing", "06/01/2012")
	security_rule_list=[security_rule]
	"""


	# Key Request Date,MatchAll, NotContaining, 06/01/2012
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Key Request Date", "MatchAll", "NotContaining", "06/01/2012")
	security_rule_list=[security_rule]
	"""

	# Key Request Date,MatchAll, "", 06/01/2012
	# result: fail,HTTP Error 500: There is an error in XML document (5, 574).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Key Request Date", "MatchAll", "", "06/01/2012")
	security_rule_list=[security_rule]
	"""


	# Key Request Date,MatchAll, EQUAL, 06/01/2012
	# result: fail,HTTP Error 500: There is an error in XML document (5, 579).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Key Request Date", "MatchAll", "EQUAL", "06/01/2012")
	security_rule_list=[security_rule]
	"""

	# Key Request Date,MatchAll, random 20 chars, 06/01/2012
	# result: fail,HTTP Error 500: There is an error in XML document (5, 594).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Key Request Date", "MatchAll", mapi_util.random_str(20), "06/01/2012")
	security_rule_list=[security_rule]
	"""

	# Key Request Date,MatchAll, equal, ""
	# result: ok, bug time cannot be empty
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Key Request Date", "MatchAll", "equal", "")
	security_rule_list=[security_rule]
	"""

	# Key Request Date,MatchAll, equal, not time format sadfasdfasf
	# result: ok, bug should only allow time format
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Key Request Date", "MatchAll", "equal", mapi_util.random_str(10))
	security_rule_list=[security_rule]
	"""

	# Key Request Date,MatchAll, equal, invalid time format 99/99/99
	# result: ok, bug should only allow valid format
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Key Request Date", "MatchAll", "equal", "99/99/99")
	security_rule_list=[security_rule]
	"""

	# Request Source IP Address,MatchAll, equal, 192.168.0.1
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IP Address", "MatchAll", "equal", "192.168.0.1")
	security_rule_list=[security_rule]
	"""
	
	# Request Source IP Address,MatchAny, equal, 192.168.0.1
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IP Address", "MatchAny", "equal", "192.168.0.1")
	security_rule_list=[security_rule]
	"""
	
	# Request Source IP Address,"", equal, 192.168.0.1
	# result: fail,HTTP Error 500: There is an error in XML document (5, 475).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IP Address", "", "equal", "192.168.0.1")
	security_rule_list=[security_rule]
	"""


	# Request Source IP Address,matchall, equal, 192.168.0.1
	# result: fail,HTTP Error 500: There is an error in XML document (5, 483).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IP Address", "matchall", "equal", "192.168.0.1")
	security_rule_list=[security_rule]
	"""


	# Request Source IP Address,random 20 chars, equal, 192.168.0.1
	# result: fail,HTTP Error 500: There is an error in XML document (5, 495).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IP Address", mapi_util.random_str(20), "equal", "192.168.0.1")
	security_rule_list=[security_rule]
	"""


	# Request Source IP Address,MatchAll, equal, 192.168.0.1
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IP Address", "MatchAll", "equal", "192.168.0.1")
	security_rule_list=[security_rule]
	"""

	# Request Source IP Address,MatchAll, notequal, 192.168.0.1
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IP Address", "MatchAll", "notequal", "192.168.0.1")
	security_rule_list=[security_rule]
	"""


	# Request Source IP Address,MatchAll, greaterThan, 192.168.0.1
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IP Address", "MatchAll", "greaterThan", "192.168.0.1")
	security_rule_list=[security_rule]
	"""

	# Request Source IP Address,MatchAll, lessThan, 192.168.0.1
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IP Address", "MatchAll", "lessThan", "192.168.0.1")
	security_rule_list=[security_rule]
	"""

	# Request Source IP Address,MatchAll, equalGreaterThan, 192.168.0.1
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IP Address", "MatchAll", "equalGreaterThan", "192.168.0.1")
	security_rule_list=[security_rule]
	"""

	# Request Source IP Address,MatchAll, equalLessThan, 192.168.0.1
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IP Address", "MatchAll", "equalLessThan", "192.168.0.1")
	security_rule_list=[security_rule]
	"""

	# Request Source IP Address,MatchAll, information, 192.168.0.1
	# result: ok, if information, security rule is not inserted
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IP Address", "MatchAll", "information", "192.168.0.1")
	security_rule_list=[security_rule]
	"""


	# Request Source IP Address,MatchAll, Has, 192.168.0.1
	# result: fail
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IP Address", "MatchAll", "Has", "192.168.0.1")
	security_rule_list=[security_rule]
	"""


	# Request Source IP Address,MatchAll, NotHave, 192.168.0.1
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IP Address", "MatchAll", "NotHave", "192.168.0.1")
	security_rule_list=[security_rule]
	"""


	# Request Source IP Address,MatchAll, Containing, 192.168.0.1
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IP Address", "MatchAll", "Containing", "192.168.0.1")
	security_rule_list=[security_rule]
	"""


	# Request Source IP Address,MatchAll, NotContaining, 192.168.0.1
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IP Address", "MatchAll", "NotContaining", "192.168.0.1")
	security_rule_list=[security_rule]
	"""

	# Request Source IP Address,MatchAll, "", 192.168.0.1
	# result: fail,HTTP Error 500: There is an error in XML document (5, 575).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IP Address", "MatchAll", "", "192.168.0.1")
	security_rule_list=[security_rule]
	"""


	# Request Source IP Address,matchAll, EQUAL, 192.168.0.1
	# result: fail,HTTP Error 500: There is an error in XML document (5, 580).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IP Address", "MatchAll", "EQUAL", "192.168.0.1")
	security_rule_list=[security_rule]
	"""

	# Request Source IP Address,matchAll, random 20 chars, 192.168.0.1
	# result: fail,HTTP Error 500: There is an error in XML document (5, 595).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IP Address", "MatchAll", mapi_util.random_str(20), "192.168.0.1")
	security_rule_list=[security_rule]
	"""
	
	# Request Source IP Address,MatchAll, equal, 192.168.0.1
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IP Address", "MatchAll", "equal", "192.168.0.1")
	security_rule_list=[security_rule]
	"""

	# Request Source IP Address,MatchAll, equal, 192.168.1.0/24
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IP Address", "MatchAll", "equal", "192.168.1.0/24")
	security_rule_list=[security_rule]
	"""

	# Request Source IP Address,MatchAll, equal, random 20 chars
	# result: ok, bug should only allow IP address
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IP Address", "MatchAll", "equal", mapi_util.random_str(20))
	security_rule_list=[security_rule]
	"""


	# Request Source IP Address,MatchAll, equal, 300.300.300.300 invalide ip address
	# result: ok, bug should check IP format
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IP Address", "MatchAll", "equal", "300.300.300.300")
	security_rule_list=[security_rule]
	"""


	# Request Source IP Address,MatchAll, equal, 192.168.1.0/300 invalide ip range
	# result: ok, bug should check valid IP range
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IP Address", "MatchAll", "equal", "192.168.1.0/300")
	security_rule_list=[security_rule]
	"""




	# Request Source IPv6 Address,MatchAll, equal, 2001:0DB8::1428:57ab
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IPv6 Address", "MatchAll", "equal", "2001:0DB8::1428:57ab")
	security_rule_list=[security_rule]
	"""

	# Request Source IPv6 Address,MatchAny, equal, 2001:0DB8::1428:57ab
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IPv6 Address", "MatchAny", "equal", "2001:0DB8::1428:57ab")
	security_rule_list=[security_rule]
	"""

	# Request Source IPv6 Address,"", equal, 2001:0DB8::1428:57ab
	# result: fail,HTTP Error 500: There is an error in XML document (5, 475).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IPv6 Address", "", "equal", "2001:0DB8::1428:57ab")
	security_rule_list=[security_rule]
	"""
	

	# Request Source IPv6 Address,matchall, equal, 2001:0DB8::1428:57ab
	# result: fail,HTTP Error 500: There is an error in XML document (5, 483).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IPv6 Address", "matchall", "equal", "2001:0DB8::1428:57ab")
	security_rule_list=[security_rule]
	"""


	# Request Source IPv6 Address,random 20 chars, equal, 2001:0DB8::1428:57ab
	# result: fail,HTTP Error 500: There is an error in XML document (5, 495).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IPv6 Address", mapi_util.random_str(20), "equal", "2001:0DB8::1428:57ab")
	security_rule_list=[security_rule]
	"""


	# Request Source IPv6 Address,MatchAll, equal, 2001:0DB8::1428:57ab
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IPv6 Address", "MatchAll", "equal", "2001:0DB8::1428:57ab")
	security_rule_list=[security_rule]
	"""

	# Request Source IPv6 Address,MatchAll, notequal, 2001:0DB8::1428:57ab
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IPv6 Address", "MatchAll", "notequal", "2001:0DB8::1428:57ab")
	security_rule_list=[security_rule]
	"""

	# Request Source IPv6 Address,MatchAll, greaterThan, 2001:0DB8::1428:57ab
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IPv6 Address", "MatchAll", "greaterThan", "2001:0DB8::1428:57ab")
	security_rule_list=[security_rule]
	"""

	# Request Source IPv6 Address,MatchAll, lessThan, 2001:0DB8::1428:57ab
	# result: ok, not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IPv6 Address", "MatchAll", "lessThan", "2001:0DB8::1428:57ab")
	security_rule_list=[security_rule]
	"""


	# Request Source IPv6 Address,MatchAll, equalGreaterThan, 2001:0DB8::1428:57ab
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IPv6 Address", "MatchAll", "equalGreaterThan", "2001:0DB8::1428:57ab")
	security_rule_list=[security_rule]
	"""

	# Request Source IPv6 Address,MatchAll, equalLessThan, 2001:0DB8::1428:57ab
	# result: ok, not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IPv6 Address", "MatchAll", "equalLessThan", "2001:0DB8::1428:57ab")
	security_rule_list=[security_rule]
	"""

	# Request Source IPv6 Address,MatchAll, information, 2001:0DB8::1428:57ab
	# result: ok, if information, security rule is not inserted
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IPv6 Address", "MatchAll", "information", "2001:0DB8::1428:57ab")
	security_rule_list=[security_rule]
	"""

	# Request Source IPv6 Address,MatchAll, Has, 2001:0DB8::1428:57ab
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IPv6 Address", "MatchAll", "Has", "2001:0DB8::1428:57ab")
	security_rule_list=[security_rule]
	"""


	# Request Source IPv6 Address,MatchAll, NotHave, 2001:0DB8::1428:57ab
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IPv6 Address", "MatchAll", "NotHave", "2001:0DB8::1428:57ab")
	security_rule_list=[security_rule]
	"""


	# Request Source IPv6 Address,MatchAll, Containing, 2001:0DB8::1428:57ab
	# result: ok, not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IPv6 Address", "MatchAll", "Containing", "2001:0DB8::1428:57ab")
	security_rule_list=[security_rule]
	"""
	

	# Request Source IPv6 Address,MatchAll, NotContaining, 2001:0DB8::1428:57ab
	# result: ok, not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IPv6 Address", "MatchAll", "NotContaining", "2001:0DB8::1428:57ab")
	security_rule_list=[security_rule]
	"""


	# Request Source IPv6 Address,MatchAll, "", 2001:0DB8::1428:57ab
	# result: fail,HTTP Error 500: There is an error in XML document (5, 584).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IPv6 Address", "MatchAll", "", "2001:0DB8::1428:57ab")
	security_rule_list=[security_rule]
	"""

	# Request Source IPv6 Address,MatchAll, EQUAL, 2001:0DB8::1428:57ab
	# result: fail,HTTP Error 500: There is an error in XML document (5, 589).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IPv6 Address", "MatchAll", "EQUAL", "2001:0DB8::1428:57ab")
	security_rule_list=[security_rule]
	"""


	# Request Source IPv6 Address,MatchAll, random 20 chars, 2001:0DB8::1428:57ab
	# result: fail,HTTP Error 500: There is an error in XML document (5, 604).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IPv6 Address", "MatchAll", mapi_util.random_str(20), "2001:0DB8::1428:57ab")
	security_rule_list=[security_rule]
	"""
	

	# Request Source IPv6 Address,MatchAll, equal, 2001:0DB8::1428:57ab
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IPv6 Address", "MatchAll", "equal", "2001:0DB8::1428:57ab")
	security_rule_list=[security_rule]
	"""

	# Request Source IPv6 Address,MatchAll, equal, 2001:0DB8::1428:57ab/96
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IPv6 Address", "MatchAll", "equal", "2001:0DB8::1428:57ab/96")
	security_rule_list=[security_rule]
	"""	

	# Request Source IPv6 Address,MatchAll, equal, random 30 chars
	# result: ok, bug should only allow IP address
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IPv6 Address", "MatchAll", "equal", mapi_util.random_str(30))
	security_rule_list=[security_rule]
	"""

	# Request Source IPv6 Address,MatchAll, equal, ZZZZ:ZZZZ:ZZZZ:ZZZZ:ZZZZ:ZZZZ:ZZZZ:ZZZZ invalide ip address
	# result: ok, bug should check IP format
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IPv6 Address", "MatchAll", "equal", "ZZZZ:ZZZZ:ZZZZ:ZZZZ:ZZZZ:ZZZZ:ZZZZ:ZZZZ")
	security_rule_list=[security_rule]
	"""


	# Request Source IPv6 Address,MatchAll, equal, 2001:0DB8::1428:57ab/ZZZZ invalide ip range
	# result: ok, bug should check valid IP range
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Request Source IPv6 Address", "MatchAll", "equal", "2001:0DB8::1428:57ab/ZZZZ")
	security_rule_list=[security_rule]
	"""




	# Instance First Seen,MatchAll, equal, 06/01/2012
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance First Seen", "MatchAll", "equal", "06/01/2012")
	security_rule_list=[security_rule]
	"""

	# Instance First Seen,MatchAny, equal, 06/01/2012
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance First Seen", "MatchAny", "equal", "06/01/2012")
	security_rule_list=[security_rule]
	"""


	# Instance First Seen,"", equal, 06/01/2012
	# result: fail,HTTP Error 500: There is an error in XML document (5, 475).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance First Seen", "", "equal", "06/01/2012")
	security_rule_list=[security_rule]
	"""


	# Instance First Seen,matchall, equal, 06/01/2012
	# result: fail,HTTP Error 500: There is an error in XML document (5, 483).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance First Seen", "matchall", "equal", "06/01/2012")
	security_rule_list=[security_rule]
	"""
	

	# Instance First Seen,random 20 chars, equal, 06/01/2012
	# result: fail,HTTP Error 500: There is an error in XML document (5, 495).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance First Seen", mapi_util.random_str(20), "equal", "06/01/2012")
	security_rule_list=[security_rule]
	"""

	# Instance First Seen,MatchAll, equal, 06/01/2012
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance First Seen", "MatchAll", "equal", "06/01/2012")
	security_rule_list=[security_rule]
	"""


	# Instance First Seen,MatchAll, notequal, 06/01/2012
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance First Seen", "MatchAll", "notequal", "06/01/2012")
	security_rule_list=[security_rule]
	"""


	# Instance First Seen,MatchAll, greaterThan, 06/01/2012
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance First Seen", "MatchAll", "greaterThan", "06/01/2012")
	security_rule_list=[security_rule]
	"""

	# Instance First Seen,MatchAll, lessThan, 06/01/2012
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance First Seen", "MatchAll", "lessThan", "06/01/2012")
	security_rule_list=[security_rule]
	"""


	# Instance First Seen,MatchAll, equalGreaterThan, 06/01/2012
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance First Seen", "MatchAll", "equalGreaterThan", "06/01/2012")
	security_rule_list=[security_rule]
	"""


	# Instance First Seen,MatchAll, equalLessThan, 06/01/2012
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance First Seen", "MatchAll", "equalLessThan", "06/01/2012")
	security_rule_list=[security_rule]
	"""
	

	# Instance First Seen,MatchAll, information, 06/01/2012
	# result: ok, if information, security rule is not inserted
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance First Seen", "MatchAll", "information", "06/01/2012")
	security_rule_list=[security_rule]
	"""

	# Instance First Seen,MatchAll, Has, 06/01/2012
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance First Seen", "MatchAll", "Has", "06/01/2012")
	security_rule_list=[security_rule]
	"""


	# Instance First Seen,MatchAll, NotHave, 06/01/2012
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance First Seen", "MatchAll", "NotHave", "06/01/2012")
	security_rule_list=[security_rule]
	"""


	# Instance First Seen,MatchAll, Containing, 06/01/2012
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance First Seen", "MatchAll", "Containing", "06/01/2012")
	security_rule_list=[security_rule]
	"""


	# Instance First Seen,MatchAll, NotContaining, 06/01/2012
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance First Seen", "MatchAll", "NotContaining", "06/01/2012")
	security_rule_list=[security_rule]
	"""

	# Instance First Seen,MatchAll, "", 06/01/2012
	# result: fail,HTTP Error 500: There is an error in XML document (5, 574).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance First Seen", "MatchAll", "", "06/01/2012")
	security_rule_list=[security_rule]
	"""

	# Instance First Seen,MatchAll, EQUAL, 06/01/2012
	# result: fail,HTTP Error 500: There is an error in XML document (5, 579).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance First Seen", "MatchAll", "EQUAL", "06/01/2012")
	security_rule_list=[security_rule]
	"""
	

	# Instance First Seen,MatchAll, random 20 chars, 06/01/2012
	# result: fail,HTTP Error 500: There is an error in XML document (5, 594).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance First Seen", "MatchAll", mapi_util.random_str(20), "06/01/2012")
	security_rule_list=[security_rule]
	"""

	# Instance First Seen,MatchAll, equal, ""
	# result: ok, bug time should not be empty
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance First Seen", "MatchAll", "equal", "")
	security_rule_list=[security_rule]
	"""

	# Instance First Seen,MatchAll, equal, not time format sadfasdfasf
	# result: ok, bug time format should be checked
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance First Seen", "MatchAll", "equal", mapi_util.random_str(10))
	security_rule_list=[security_rule]
	"""


	# Instance First Seen,MatchAll, equal, invalid time format 99/99/99
	# result: ok, valid time format should be checked
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance First Seen", "MatchAll", "equal", "99/99/99")
	security_rule_list=[security_rule]
	"""


	# Instance User Data,MatchAll, equal,test
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance User Data", "MatchAll", "equal", "test")
	security_rule_list=[security_rule]
	"""

	# Instance User Data,MatchAny, equal, test
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance User Data", "MatchAny", "equal", "test")
	security_rule_list=[security_rule]
	"""


	# Instance User Data,"", equal, test
	# result: fail,HTTP Error 500: There is an error in XML document (5, 475).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance User Data", "", "equal", "test")
	security_rule_list=[security_rule]
	"""

	# Instance User Data,matchall, equal, test
	# result: fail,HTTP Error 500: There is an error in XML document (5, 483).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance User Data", "matchall", "equal", "test")
	security_rule_list=[security_rule]
	"""

	# Instance User Data,random 20 chars, equal, test
	# result: fail,HTTP Error 500: There is an error in XML document (5, 495).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance User Data", mapi_util.random_str(20), "equal", "test")
	security_rule_list=[security_rule]
	"""
	

	# Instance User Data,MatchAll, equal, test
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance User Data", "MatchAll", "equal", "test")
	security_rule_list=[security_rule]
	"""


	# Instance User Data,MatchAll, notequal, test
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance User Data", "MatchAll", "notequal", "test")
	security_rule_list=[security_rule]
	"""

	# Instance User Data,MatchAll, greaterThan, test
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance User Data", "MatchAll", "greaterThan", "test")
	security_rule_list=[security_rule]
	"""

	# Instance User Data,MatchAll, lessThan, test
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance User Data", "MatchAll", "lessThan", "test")
	security_rule_list=[security_rule]
	"""

	# Instance User Data,MatchAll, equalGreaterThan, test
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance User Data", "MatchAll", "equalGreaterThan", "test")
	security_rule_list=[security_rule]
	"""

	# Instance User Data,MatchAll, equalLessThan, test
	# result: ok, bug not valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance User Data", "MatchAll", "equalLessThan", "test")
	security_rule_list=[security_rule]
	"""
	

	# Instance User Data,MatchAll, information, test
	# result: ok, if information, security rule is not saved
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance User Data", "MatchAll", "information", "test")
	security_rule_list=[security_rule]
	"""
	
	# Instance User Data,MatchAll, Has, test
	# result: fail
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance User Data", "MatchAll", "Has", "test")
	security_rule_list=[security_rule]
	"""
	
	# Instance User Data,MatchAll, NotHave, test
	# result: ok, not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance User Data", "MatchAll", "NotHave", "test")
	security_rule_list=[security_rule]
	"""


	# Instance User Data,MatchAll, Containing, test
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance User Data", "MatchAll", "Containing", "test")
	security_rule_list=[security_rule]
	"""

	# Instance User Data,MatchAll, NotContaining, test
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance User Data", "MatchAll", "NotContaining", "test")
	security_rule_list=[security_rule]
	"""
	
	# Instance User Data,MatchAll, "", test
	# result: fail,HTTP Error 500: There is an error in XML document (5, 568).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance User Data", "MatchAll", "", "test")
	security_rule_list=[security_rule]
	"""

	# Instance User Data,MatchAll, EQUAL, test
	# result: fail,HTTP Error 500: There is an error in XML document (5, 573).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance User Data", "MatchAll", "EQUAL", "test")
	security_rule_list=[security_rule]
	"""


	# Instance User Data,MatchAll, random 20 chars, test
	# result: fail,HTTP Error 500: There is an error in XML document (5, 588).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance User Data", "MatchAll", mapi_util.random_str(20), "test")
	security_rule_list=[security_rule]
	"""
	

	# Instance User Data,MatchAll, equal, UI max 256
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance User Data", "MatchAll", "equal", mapi_util.random_str(256))
	security_rule_list=[security_rule]
	"""


	# Instance User Data,MatchAll, equal, UI max 256+1
	# result: ok, bug UI max 256
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance User Data", "MatchAll", "equal", mapi_util.random_str(257))
	security_rule_list=[security_rule]
	"""



	# Instance User Data,MatchAll, equal, db max 4000
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance User Data", "MatchAll", "equal", mapi_util.random_str(4000))
	security_rule_list=[security_rule]
	"""

	# Instance User Data,MatchAll, others, db max 4000+1
	# result: ok, bug extra char is truncated
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance User Data", "MatchAll", "equal", mapi_util.random_str(4001))
	security_rule_list=[security_rule]
	"""

	# Instance User Data,MatchAll, equal, ""
	# result: ok, bug empty user data should not be allowed
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance User Data", "MatchAll", "equal", "")
	security_rule_list=[security_rule]
	"""


	# Instance User Data,MatchAll, equal, special chars
	# result: ??
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance User Data", "MatchAll", "equal", "")
	security_rule_list=[security_rule]
	"""



	# Instance Location,MatchAll, equal, japan
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance Location", "MatchAll", "equal", "japan")
	security_rule_list=[security_rule]
	"""

	# Instance Location,MatchAny, equal, japan
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance Location", "MatchAny", "equal", "japan")
	security_rule_list=[security_rule]
	"""
	
	# Instance Location,"", equal,  japan
	# result: fail,HTTP Error 500: There is an error in XML document (5, 475).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance Location", "", "equal", "japan")
	security_rule_list=[security_rule]
	"""

	# Instance Location,matchall, equal,  japan
	# result: fail,HTTP Error 500: There is an error in XML document (5, 483).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance Location", "matchall", "equal", "japan")
	security_rule_list=[security_rule]
	"""

	# Instance Location,random 20 chars, equal, japan
	# result: fail,HTTP Error 500: There is an error in XML document (5, 495).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance Location", mapi_util.random_str(20), "equal", "japan")
	security_rule_list=[security_rule]
	"""

	# Instance Location,MatchAll, equal, japan
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance Location", "MatchAll", "equal", "japan")
	security_rule_list=[security_rule]
	"""
	
	# Instance Location,MatchAll, notequal, japan
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance Location", "MatchAll", "notequal", "japan")
	security_rule_list=[security_rule]
	"""

	# Instance Location,MatchAll, greaterThan, japan
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance Location", "MatchAll", "greaterThan", "japan")
	security_rule_list=[security_rule]
	"""

	# Instance Location,MatchAll, lessThan, japan
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance Location", "MatchAll", "lessThan", "japan")
	security_rule_list=[security_rule]
	"""
	
	# Instance Location,MatchAll, equalGreaterThan, japan
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance Location", "MatchAll", "equalGreaterThan", "japan")
	security_rule_list=[security_rule]
	"""

	# Instance Location,MatchAll, equalLessThan, japan
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance Location", "MatchAll", "equalLessThan", "japan")
	security_rule_list=[security_rule]
	"""


	# Instance Location,MatchAll, information, japan
	# result: ok, if information, security rule is not saved
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance Location", "MatchAll", "information", "japan")
	security_rule_list=[security_rule]
	"""

	# Instance Location,MatchAll, Has, japan
	# result: ok, not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance Location", "MatchAll", "Has", "japan")
	security_rule_list=[security_rule]
	"""

	# Instance Location,MatchAll, NotHave, japan
	# result: ok, not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance Location", "MatchAll", "NotHave", "japan")
	security_rule_list=[security_rule]
	"""
	
	# Instance Location,MatchAll, Containing, japan
	# result: ok, not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance Location", "MatchAll", "Containing", "japan")
	security_rule_list=[security_rule]
	"""
	
	# Instance Location,MatchAll, NotContaining, japan
	# result: ok, not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance Location", "MatchAll", "NotContaining", "japan")
	security_rule_list=[security_rule]
	"""

	# Instance Location,MatchAll, "", japan
	# result: fail,HTTP Error 500: There is an error in XML document (5, 569).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance Location", "MatchAll", "", "japan")
	security_rule_list=[security_rule]
	"""
	
	# Instance Location,MatchAll, EQUAL, japan
	# result: fail,HTTP Error 500: There is an error in XML document (5, 574).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance Location", "MatchAll", "EQUAL", "japan")
	security_rule_list=[security_rule]
	"""
	

	# Instance Location,MatchAll, random 20 chars, japan
	# result: fail,HTTP Error 500: There is an error in XML document (5, 589).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance Location", "MatchAll", mapi_util.random_str(20), "japan")
	security_rule_list=[security_rule]
	"""

	# Instance Location,MatchAll, equal, UI max 256
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance Location", "MatchAll", "equal", mapi_util.random_str(256))
	security_rule_list=[security_rule]
	"""
	
	# Instance LocationMatchAll, equal, UI max 256+1
	# result: ok, bug UI max is 256
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance Location", "MatchAll", "equal", mapi_util.random_str(257))
	security_rule_list=[security_rule]
	"""


	# Instance Location,MatchAll, equal, db max 4000
	# result: ok, bug UI max is 256
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance Location", "MatchAll", "equal", mapi_util.random_str(4000))
	security_rule_list=[security_rule]
	"""

	# Instance Location,MatchAll, equal, db max 4000+1
	# result: ok, bug extra char is truncated
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance Location", "MatchAll", "equal", mapi_util.random_str(4001))
	security_rule_list=[security_rule]
	"""

	# Instance Location,MatchAll, equal, ""
	# result: ok, bug empty location should not be allowed
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Instance Location", "MatchAll", "equal", "")
	security_rule_list=[security_rule]
	"""



	# OSSEC Version,MatchAll, equal, 2.0
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("OSSEC Version", "MatchAll", "equal", "2.0")
	security_rule_list=[security_rule]
	"""

	# OSSEC Version,MatchAny, equal, 2.0
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("OSSEC Version", "MatchAny", "equal", "2.0")
	security_rule_list=[security_rule]
	"""


	# OSSEC Version,"", equal,  2.0
	# result: fail,HTTP Error 500: There is an error in XML document (5, 475).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("OSSEC Version", "", "equal", "2.0")
	security_rule_list=[security_rule]
	"""

	# OSSEC Version,matchall, equal,  2.0
	# result: fail,HTTP Error 500: There is an error in XML document (5, 483).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("OSSEC Version", "matchall", "equal", "2.0")
	security_rule_list=[security_rule]
	"""

	# OSSEC Version,random 20 chars, equal, 2.0
	# result: fail,HTTP Error 500: There is an error in XML document (5, 495).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("OSSEC Version", mapi_util.random_str(20), "equal", "2.0")
	security_rule_list=[security_rule]
	"""


	# OSSEC Version,MatchAll, equal, 2.0
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("OSSEC Version", "MatchAll", "equal", "2.0")
	security_rule_list=[security_rule]
	"""


	# OSSEC Version,MatchAll, notequal, 2.0
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("OSSEC Version", "MatchAll", "notequal", "2.0")
	security_rule_list=[security_rule]
	"""


	# OSSEC Version,MatchAll, greaterThan, 2.0
	# result: ok, not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("OSSEC Version", "MatchAll", "greaterThan", "2.0")
	security_rule_list=[security_rule]
	"""


	# OSSEC Version,MatchAll, lessThan, 2.0
	# result: ok, not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("OSSEC Version", "MatchAll", "lessThan", "2.0")
	security_rule_list=[security_rule]
	"""


	# OSSEC Version,MatchAll, equalGreaterThan, 2.0
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("OSSEC Version", "MatchAll", "equalGreaterThan", "2.0")
	security_rule_list=[security_rule]
	"""


	# OSSEC Version,MatchAll, equalLessThan, 2.0
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("OSSEC Version", "MatchAll", "equalLessThan", "2.0")
	security_rule_list=[security_rule]
	"""

	# OSSEC Version,MatchAll, information, 2.0
	# result: ok, if information, security rule is not saved
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("OSSEC Version", "MatchAll", "information", "2.0")
	security_rule_list=[security_rule]
	"""


	# OSSEC Version,MatchAll, Has, 2.0
	# result: ok, not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("OSSEC Version", "MatchAll", "Has", "2.0")
	security_rule_list=[security_rule]
	"""


	# OSSEC Version,MatchAll, NotHave, 2.0
	# result: ok, not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("OSSEC Version", "MatchAll", "NotHave", "2.0")
	security_rule_list=[security_rule]
	"""


	# OSSEC Version,MatchAll, Containing, 2.0
	# result: ok, not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("OSSEC Version", "MatchAll", "Containing", "2.0")
	security_rule_list=[security_rule]
	"""

	# OSSEC Version,MatchAll, NotContaining, 2.0
	# result: ok, not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("OSSEC Version", "MatchAll", "NotContaining", "2.0")
	security_rule_list=[security_rule]
	"""
	

	# OSSEC Version,MatchAll, "", 2.0
	# result: fail,HTTP Error 500: There is an error in XML document (5, 567).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("OSSEC Version", "MatchAll", "", "2.0")
	security_rule_list=[security_rule]
	"""

	# OSSEC Version,MatchAll, EQUAL, 2.0
	# result: fail,HTTP Error 500: There is an error in XML document (5, 572).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("OSSEC Version", "MatchAll", "EQUAL", "2.0")
	security_rule_list=[security_rule]
	"""



	# OSSEC Version,MatchAll, random 20 chars, 2.0
	# result: fail,HTTP Error 500: There is an error in XML document (5, 587).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("OSSEC Version", "MatchAll", mapi_util.random_str(20), "2.0")
	security_rule_list=[security_rule]
	"""

	# OSSEC Version,MatchAll, equal, UI max 128
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("OSSEC Version", "MatchAll", "equal", mapi_util.random_str(128))
	security_rule_list=[security_rule]
	"""

	# OSSEC Version,MatchAll, equal, UI max 128+1
	# result: ok, bug exceed UI max
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("OSSEC Version", "MatchAll", "equal", mapi_util.random_str(129))
	security_rule_list=[security_rule]
	"""
	
	# OSSEC Version,MatchAll, equal, db max 4000
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("OSSEC Version", "MatchAll", "equal", mapi_util.random_str(4000))
	security_rule_list=[security_rule]
	"""
	
	# OSSEC Version,MatchAll, equal, db max 4000+1
	# result: ok, bug extra char is truncated
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("OSSEC Version", "MatchAll", "equal", mapi_util.random_str(4001))
	security_rule_list=[security_rule]
	"""


	# OSSEC Version,MatchAll, equal, ""
	# result: ok, empty should not be allowed
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("OSSEC Version", "MatchAll", "equal", "")
	security_rule_list=[security_rule]
	"""

	# OSSEC Version,MatchAll, equal, non-integer
	# result: ok bug should only allow digits, dot
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("OSSEC Version", "MatchAll", "equal", "aaabbbccc123")
	security_rule_list=[security_rule]
	"""


	# OSSEC Version,MatchAll, equal, negative integer
	# result: ok, bug should only allow valid version
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("OSSEC Version", "MatchAll", "equal", "-1.2")
	security_rule_list=[security_rule]
	"""


	# Trend Micro Virus Scan Engine,MatchAll, equal, 1.0
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Engine", "MatchAll", "equal", "1.0")
	security_rule_list=[security_rule]
	"""

	# Trend Micro Virus Scan Engine,MatchAny, equal, 1.0
	# result: fail, should only allow MatchAll
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Engine", "MatchAny", "equal", "1.0")
	security_rule_list=[security_rule]
	"""


	# Trend Micro Virus Scan Engine,"", equal, 1.0
	# result: fail,HTTP Error 500: There is an error in XML document (5, 475).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Engine", "", "equal", "1.0")
	security_rule_list=[security_rule]
	"""
	
	# Trend Micro Virus Scan Engine,matchall, equal, 1.0
	# result: fail,HTTP Error 500: There is an error in XML document (5, 483).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Engine", "matchall", "equal", "1.0")
	security_rule_list=[security_rule]
	"""

	# Trend Micro Virus Scan Engine,random 20 chars, equal, 1.0
	# result: fail,HTTP Error 500: There is an error in XML document (5, 495).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Engine", mapi_util.random_str(20), "equal", "1.0")
	security_rule_list=[security_rule]
	"""

	# Trend Micro Virus Scan Engine,MatchAll, equal, 1.0
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Engine", "MatchAll", "equal", "1.0")
	security_rule_list=[security_rule]
	"""


	# Trend Micro Virus Scan Engine,MatchAll, notequal, 1.0
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Engine", "MatchAll", "notequal", "1.0")
	security_rule_list=[security_rule]
	"""
	
	# Trend Micro Virus Scan Engine,MatchAll, greaterThan, 1.0
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Engine", "MatchAll", "greaterThan", "1.0")
	security_rule_list=[security_rule]
	"""
	
	# Trend Micro Virus Scan Engine,MatchAll, lessThan, 1.0
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Engine", "MatchAll", "lessThan", "1.0")
	security_rule_list=[security_rule]
	"""
	
	# Trend Micro Virus Scan Engine,MatchAll, equalGreaterThan, 1.0
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Engine", "MatchAll", "equalGreaterThan", "1.0")
	security_rule_list=[security_rule]
	"""


	# Trend Micro Virus Scan Engine,MatchAll, equalLessThan, 1.0
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Engine", "MatchAll", "equalLessThan", "1.0")
	security_rule_list=[security_rule]
	"""

	# Trend Micro Virus Scan Engine,MatchAll, information, 1.0
	# result: ok, if information, security rule is not saved
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Engine", "MatchAll", "information", "1.0")
	security_rule_list=[security_rule]
	"""


	# Trend Micro Virus Scan Engine,MatchAll, Has, 1.0
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Engine", "MatchAll", "Has", "1.0")
	security_rule_list=[security_rule]
	"""
	
	# Trend Micro Virus Scan Engine,MatchAll, NotHave, 1.0
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Engine", "MatchAll", "NotHave", "1.0")
	security_rule_list=[security_rule]
	"""
	
	# Trend Micro Virus Scan Engine,MatchAll, Containing, 1.0
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Engine", "MatchAll", "Containing", "1.0")
	security_rule_list=[security_rule]
	"""

	# Trend Micro Virus Scan Engine,MatchAll, NotContaining, 1.0
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Engine", "MatchAll", "NotContaining", "1.0")
	security_rule_list=[security_rule]
	"""
	
	# Trend Micro Virus Scan Engine,MatchAll, "", 1.0
	# result: fail,HTTP Error 500: There is an error in XML document (5, 567).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Engine", "MatchAll", "", "1.0")
	security_rule_list=[security_rule]
	"""

	# Trend Micro Virus Scan Engine,MatchAll, EQUAL, 1.0
	# result: fail,HTTP Error 500: There is an error in XML document (5, 572).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Engine", "MatchAll", "EQUAL", "1.0")
	security_rule_list=[security_rule]
	"""


	# Trend Micro Virus Scan Engine,MatchAll, random 20 chars, 1.0
	# result: fail,HTTP Error 500: There is an error in XML document (5, 587).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Engine", "MatchAll", mapi_util.random_str(20), "1.0")
	security_rule_list=[security_rule]
	"""

	# Trend Micro Virus Scan Engine,MatchAll, equal, UI max 128
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Engine", "MatchAll", "equal", mapi_util.random_str(128))
	security_rule_list=[security_rule]
	"""


	# Trend Micro Virus Scan Engine,MatchAll, equal, UI max 129
	# result: ok, bug UI max is 129
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Engine", "MatchAll", "equal", mapi_util.random_str(129))
	security_rule_list=[security_rule]
	"""

	# Trend Micro Virus Scan Engine,MatchAll, equal, db max 4000
	# result: ok, bug UI max is 128
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Engine", "MatchAll", "equal", mapi_util.random_str(4000))
	security_rule_list=[security_rule]
	"""


	# Trend Micro Virus Scan Engine,MatchAll, equal, db max 4001
	# result: ok, bug extra char is truncated
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Engine", "MatchAll", "equal", mapi_util.random_str(4001))
	security_rule_list=[security_rule]
	"""


	# Trend Micro Virus Scan Engine,MatchAll, equal, non-integer
	# result: ok, bug should only allow digits and dot
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Engine", "MatchAll", "equal", "aaabbbccc")
	security_rule_list=[security_rule]
	"""

	# Trend Micro Virus Scan Engine,MatchAll, equal, ""
	# result: ok, bug emtpy should not be allowed
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Engine", "MatchAll", "equal", "")
	security_rule_list=[security_rule]
	"""
	
	# Trend Micro Virus Scan Engine,MatchAll, equal, negative integer
	# result: ok, bug negative number should not be allowed
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Engine", "MatchAll", "equal", "-2.0")
	security_rule_list=[security_rule]
	"""
	

	# Trend Micro Virus Scan Pattern,MatchAll, equal, 1.0
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Pattern", "MatchAll", "equal", "1.0")
	security_rule_list=[security_rule]
	"""
	
	# Trend Micro Virus Scan Pattern,MatchAny, equal, 1.0
	# result: ok, bug should only allow MatchAll
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Pattern", "MatchAny", "equal", "1.0")
	security_rule_list=[security_rule]
	"""

	# Trend Micro Virus Scan Pattern,"", equal, 1.0
	# result: fail,HTTP Error 500: There is an error in XML document (5, 475).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Pattern", "", "equal", "1.0")
	security_rule_list=[security_rule]
	"""

	# Trend Micro Virus Scan Pattern,matchall, equal, 1.0
	# result: fail,HTTP Error 500: There is an error in XML document (5, 483).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Pattern", "matchall", "equal", "1.0")
	security_rule_list=[security_rule]
	"""
	
	# Trend Micro Virus Scan Pattern,random 20 chars, equal, 1.0
	# result: fail,HTTP Error 500: There is an error in XML document (5, 495).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Pattern", mapi_util.random_str(20), "equal", "1.0")
	security_rule_list=[security_rule]
	"""

	# Trend Micro Virus Scan Pattern,MatchAll, equal, 1.0
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Pattern", "MatchAll", "equal", "1.0")
	security_rule_list=[security_rule]
	"""

	# Trend Micro Virus Scan Pattern,MatchAll, notequal, 1.0
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Pattern", "MatchAll", "notequal", "1.0")
	security_rule_list=[security_rule]
	"""

	# Trend Micro Virus Scan Pattern,MatchAll, greaterThan, 1.0
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Pattern", "MatchAll", "greaterThan", "1.0")
	security_rule_list=[security_rule]
	"""

	# Trend Micro Virus Scan Pattern,MatchAll, lessThan, 1.0
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Pattern", "MatchAll", "lessThan", "1.0")
	security_rule_list=[security_rule]
	"""
	

	# Trend Micro Virus Scan Pattern,MatchAll, equalGreaterThan, 1.0
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Pattern", "MatchAll", "equalGreaterThan", "1.0")
	security_rule_list=[security_rule]
	"""
	
	# Trend Micro Virus Scan Pattern,MatchAll, equalLessThan, 1.0
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Pattern", "MatchAll", "equalLessThan", "1.0")
	security_rule_list=[security_rule]
	"""

	# Trend Micro Virus Scan Pattern,MatchAll, information, 1.0
	# result: ok, if information, security rule is not saved
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Pattern", "MatchAll", "information", "1.0")
	security_rule_list=[security_rule]
	"""
	

	# Trend Micro Virus Scan Pattern,MatchAll, Has, 1.0
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Pattern", "MatchAll", "Has", "1.0")
	security_rule_list=[security_rule]
	"""
	
	# Trend Micro Virus Scan Pattern,MatchAll, NotHave, 1.0
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Pattern", "MatchAll", "NotHave", "1.0")
	security_rule_list=[security_rule]
	"""


	# Trend Micro Virus Scan Pattern,MatchAll, Containing, 1.0
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Pattern", "MatchAll", "Containing", "1.0")
	security_rule_list=[security_rule]
	"""

	# Trend Micro Virus Scan Pattern,MatchAll, NotContaining, 1.0
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Pattern", "MatchAll", "NotContaining", "1.0")
	security_rule_list=[security_rule]
	"""


	# Trend Micro Virus Scan Pattern,MatchAll, "", 1.0
	# result: fail,HTTP Error 500: There is an error in XML document (5, 567).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Pattern", "MatchAll", "", "1.0")
	security_rule_list=[security_rule]
	"""


	# Trend Micro Virus Scan Pattern,MatchAll, EQUAL, 1.0
	# result: fail,HTTP Error 500: There is an error in XML document (5, 572).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Pattern", "MatchAll", "EQUAL", "1.0")
	security_rule_list=[security_rule]
	"""


	# Trend Micro Virus Scan Pattern,MatchAll, random 20 chars, 1.0
	# result: fail,HTTP Error 500: There is an error in XML document (5, 587).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Pattern", "MatchAll", mapi_util.random_str(20), "1.0")
	security_rule_list=[security_rule]
	"""
	

	# Trend Micro Virus Scan Pattern,MatchAll, equal, UI max 128
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Pattern", "MatchAll", "equal", mapi_util.random_str(128))
	security_rule_list=[security_rule]
	"""

	# Trend Micro Virus Scan Pattern,MatchAll, equal, UI max 129
	# result: ok, bug UI max is 129
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Pattern", "MatchAll", "equal", mapi_util.random_str(129))
	security_rule_list=[security_rule]
	"""
	

	# Trend Micro Virus Scan Pattern,MatchAll, equal, db max 4000
	# result: ok, bug UI max is 128
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Pattern", "MatchAll", "equal", mapi_util.random_str(4000))
	security_rule_list=[security_rule]
	"""


	# Trend Micro Virus Scan Pattern,MatchAll, equal, db max 4001
	# result: ok, bug UI max is 128 and extra char is truncated
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Pattern", "MatchAll", "equal", mapi_util.random_str(4001))
	security_rule_list=[security_rule]
	"""


	# Trend Micro Virus Scan Pattern,MatchAll, equal, non-integer
	# result: ok, bug should only allow digits and dot
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Pattern", "MatchAll", "equal", "aaabbbccc")
	security_rule_list=[security_rule]
	"""


	# Trend Micro Virus Scan Pattern,MatchAll, equal, ""
	# result: ok, bug empty should not be allowed
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Pattern", "MatchAll", "equal", "")
	security_rule_list=[security_rule]
	"""
	
	# Trend Micro Virus Scan Pattern,MatchAll, equal, negative integer
	# result: ok, bug negative number should not be allowed
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Trend Micro Virus Scan Pattern", "MatchAll", "equal", "-2.0")
	security_rule_list=[security_rule]
	"""

	# Guest OS Type,MatchAll, equal, Linux
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Type", "MatchAll", "equal", "Linux")
	security_rule_list=[security_rule]
	"""
	

	# Guest OS Type,MatchAll, equal, Windows
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Type", "MatchAll", "equal", "Windows")
	security_rule_list=[security_rule]
	"""

	# Guest OS Type,MatchAny, equal, Linux
	# result: ok, bug should only allow MatchAll
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Type", "MatchAny", "equal", "Linux")
	security_rule_list=[security_rule]
	"""
	

	# Guest OS Type,"", equal, Linux
	# result: fail,HTTP Error 500: There is an error in XML document (5, 475).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Type", "", "equal", "Linux")
	security_rule_list=[security_rule]
	"""

	# Guest OS Type,matchall, equal, Linux
	# result: fail,HTTP Error 500: There is an error in XML document (5, 483).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Type", "matchall", "equal", "Linux")
	security_rule_list=[security_rule]
	"""
	

	# Guest OS Type,random 20 chars, equal, Linux
	# result: fail,HTTP Error 500: There is an error in XML document (5, 495).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Type", mapi_util.random_str(20), "equal", "Linux")
	security_rule_list=[security_rule]
	"""

	# Guest OS Type,MatchAll, notequal,  Linux
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Type", "MatchAll", "notequal", "Linux")
	security_rule_list=[security_rule]
	"""
	
	# Guest OS Type,MatchAll, notequal,  Windows
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Type", "MatchAll", "notequal", "Windows")
	security_rule_list=[security_rule]
	"""

	# Guest OS Type,MatchAll, greaterThan,  Linux
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Type", "MatchAll", "greaterThan", "Linux")
	security_rule_list=[security_rule]
	"""

	# Guest OS Type,MatchAll, lessThan,  Linux
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Type", "MatchAll", "lessThan", "Linux")
	security_rule_list=[security_rule]
	"""


	# Guest OS Type,MatchAll, equalGreaterThan,  Linux
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Type", "MatchAll", "equalGreaterThan", "Linux")
	security_rule_list=[security_rule]
	"""


	# Guest OS Type,MatchAll, equalLessThan,  Linux
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Type", "MatchAll", "equalLessThan", "Linux")
	security_rule_list=[security_rule]
	"""


	# Guest OS Type,MatchAll, information,  Linux
	# result: ok, if information, security rule is not saved
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Type", "MatchAll", "information", "Linux")
	security_rule_list=[security_rule]
	"""
	
	# Guest OS Type,MatchAll, Has,  Linux
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Type", "MatchAll", "Has", "Linux")
	security_rule_list=[security_rule]
	"""

	# Guest OS Type,MatchAll, NotHave,  Linux
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Type", "MatchAll", "NotHave", "Linux")
	security_rule_list=[security_rule]
	"""

	# Guest OS Type,MatchAll, Containing,  Linux
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Type", "MatchAll", "Containing", "Linux")
	security_rule_list=[security_rule]
	"""

	# Guest OS Type,MatchAll, NotContaining,  Linux
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Type", "MatchAll", "NotContaining", "Linux")
	security_rule_list=[security_rule]
	"""
	
	# Guest OS Type,MatchAll, "",  Linux
	# result: fail,HTTP Error 500: There is an error in XML document (5, 569).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Type", "MatchAll", "", "Linux")
	security_rule_list=[security_rule]
	"""

	# Guest OS Type,MatchAll, EQUAL,  Linux
	# result: fail,HTTP Error 500: There is an error in XML document (5, 574).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Type", "MatchAll", "EQUAL", "Linux")
	security_rule_list=[security_rule]
	"""

	# Guest OS Type,MatchAll, random 20 char,  Linux
	# result: fail,HTTP Error 500: There is an error in XML document (5, 589).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Type", "MatchAll", mapi_util.random_str(20), "Linux")
	security_rule_list=[security_rule]
	"""
	
	# Guest OS Type,MatchAll, equal, ""
	# result: ok, bug empty should not be allowed
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Type", "MatchAll", "equal", "")
	security_rule_list=[security_rule]
	"""

	# Guest OS Type,MatchAll, equal, random 4000 
	# result: ok, bug should only allow value Linux/Windows
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Type", "MatchAll", "equal", mapi_util.random_str(4000))
	security_rule_list=[security_rule]
	"""
	
	# Guest OS Type,MatchAll, equal, random 4000+1
	# result: ok, bug bug should only allow value Linux/Windows
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Type", "MatchAll", "equal", mapi_util.random_str(4001))
	security_rule_list=[security_rule]
	"""
	
	# Guest OS Type,MatchAll, equal, linux (case sensitive)
	# result: ok, bug should be case sensitive
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Type", "MatchAll", "equal", "linux")
	security_rule_list=[security_rule]
	"""


	# Guest OS Architecture,MatchAll, equal, 32bit
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Architecture", "MatchAll", "equal", "32bit")
	security_rule_list=[security_rule]
	"""
	
	# Guest OS Architecture,MatchAll, equal, 64bit
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Architecture", "MatchAll", "equal", "64bit")
	security_rule_list=[security_rule]
	"""

	# Guest OS Architecture,MatchAny, equal, 32bit
	# result: ok, bug should only allow MatchAll
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Architecture", "MatchAny", "equal", "32bit")
	security_rule_list=[security_rule]
	"""

	# Guest OS Architecture,"", equal, 32bit
	# result: fail,HTTP Error 500: There is an error in XML document (5, 475).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Architecture", "", "equal", "32bit")
	security_rule_list=[security_rule]
	"""
	
	# Guest OS Architecture,matchall, equal, 32bit
	# result: fail,HTTP Error 500: There is an error in XML document (5, 483).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Architecture", "matchall", "equal", "32bit")
	security_rule_list=[security_rule]
	"""

	# Guest OS Architecture,random 20 chars, equal, 32bit
	# result: fail,HTTP Error 500: There is an error in XML document (5, 495).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Architecture", mapi_util.random_str(20), "equal", "32bit")
	security_rule_list=[security_rule]
	"""

	# Guest OS Architecture,MatchAll, notequal,  32bit
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Architecture", "MatchAll", "notequal", "32bit")
	security_rule_list=[security_rule]
	"""

	# Guest OS Architecture,MatchAll, notequal,  64bit
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Architecture", "MatchAll", "notequal", "64bit")
	security_rule_list=[security_rule]
	"""

	# Guest OS Architecture,MatchAll, greaterThan,  32bit
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Architecture", "MatchAll", "greaterThan", "32bit")
	security_rule_list=[security_rule]
	"""
	

	# Guest OS Architecture,MatchAll, lessThan,  32bit
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Architecture", "MatchAll", "lessThan", "32bit")
	security_rule_list=[security_rule]
	"""
	
	# Guest OS Architecture,MatchAll, equalGreaterThan,  32bit
	# result: ok, bug not a valid option

	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Architecture", "MatchAll", "equalGreaterThan", "32bit")
	security_rule_list=[security_rule]
	"""
	
	# Guest OS Architecture,MatchAll, equalLessThan,  32bit
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Architecture", "MatchAll", "equalLessThan", "32bit")
	security_rule_list=[security_rule]
	"""

	# Guest OS Architecture,MatchAll, information,  32bit
	# result: ok, if information, security rule is not saved
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Architecture", "MatchAll", "information", "32bit")
	security_rule_list=[security_rule]
	"""
	
	# Guest OS Architecture,MatchAll, Has,  32bit
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Architecture", "MatchAll", "Has", "32bit")
	security_rule_list=[security_rule]
	"""

	# Guest OS Architecture,MatchAll, NotHave,  32bit
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Architecture", "MatchAll", "NotHave", "32bit")
	security_rule_list=[security_rule]
	"""

	# Guest OS Architecture,MatchAll, Containing,  32bit
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Architecture", "MatchAll", "Containing", "32bit")
	security_rule_list=[security_rule]
	"""

	# Guest OS Architecture,MatchAll, NotContaining,  32bit
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Architecture", "MatchAll", "NotContaining", "32bit")
	security_rule_list=[security_rule]
	"""

	# Guest OS Architecture,MatchAll, "",  32bit
	# result: fail,HTTP Error 500: There is an error in XML document (5, 569).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Architecture", "MatchAll", "", "32bit")
	security_rule_list=[security_rule]
	"""

	# Guest OS Architecture,MatchAll, EQUAL,  32bit
	# result: fail,HTTP Error 500: There is an error in XML document (5, 574).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Architecture", "MatchAll", "EQUAL", "32bit")
	security_rule_list=[security_rule]
	"""

	# Guest OS Architecture,MatchAll, random 20 chars,  32bit
	# result: fail,HTTP Error 500: There is an error in XML document (5, 589).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Architecture", "MatchAll", mapi_util.random_str(20), "32bit")
	security_rule_list=[security_rule]
	"""

	# Guest OS Architecture,MatchAll, equal, ""
	# result: ok, bug empty should not be allowed
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Architecture", "MatchAll", "equal", "")
	security_rule_list=[security_rule]
	"""

	# Guest OS Architecture,MatchAll, equal, random 4000 
	# result: pass, bug should only allow value 32bit/64bit
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Architecture", "MatchAll", "equal", mapi_util.random_str(4000))
	security_rule_list=[security_rule]
	"""

	# Guest OS Architecture,MatchAll, equal, random 4000+1
	# result: pass, bug should only allow value 32bit/64bit and extra chars are truncated
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Architecture", "MatchAll", "equal", mapi_util.random_str(4001))
	security_rule_list=[security_rule]
	"""

	# Guest OS Architecture,MatchAll, equal, 32BIT case sensitive
	# result: pass, bug should be case sensitive
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Guest OS Architecture", "MatchAll", "equal", "32BIT")
	security_rule_list=[security_rule]
	"""
	
	# Guest OS Architecture,MatchAll, equal, special chars
	# result: fail



	# Deep Security Status,MatchAll, equal, Green
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Status", "MatchAll", "equal", "Green")
	security_rule_list=[security_rule]
	"""

	# Deep Security Status,MatchAll, equal, Blue
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Status", "MatchAll", "equal", "Blue")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Status,MatchAll, equal, Red
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Status", "MatchAll", "equal", "Red")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Status,MatchAny, equal, Green
	# result: ok, bug should only allow MatchAll
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Status", "MatchAny", "equal", "Green")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Status,"", equal, Green
	# result: fail,HTTP Error 500: There is an error in XML document (5, 475).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Status", "", "equal", "Green")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Status,matchall, equal, Green
	# result: fail,HTTP Error 500: There is an error in XML document (5, 483).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Status", "matchall", "equal", "Green")
	security_rule_list=[security_rule]
	"""

	# Deep Security Status,random 20 chars, equal, Green
	# result: fail,HTTP Error 500: There is an error in XML document (5, 495).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Status", mapi_util.random_str(20), "equal", "Green")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Status,MatchAll, notequal,  Green
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Status", "MatchAll", "notequal", "Green")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Status,MatchAll, notequal,  Blue
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Status", "MatchAll", "notequal", "Blue")
	security_rule_list=[security_rule]
	"""


	# Deep Security Status,MatchAll, notequal,  Red
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Status", "MatchAll", "notequal", "Red")
	security_rule_list=[security_rule]
	"""

	# Deep Security Status,MatchAll, greaterThan,  Green
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Status", "MatchAll", "greaterThan", "Green")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Status,MatchAll, lessThan,  Green
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Status", "MatchAll", "lessThan", "Green")
	security_rule_list=[security_rule]
	"""
	

	# Deep Security Status,MatchAll, equalGreaterThan,  Green
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Status", "MatchAll", "equalGreaterThan", "Green")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Status,MatchAll, equalLessThan,  Green
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Status", "MatchAll", "equalLessThan", "Green")
	security_rule_list=[security_rule]
	"""

	# Deep Security Status,MatchAll, information,  Green
	# result: ok, if information, security is not saved
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Status", "MatchAll", "information", "Green")
	security_rule_list=[security_rule]
	"""

	# Deep Security Status,MatchAll, Has,  Green
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Status", "MatchAll", "Has", "Green")
	security_rule_list=[security_rule]
	"""

	# Deep Security Status,MatchAll, NotHave,  Green
	# result: ok, not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Status", "MatchAll", "NotHave", "Green")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Status,MatchAll, Containing,  Green
	# result: ok, not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Status", "MatchAll", "Containing", "Green")
	security_rule_list=[security_rule]
	"""

	# Deep Security Status,MatchAll, NotContaining,  Green
	# result: ok, not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Status", "MatchAll", "NotContaining", "Green")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Status,MatchAll, "",  Green
	# result: fail,HTTP Error 500: There is an error in XML document (5, 569).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Status", "MatchAll", "", "Green")
	security_rule_list=[security_rule]
	"""

	# Deep Security Status,MatchAll, EQUAL,  Green
	# result: fail,HTTP Error 500: There is an error in XML document (5, 574).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Status", "MatchAll", "EQUAL", "Green")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Status,MatchAll, random 20 chars,  Green
	# result: fail,HTTP Error 500: There is an error in XML document (5, 589).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Status", "MatchAll", mapi_util.random_str(20), "Green")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Status,MatchAll, equal, ""
	# result: ok, empty should not be allowed
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Status", "MatchAll", "equal", "")
	security_rule_list=[security_rule]
	"""

	# Deep Security Status,MatchAll, equal, random 4000 
	# result: ok, bug only specified values should be allowed
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Status", "MatchAll", "equal", mapi_util.random_str(4000))
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Status,MatchAll, equal, random 4000+1
	# result: ok, bug extra chars are truncated and only specified values should be allowed
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Status", "MatchAll", "equal", mapi_util.random_str(4000))
	security_rule_list=[security_rule]
	"""
	

	# Deep Security Status,MatchAll, equal, GREEN case sensitive
	# result: ok, bug should be case sensitive
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Status", "MatchAll", "equal", "GREEN")
	security_rule_list=[security_rule]
	"""


	# Deep Security Anti-Malware Status,MatchAll, equal, NotCapable
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Anti-Malware Status", "MatchAll", "equal", "NotCapable")
	security_rule_list=[security_rule]
	"""

	# Deep Security Anti-Malware Status,MatchAll, equal, On
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Anti-Malware Status", "MatchAll", "equal", "On")
	security_rule_list=[security_rule]
	"""

	# Deep Security Anti-Malware Status,MatchAll, equal, Off
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Anti-Malware Status", "MatchAll", "equal", "Off")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Anti-Malware Status,MatchAny, equal, NotCapable
	# result: ok, bug should only allow MatchAll
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Anti-Malware Status", "MatchAny", "equal", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Anti-Malware Status,"", equal, NotCapable
	# result: fail,HTTP Error 500: There is an error in XML document (5, 475).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Anti-Malware Status", "", "equal", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Anti-Malware Status,matchall, equal, NotCapable
	# result: fail,HTTP Error 500: There is an error in XML document (5, 483).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Anti-Malware Status", "matchall", "equal", "NotCapable")
	security_rule_list=[security_rule]
	"""

	# Deep Security Anti-Malware Status,random 20 chars, equal, NotCapable
	# result: fail,HTTP Error 500: There is an error in XML document (5, 495).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Anti-Malware Status", mapi_util.random_str(20), "equal", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Anti-Malware Status,MatchAll, notequal,  NotCapable
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Anti-Malware Status", "MatchAll", "notequal", "NotCapable")
	security_rule_list=[security_rule]
	"""

	# Deep Security Anti-Malware Status,MatchAll, notequal,  On
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Anti-Malware Status", "MatchAll", "notequal", "On")
	security_rule_list=[security_rule]
	"""

	# Deep Security Anti-Malware Status,MatchAll, notequal,  Off
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Anti-Malware Status", "MatchAll", "notequal", "Off")
	security_rule_list=[security_rule]
	"""

	# Deep Security Anti-Malware Status,MatchAll, greaterThan,  NotCapable
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Anti-Malware Status", "MatchAll", "greaterThan", "NotCapable")
	security_rule_list=[security_rule]
	"""
	

	# Deep Security Anti-Malware Status,MatchAll, lessThan,  NotCapable
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Anti-Malware Status", "MatchAll", "lessThan", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Anti-Malware Status,MatchAll, equalGreaterThan,  NotCapable
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Anti-Malware Status", "MatchAll", "equalGreaterThan", "NotCapable")
	security_rule_list=[security_rule]
	"""

	# Deep Security Anti-Malware Status,MatchAll, equalLessThan,  NotCapable
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Anti-Malware Status", "MatchAll", "equalLessThan", "NotCapable")
	security_rule_list=[security_rule]
	"""

	# Deep Security Anti-Malware Status,MatchAll, information,  NotCapable
	# result: ok, if information, security rule is not saved
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Anti-Malware Status", "MatchAll", "information", "NotCapable")
	security_rule_list=[security_rule]
	"""

	# Deep Security Anti-Malware Status,MatchAll, Has,  NotCapable
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Anti-Malware Status", "MatchAll", "Has", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Anti-Malware Status,MatchAll, NotHave,  NotCapable
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Anti-Malware Status", "MatchAll", "NotHave", "NotCapable")
	security_rule_list=[security_rule]
	"""

	# Deep Security Anti-Malware Status,MatchAll, Containing,  NotCapable
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Anti-Malware Status", "MatchAll", "Containing", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Anti-Malware Status,MatchAll, NotContaining,  NotCapable
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Anti-Malware Status", "MatchAll", "NotContaining", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Anti-Malware Status,MatchAll, "",  NotCapable
	# result: fail,HTTP Error 500: There is an error in XML document (5, 574).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Anti-Malware Status", "MatchAll", "", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Anti-Malware Status,MatchAll, EQUAL,  NotCapable
	# result: fail,HTTP Error 500: There is an error in XML document (5, 579).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Anti-Malware Status", "MatchAll", "EQUAL", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Anti-Malware Status,MatchAll, random 20 chars,  NotCapable
	# result: fail,HTTP Error 500: There is an error in XML document (5, 594).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Anti-Malware Status", "MatchAll", mapi_util.random_str(20), "NotCapable")
	security_rule_list=[security_rule]
	"""

	# Deep Security Anti-Malware Status,MatchAll, equal, ""
	# result: ok, bug empty should be be allowed
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Anti-Malware Status", "MatchAll", "equal", "")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Anti-Malware Status,MatchAll, equal, random 4000 
	# result: ok, bug not a valid value
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Anti-Malware Status", "MatchAll", "equal", mapi_util.random_str(4000))
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Anti-Malware Status,MatchAll, equal, random 4000+1
	# result: ok,bug extra chars are truncated and values are not valid
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Anti-Malware Status", "MatchAll", "equal", mapi_util.random_str(4001))
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Anti-Malware Status,MatchAll, equal, on (case sensitive)
	# result: ok,bug should be case sensitive
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Anti-Malware Status", "MatchAll", "equal", "on")
	security_rule_list=[security_rule]
	"""


	# Deep Security Web Reputation Status,MatchAll, equal, NotCapable
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Web Reputation Status", "MatchAll", "equal", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Web Reputation Status,MatchAll, equal, On
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Web Reputation Status", "MatchAll", "equal", "On")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Web Reputation Status,MatchAll, equal, Off
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Web Reputation Status", "MatchAll", "equal", "Off")
	security_rule_list=[security_rule]
	"""

	# Deep Security Web Reputation Status,MatchAny, equal, NotCapable
	# result: ok, bug should only allow MatchAll
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Web Reputation Status", "MatchAny", "equal", "NotCapable")
	security_rule_list=[security_rule]
	"""

	# Deep Security Web Reputation Status,"", equal, NotCapable
	# result: fail,HTTP Error 500: There is an error in XML document (5, 475).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Web Reputation Status", "", "equal", "NotCapable")
	security_rule_list=[security_rule]
	"""

	# Deep Security Web Reputation Status,matchall, equal, NotCapable
	# result: fail,HTTP Error 500: There is an error in XML document (5, 483).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Web Reputation Status", "matchall", "equal", "NotCapable")
	security_rule_list=[security_rule]
	"""

	# Deep Security Web Reputation Status,random 20 chars, equal, NotCapable
	# result: fail,HTTP Error 500: There is an error in XML document (5, 495).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Web Reputation Status", mapi_util.random_str(20), "equal", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Web Reputation Status,MatchAll, notequal,  NotCapable
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Web Reputation Status", "MatchAll", "notequal", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Web Reputation Status,MatchAll, notequal,  On
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Web Reputation Status", "MatchAll", "notequal", "On")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Web Reputation Status,MatchAll, notequal,  Off
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Web Reputation Status", "MatchAll", "notequal", "Off")
	security_rule_list=[security_rule]
	"""

	# Deep Security Web Reputation Status,MatchAll, greaterThan,  NotCapable
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Web Reputation Status", "MatchAll", "greaterThan", "NotCapable")
	security_rule_list=[security_rule]
	"""

	# Deep Security Web Reputation Status,MatchAll, lessThan,  NotCapable
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Web Reputation Status", "MatchAll", "lessThan", "NotCapable")
	security_rule_list=[security_rule]
	"""

	# Deep Security Web Reputation Status,MatchAll, equalGreaterThan,  NotCapable
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Web Reputation Status", "MatchAll", "equalGreaterThan", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Web Reputation Status,MatchAll, equalLessThan,  NotCapable
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Web Reputation Status", "MatchAll", "equalLessThan", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Web Reputation Status,MatchAll, information,  NotCapable
	# result: ok, if information, security rule is not saved
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Web Reputation Status", "MatchAll", "information", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Web Reputation Status,MatchAll, Has,  NotCapable
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Web Reputation Status", "MatchAll", "Has", "NotCapable")
	security_rule_list=[security_rule]
	"""


	# Deep Security Web Reputation Status,MatchAll, NotHave,  NotCapable
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Web Reputation Status", "MatchAll", "NotHave", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Web Reputation Status,MatchAll, Containing,  NotCapable
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Web Reputation Status", "MatchAll", "Containing", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Web Reputation Status,MatchAll, NotContaining,  NotCapable
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Web Reputation Status", "MatchAll", "NotContaining", "NotCapable")
	security_rule_list=[security_rule]
	"""

	# Deep Security Web Reputation Status,MatchAll, "",  NotCapable
	# result: fail,HTTP Error 500: There is an error in XML document (5, 574).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Web Reputation Status", "MatchAll", "", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Web Reputation Status,MatchAll, EQUAL,  NotCapable
	# result: fail,HTTP Error 500: There is an error in XML document (5, 579).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Web Reputation Status", "MatchAll", "EQUAL", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Web Reputation Status,MatchAll, random 20 chars,  NotCapable
	# result: fail,HTTP Error 500: There is an error in XML document (5, 594).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Web Reputation Status", "MatchAll", mapi_util.random_str(20), "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Web Reputation Status,MatchAll, equal, ""
	# result: ok, bug empty should not be allowed
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Web Reputation Status", "MatchAll", "equal", "")
	security_rule_list=[security_rule]
	"""

	# Deep Security Web Reputation Status,MatchAll, equal, random 4000 
	# result: ok, bug only specified values should be allowed
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Web Reputation Status", "MatchAll", "equal", mapi_util.random_str(4000))
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Web Reputation Status,MatchAll, equal, random 4000+1
	# result: ok, bug only specified values should be allowed and extra chars are truncated
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Web Reputation Status", "MatchAll", "equal", mapi_util.random_str(4001))
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Web Reputation Status,MatchAll, equal, on (case sensitive)
	# result: ok, bug should be case sensitive
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Web Reputation Status", "MatchAll", "equal", "on")
	security_rule_list=[security_rule]
	"""
	



	# Deep Security Firewall Status,MatchAll, equal, NotCapable
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Firewall Status", "MatchAll", "equal", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Firewall Status,MatchAll, equal, On
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Firewall Status", "MatchAll", "equal", "On")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Firewall Status,MatchAll, equal, Off
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Firewall Status", "MatchAll", "equal", "Off")
	security_rule_list=[security_rule]
	"""
	

	# Deep Security Firewall Status,MatchAny, equal, NotCapable
	# result: ok, bug should only allow MatchAll
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Firewall Status", "MatchAny", "equal", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Firewall Status,"", equal, NotCapable
	# result: fail,HTTP Error 500: There is an error in XML document (5, 475).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Firewall Status", "", "equal", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Firewall Status,matchall, equal, NotCapable
	# result: fail,HTTP Error 500: There is an error in XML document (5, 483).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Firewall Status", "matchall", "equal", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Firewall Status,random 20 chars, equal, NotCapable
	# result: fail,HTTP Error 500: There is an error in XML document (5, 495).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Firewall Status", mapi_util.random_str(20), "equal", "NotCapable")
	security_rule_list=[security_rule]
	"""

	# Deep Security Firewall Status,MatchAll, notequal,  NotCapable
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Firewall Status", "MatchAll", "notequal", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Firewall Status,MatchAll, notequal,  On
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Firewall Status", "MatchAll", "notequal", "On")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Firewall Status,MatchAll, notequal,  Off
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Firewall Status", "MatchAll", "notequal", "Off")
	security_rule_list=[security_rule]
	"""

	# Deep Security Firewall Status,MatchAll, greaterThan,  NotCapable
	# result: ok, not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Firewall Status", "MatchAll", "greaterThan", "NotCapable")
	security_rule_list=[security_rule]
	"""


	# Deep Security Firewall Status,MatchAll, lessThan,  NotCapable
	# result: ok, not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Firewall Status", "MatchAll", "lessThan", "NotCapable")
	security_rule_list=[security_rule]
	"""

	# Deep Security Firewall Status,MatchAll, equalGreaterThan,  NotCapable
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Firewall Status", "MatchAll", "equalGreaterThan", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Firewall Status,MatchAll, equalLessThan,  NotCapable
	# result: ok, not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Firewall Status", "MatchAll", "equalLessThan", "NotCapable")
	security_rule_list=[security_rule]
	"""

	# Deep Security Firewall Status,MatchAll, information,  NotCapable
	# result: ok, if information, security rule is not saved
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Firewall Status", "MatchAll", "information", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Firewall Status,MatchAll, Has,  NotCapable
	# result: ok, not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Firewall Status", "MatchAll", "Has", "NotCapable")
	security_rule_list=[security_rule]
	"""

	# Deep Security Firewall Status,MatchAll, NotHave,  NotCapable
	# result: ok, not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Firewall Status", "MatchAll", "NotHave", "NotCapable")
	security_rule_list=[security_rule]
	"""

	# Deep Security Firewall Status,MatchAll, Containing,  NotCapable
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Firewall Status", "MatchAll", "Containing", "NotCapable")
	security_rule_list=[security_rule]
	"""

	# Deep Security Firewall Status,MatchAll, NotContaining,  NotCapable
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Firewall Status", "MatchAll", "NotContaining", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Firewall Status,MatchAll, "",  NotCapable
	# result: fail,HTTP Error 500: There is an error in XML document (5, 574).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Firewall Status", "MatchAll", "", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Firewall Status,MatchAll, EQUAL,  NotCapable
	# result: fail,HTTP Error 500: There is an error in XML document (5, 579).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Firewall Status", "MatchAll", "EQUAL", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Firewall Status,MatchAll, random 20 chars,  NotCapable
	# result: fail,HTTP Error 500: There is an error in XML document (5, 594).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Firewall Status", "MatchAll", mapi_util.random_str(20), "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Firewall Status,MatchAll, equal, ""
	# result: ok, bug empty should not be allowed
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Firewall Status", "MatchAll", "equal", "")
	security_rule_list=[security_rule]
	"""

	# Deep Security Firewall Status,MatchAll, equal, random 4000 
	# result: ok, bug only specified values should be allowed
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Firewall Status", "MatchAll", "equal", mapi_util.random_str(4000))
	security_rule_list=[security_rule]
	"""

	# Deep Security Firewall Status,MatchAll, equal, random 4000+1
	# result: ok, bug only specified values should be allowed and extra chars are truncated
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Firewall Status", "MatchAll", "equal", mapi_util.random_str(4001))
	security_rule_list=[security_rule]
	"""
	

	# Deep Security Firewall Status,MatchAll, equal, on (case sensitive)
	# result: ok, bug should be case sensitive
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Firewall Status", "MatchAll", "equal", "on")
	security_rule_list=[security_rule]
	"""
	

	# Deep Security DPI Status,MatchAll, equal, NotCapable
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security DPI Status", "MatchAll", "equal", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security DPI Status,MatchAll, equal, Detect
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security DPI Status", "MatchAll", "equal", "Detect")
	security_rule_list=[security_rule]
	"""

	# Deep Security DPI Status,MatchAll, equal, Prevent
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security DPI Status", "MatchAll", "equal", "Prevent")
	security_rule_list=[security_rule]
	"""

	# Deep Security DPI Status,MatchAll, equal, Off
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security DPI Status", "MatchAll", "equal", "Off")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security DPI Status,MatchAny, equal, NotCapable
	# result: ok, should only allow MatchAll
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security DPI Status", "MatchAny", "equal", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security DPI Status,"", equal, NotCapable
	# result: fail,HTTP Error 500: There is an error in XML document (5, 475).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security DPI Status", "", "equal", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security DPI Status,random 20 chars, equal, NotCapable
	# result: fail,HTTP Error 500: There is an error in XML document (5, 495).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security DPI Status", mapi_util.random_str(20), "equal", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security DPI Status,MatchAll, notequal,  NotCapable
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security DPI Status", "MatchAll", "notequal", "NotCapable")
	security_rule_list=[security_rule]
	"""

	# Deep Security DPI Status,MatchAll, notequal,  Detect
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security DPI Status", "MatchAll", "notequal", "Detect")
	security_rule_list=[security_rule]
	"""

	# Deep Security DPI Status,MatchAll, notequal,  Prevent
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security DPI Status", "MatchAll", "notequal", "Prevent")
	security_rule_list=[security_rule]
	"""

	# Deep Security DPI Status,MatchAll, notequal,  Off
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security DPI Status", "MatchAll", "notequal", "Off")
	security_rule_list=[security_rule]
	"""

	# Deep Security DPI Status,MatchAll, greaterThan,  NotCapable
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security DPI Status", "MatchAll", "greaterThan", "NotCapable")
	security_rule_list=[security_rule]
	"""

	# Deep Security DPI Status,MatchAll, lessThan,  NotCapable
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security DPI Status", "MatchAll", "lessThan", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security DPI Status,MatchAll, equalGreaterThan,  NotCapable
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security DPI Status", "MatchAll", "equalGreaterThan", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security DPI Status,MatchAll, equalLessThan,  NotCapable
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security DPI Status", "MatchAll", "equalLessThan", "NotCapable")
	security_rule_list=[security_rule]
	"""


	# Deep Security DPI Status,MatchAll, information,  NotCapable
	# result: ok, if information, security rule is not saved
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security DPI Status", "MatchAll", "information", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security DPI Status,MatchAll, Has,  NotCapable
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security DPI Status", "MatchAll", "Has", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security DPI Status,MatchAll, NotHave,  NotCapable
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security DPI Status", "MatchAll", "NotHave", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security DPI Status,MatchAll, Containing,  NotCapable
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security DPI Status", "MatchAll", "Containing", "NotCapable")
	security_rule_list=[security_rule]
	"""

	# Deep Security DPI Status,MatchAll, NotContaining,  NotCapable
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security DPI Status", "MatchAll", "NotContaining", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security DPI Status,MatchAll, "",  NotCapable
	# result: fail,HTTP Error 500: There is an error in XML document (5, 574).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security DPI Status", "MatchAll", "", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security DPI Status,MatchAll, EQUAL,  NotCapable
	# result: fail,HTTP Error 500: There is an error in XML document (5, 579).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security DPI Status", "MatchAll", "EQUAL", "NotCapable")
	security_rule_list=[security_rule]
	"""

	# Deep Security DPI Status,MatchAll, random 20 chars,  NotCapable
	# result: fail,HTTP Error 500: There is an error in XML document (5, 594).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security DPI Status", "MatchAll", mapi_util.random_str(20), "NotCapable")
	security_rule_list=[security_rule]
	"""

	# Deep Security DPI Status,MatchAll, equal, ""
	# result: ok, bug empty should not be allowed
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security DPI Status", "MatchAll", "equal", "")
	security_rule_list=[security_rule]
	"""

	# Deep Security DPI Status,MatchAll, equal, random 4000 
	# result: ok, bug should only allow specific values
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security DPI Status", "MatchAll", "equal", mapi_util.random_str(4000))
	security_rule_list=[security_rule]
	"""

	# Deep Security DPI Status,MatchAll, equal, random 4000+1
	# result: ok, bug should only allow specific values and extra chars are truncated
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security DPI Status", "MatchAll", "equal", mapi_util.random_str(4001))
	security_rule_list=[security_rule]
	"""


	# Deep Security DPI Status,MatchAll, equal, off
	# result: ok, bug should be case sensitive
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security DPI Status", "MatchAll", "equal", "off")
	security_rule_list=[security_rule]
	"""
	



	# Deep Security Integrity Monitoring Status,MatchAll, equal, NotCapable
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Integrity Monitoring Status", "MatchAll", "equal", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Integrity Monitoring Status,MatchAll, equal, On
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Integrity Monitoring Status", "MatchAll", "equal", "On")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Integrity Monitoring Status,MatchAll, equal, Off
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Integrity Monitoring Status", "MatchAll", "equal", "Off")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Integrity Monitoring Status,MatchAll, equal, Real-time
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Integrity Monitoring Status", "MatchAll", "equal", "Real-time")
	security_rule_list=[security_rule]
	"""

	# Deep Security Integrity Monitoring Status,MatchAny, equal, NotCapable
	# result: ok, bug should only allow MatchAll
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Integrity Monitoring Status", "MatchAny", "equal", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Integrity Monitoring Status,"", equal, NotCapable
	# result: fail,HTTP Error 500: There is an error in XML document (5, 475).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Integrity Monitoring Status", "", "equal", "NotCapable")
	security_rule_list=[security_rule]
	"""

	# Deep Security Integrity Monitoring Status,matchall, equal, NotCapable
	# result: fail,HTTP Error 500: There is an error in XML document (5, 483).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Integrity Monitoring Status", "matchall", "equal", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Integrity Monitoring Status,random 20 chars, equal, NotCapable
	# result: fail,HTTP Error 500: There is an error in XML document (5, 495).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Integrity Monitoring Status", mapi_util.random_str(20), "equal", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Integrity Monitoring Status,MatchAll, notequal,  NotCapable
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Integrity Monitoring Status", "MatchAll", "notequal", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Integrity Monitoring Status,MatchAll, notequal,  On
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Integrity Monitoring Status", "MatchAll", "notequal", "On")
	security_rule_list=[security_rule]
	"""


	# Deep Security Integrity Monitoring Status,MatchAll, notequal,  Off
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Integrity Monitoring Status", "MatchAll", "notequal", "Off")
	security_rule_list=[security_rule]
	"""

	# Deep Security Integrity Monitoring Status,MatchAll, notequal,  Real-time
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Integrity Monitoring Status", "MatchAll", "notequal", "Real-time")
	security_rule_list=[security_rule]
	"""


	# Deep Security Integrity Monitoring Status,MatchAll, greaterThan,  NotCapable
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Integrity Monitoring Status", "MatchAll", "greaterThan", "NotCapable")
	security_rule_list=[security_rule]
	"""

	# Deep Security Integrity Monitoring Status,MatchAll, lessThan,  NotCapable
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Integrity Monitoring Status", "MatchAll", "lessThan", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Integrity Monitoring Status,MatchAll, equalGreaterThan,  NotCapable
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Integrity Monitoring Status", "MatchAll", "equalGreaterThan", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Integrity Monitoring Status,MatchAll, equalLessThan,  NotCapable
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Integrity Monitoring Status", "MatchAll", "equalLessThan", "NotCapable")
	security_rule_list=[security_rule]
	"""


	# Deep Security Integrity Monitoring Status,MatchAll, information,  NotCapable
	# result: ok, if information, security rule is not saved
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Integrity Monitoring Status", "MatchAll", "information", "NotCapable")
	security_rule_list=[security_rule]
	"""

	# Deep Security Integrity Monitoring Status,MatchAll, Has,  NotCapable
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Integrity Monitoring Status", "MatchAll", "Has", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Integrity Monitoring Status,MatchAll, NotHave,  NotCapable
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Integrity Monitoring Status", "MatchAll", "NotHave", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Integrity Monitoring Status,MatchAll, Containing,  NotCapable
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Integrity Monitoring Status", "MatchAll", "Containing", "NotCapable")
	security_rule_list=[security_rule]
	"""


	# Deep Security Integrity Monitoring Status,MatchAll, NotContaining,  NotCapable
	# result: fail
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Integrity Monitoring Status", "MatchAll", "NotContaining", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Integrity Monitoring Status,MatchAll, "",  NotCapable
	# result: fail,HTTP Error 500: There is an error in XML document (5, 574).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Integrity Monitoring Status", "MatchAll", "", "NotCapable")
	security_rule_list=[security_rule]
	"""

	# Deep Security Integrity Monitoring Status,MatchAll, EQUAL,  NotCapable
	# result: fail,HTTP Error 500: There is an error in XML document (5, 579).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Integrity Monitoring Status", "MatchAll", "EQUAL", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Integrity Monitoring Status,MatchAll, random 20 chars,  NotCapable
	# result: fail,HTTP Error 500: There is an error in XML document (5, 594).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Integrity Monitoring Status", "MatchAll", mapi_util.random_str(20), "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Integrity Monitoring Status,MatchAll, equal, ""
	# result: ok, bug empty should not be allowed
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Integrity Monitoring Status", "MatchAll", "equal", "")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Integrity Monitoring Status,MatchAll, equal, random 4000 
	# result: ok, bug should only allow specific values
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Integrity Monitoring Status", "MatchAll", "equal", mapi_util.random_str(4000))
	security_rule_list=[security_rule]
	"""

	# Deep Security Integrity Monitoring Status,MatchAll, equal, random 4000+1
	# result: ok, bug should only allow specific values and extra chars are truncated
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Integrity Monitoring Status", "MatchAll", "equal", mapi_util.random_str(4001))
	security_rule_list=[security_rule]
	"""

	# Deep Security Integrity Monitoring Status,MatchAll, equal, on
	# result: ok, bug should be case sensitive
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Integrity Monitoring Status", "MatchAll", "equal", "on")
	security_rule_list=[security_rule]
	"""
	


	# Deep Security Log Inspection Status,MatchAll, equal, NotCapable
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Log Inspection Status", "MatchAll", "equal", "NotCapable")
	security_rule_list=[security_rule]
	"""

	# Deep Security Log Inspection Status,MatchAll, equal, On
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Log Inspection Status", "MatchAll", "equal", "On")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Log Inspection Status,MatchAll, equal, Off
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Log Inspection Status", "MatchAll", "equal", "Off")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Log Inspection Status,MatchAny, equal, NotCapable
	# result: ok, bug should only allow MatchAll

	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Log Inspection Status", "MatchAny", "equal", "NotCapable")
	security_rule_list=[security_rule]
	"""

	# Deep Security Log Inspection Status,"", equal, NotCapable
	# result: fail,HTTP Error 500: There is an error in XML document (5, 475).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Log Inspection Status", "", "equal", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Log Inspection Status,matchall, equal, NotCapable
	# result: fail,HTTP Error 500: There is an error in XML document (5, 483).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Log Inspection Status", "matchall", "equal", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Log Inspection Status,random 20 chars, equal, NotCapable
	# result: fail,HTTP Error 500: There is an error in XML document (5, 495).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Log Inspection Status", mapi_util.random_str(20), "equal", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Log Inspection Status,MatchAll, notequal,  NotCapable
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Log Inspection Status", "MatchAll", "notequal", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Log Inspection Status,MatchAll, notequal,  On
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Log Inspection Status", "MatchAll", "notequal", "On")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Log Inspection Status,MatchAll, notequal,  Off
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Log Inspection Status", "MatchAll", "notequal", "Off")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Log Inspection Status,MatchAll, greaterThan,  NotCapable
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Log Inspection Status", "MatchAll", "greaterThan", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Log Inspection Status,MatchAll, lessThan,  NotCapable
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Log Inspection Status", "MatchAll", "lessThan", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Log Inspection Status,MatchAll, equalGreaterThan,  NotCapable
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Log Inspection Status", "MatchAll", "equalGreaterThan", "NotCapable")
	security_rule_list=[security_rule]
	"""

	# Deep Security Log Inspection Status,MatchAll, equalLessThan,  NotCapable
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Log Inspection Status", "MatchAll", "equalLessThan", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Log Inspection Status,MatchAll, information,  NotCapable
	# result: ok, if information, security rule is not saved
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Log Inspection Status", "MatchAll", "information", "NotCapable")
	security_rule_list=[security_rule]
	"""

	# Deep Security Log Inspection Status,MatchAll, Has,  NotCapable
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Log Inspection Status", "MatchAll", "Has", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Log Inspection Status,MatchAll, NotHave,  NotCapable
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Log Inspection Status", "MatchAll", "NotHave", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Log Inspection Status,MatchAll, Containing,  NotCapable
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Log Inspection Status", "MatchAll", "Containing", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Log Inspection Status,MatchAll, NotContaining,  NotCapable
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Log Inspection Status", "MatchAll", "NotContaining", "NotCapable")
	security_rule_list=[security_rule]
	"""
	
	# Deep Security Log Inspection Status,MatchAll, "",  NotCapable
	# result: fail,HTTP Error 500: There is an error in XML document (5, 574).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Log Inspection Status", "MatchAll", "", "NotCapable")
	security_rule_list=[security_rule]
	"""

	# Deep Security Log Inspection Status,MatchAll, EQUAL,  NotCapable
	# result: fail,HTTP Error 500: There is an error in XML document (5, 579).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Log Inspection Status", "MatchAll", "EQUAL", "NotCapable")
	security_rule_list=[security_rule]
	"""

	# Deep Security Log Inspection Status,MatchAll, random 20 chars,  NotCapable
	# result: fail,HTTP Error 500: There is an error in XML document (5, 594).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Log Inspection Status", "MatchAll", mapi_util.random_str(20), "NotCapable")
	security_rule_list=[security_rule]
	"""

	# Deep Security Log Inspection Status,MatchAll, equal, ""
	# result: ok, bug empty should not be allowed
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Log Inspection Status", "MatchAll", "equal", "")
	security_rule_list=[security_rule]
	"""


	# Deep Security Log Inspection Status,MatchAll, equal, random 4000 
	# result: ok, bug should only allow specific values
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Log Inspection Status", "MatchAll", "equal", mapi_util.random_str(4000))
	security_rule_list=[security_rule]
	"""


	# Deep Security Log Inspection Status,MatchAll, equal, random 4000+1
	# result: ok, bug should only allow specific values and extra chars are truncated
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Log Inspection Status", "MatchAll", "equal", mapi_util.random_str(4001))
	security_rule_list=[security_rule]
	"""
	

	# Deep Security Log Inspection Status,MatchAll, equal, on (case sensitive)
	# result: ok, bug should be case sensitive
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Deep Security Log Inspection Status", "MatchAll", "equal", "on")
	security_rule_list=[security_rule]
	"""
	

	# Network Services,MatchAll, equal, 80
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Network Services", "MatchAll", "equal", "80")
	security_rule_list=[security_rule]
	"""

	# Network Services,MatchAny, equal, 80
	# result: fail
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Network Services", "MatchAny", "equal", "80")
	security_rule_list=[security_rule]
	"""
	
	# Network Services,"", equal, 80
	# result: fail,HTTP Error 500: There is an error in XML document (5, 475).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Network Services", "", "equal", "80")
	security_rule_list=[security_rule]
	"""
	
	# Network Services,matchall, equal, 80
	# result: fail,HTTP Error 500: There is an error in XML document (5, 483).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Network Services", "matchall", "equal", "80")
	security_rule_list=[security_rule]
	"""
	
	# Network Services,random 20 chars, equal, 80
	# result: fail,HTTP Error 500: There is an error in XML document (5, 495).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Network Services", mapi_util.random_str(20), "equal", "80")
	security_rule_list=[security_rule]
	"""
	
	
	# Network Services,MatchAll, notequal, 80
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Network Services", "MatchAll", "notequal", "80")
	security_rule_list=[security_rule]
	"""

	# Network Services,MatchAll, greaterThan, 80
	# result: ok bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Network Services", "MatchAll", "greaterThan", "80")
	security_rule_list=[security_rule]
	"""

	# Network Services,MatchAll, lessThan, 80
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Network Services", "MatchAll", "lessThan", "80")
	security_rule_list=[security_rule]
	"""

	# Network Services,MatchAll, equalGreaterThan, 80
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Network Services", "MatchAll", "equalGreaterThan", "80")
	security_rule_list=[security_rule]
	"""

	# Network Services,MatchAll, equalLessThan, 80
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Network Services", "MatchAll", "equalLessThan", "80")
	security_rule_list=[security_rule]
	"""

	# Network Services,MatchAll, information, 80
	# result: ok, if information, security rule is not saved
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Network Services", "MatchAll", "information", "80")
	security_rule_list=[security_rule]
	"""

	# Network Services,MatchAll, Has, 80
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Network Services", "MatchAll", "Has", "80")
	security_rule_list=[security_rule]
	"""

	# Network Services,MatchAll, NotHave, 80
	# result: ok, not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Network Services", "MatchAll", "NotHave", "80")
	security_rule_list=[security_rule]
	"""
	
	# Network Services,MatchAll, Containing, 80
	# result: ok, bug not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Network Services", "MatchAll", "Containing", "80")
	security_rule_list=[security_rule]
	"""
	
	# Network Services,MatchAll, NotContaining, 80
	# result: ok, not a valid option
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Network Services", "MatchAll", "NotContaining", "80")
	security_rule_list=[security_rule]
	"""

	# Network Services,MatchAll, "", 80
	# result: fail,HTTP Error 500: There is an error in XML document (5, 566).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Network Services", "MatchAll", "", "80")
	security_rule_list=[security_rule]
	"""

	# Network Services,MatchAll, EQUAL, 80
	# result: fail,HTTP Error 500: There is an error in XML document (5, 571).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Network Services", "MatchAll", "EQUAL", "80")
	security_rule_list=[security_rule]
	"""
	
	# Network Services,MatchAll, random 20 chars, 80
	# result: fail,HTTP Error 500: There is an error in XML document (5, 586).
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Network Services", "MatchAll", mapi_util.random_str(20), "80")
	security_rule_list=[security_rule]
	"""

	# Network Services,MatchAll, equal, ""
	# result: ok, bug empty should not be allowed
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Network Services", "MatchAll", "equal", "")
	security_rule_list=[security_rule]
	"""
	
	# Network Services,MatchAll, equal, not digit and comma, asdfasdfasdfsdf
	# result: ok, bug only digits and comma should be allowed
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Network Services", "MatchAll", "equal", "asdfasdfasdfsdf")
	security_rule_list=[security_rule]
	"""
	
	# Network Services,MatchAll, equal, UI max 35
	# result: ok
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Network Services", "MatchAll", "equal", mapi_util.random_str(35))
	security_rule_list=[security_rule]
	"""
	
	# Network Services,MatchAll, equal, UI max 35+1
	# result: ok, bug UI max is 35
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Network Services", "MatchAll", "equal", mapi_util.random_str(36))
	security_rule_list=[security_rule]
	"""

	# Network Services,MatchAll, equal, db max 4000 
	# result: ok, bug UI max is 35
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Network Services", "MatchAll", "equal", mapi_util.random_str(4000))
	security_rule_list=[security_rule]
	"""
	
	# Network Services,MatchAll, equal, db max 4000+1
	# result: ok, bug UI max is 35 and extra chars are truncated
	"""
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule = "%s,%s,%s#%s" % ("Network Services", "MatchAll", "equal", mapi_util.random_str(4001))
	security_rule_list=[security_rule]
	"""

	"""
	print createSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					device_id_list,image_id_list, security_rule_list)
	"""





	# Device Access Type,MatchAll, equal, special chars
	# result: fail,HTTP Error 500: There is an error in XML document (8, 87).

	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list= None
	formatted_security_rule = """<securityRuleList>
		<securityRule dataMissing="Failed" description="" id="%s" matchType="%s">
			<securityRuleConditionList>
				<securityRuleCondition evaluator="%s" expectedValue="%s"/>
			</securityRuleConditionList>
		</securityRule>
	</securityRuleList>""" % (mapi_config.rule_mapping["Device Access Type"], "MatchAll", "equal", mapi_util.SPECIAL_CHARS)

	"""
	print createSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					device_id_list,image_id_list, security_rule_list, False, formatted_security_rule)
	"""


	# Device Mount Point,MatchAll, equal, special chars
	# result: fail,HTTP Error 500: There is an error in XML document (8, 87).

	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list= None
	formatted_security_rule = """<securityRuleList>
		<securityRule dataMissing="Failed" description="" id="%s" matchType="%s">
			<securityRuleConditionList>
				<securityRuleCondition evaluator="%s" expectedValue="%s"/>
			</securityRuleConditionList>
		</securityRule>
	</securityRuleList>""" % (mapi_config.rule_mapping["Device Mount Point"], "MatchAll", "equal", mapi_util.SPECIAL_CHARS)

	"""
	print createSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					device_id_list,image_id_list, security_rule_list, False, formatted_security_rule)
	"""


	# Request Source IP Address,MatchAll, equal, special chars
	# result: fail,HTTP Error 500: There is an error in XML document (8, 87).

	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list= None
	formatted_security_rule = """<securityRuleList>
		<securityRule dataMissing="Failed" description="" id="%s" matchType="%s">
			<securityRuleConditionList>
				<securityRuleCondition evaluator="%s" expectedValue="%s"/>
			</securityRuleConditionList>
		</securityRule>
	</securityRuleList>""" % (mapi_config.rule_mapping["Request Source IP Address"], "MatchAll", "equal", mapi_util.SPECIAL_CHARS)

	"""
	print createSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					device_id_list,image_id_list, security_rule_list, False, formatted_security_rule)
	"""



	# Request Source IPv6 Address,MatchAll, equal, special chars
	# result: fail,HTTP Error 500: There is an error in XML document (8, 87).

	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list= None
	formatted_security_rule = """<securityRuleList>
		<securityRule dataMissing="Failed" description="" id="%s" matchType="%s">
			<securityRuleConditionList>
				<securityRuleCondition evaluator="%s" expectedValue="%s"/>
			</securityRuleConditionList>
		</securityRule>
	</securityRuleList>""" % (mapi_config.rule_mapping["Request Source IPv6 Address"], "MatchAll", "equal", mapi_util.SPECIAL_CHARS)

	"""
	print createSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					device_id_list,image_id_list, security_rule_list, False, formatted_security_rule)
	"""



	# Instance User Data,MatchAll, others, db max 4000+1
	# result: fail,HTTP Error 500: There is an error in XML document (8, 87).
	
	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list= None
	formatted_security_rule = """<securityRuleList>
		<securityRule dataMissing="Failed" description="" id="%s" matchType="%s">
			<securityRuleConditionList>
				<securityRuleCondition evaluator="%s" expectedValue="%s"/>
			</securityRuleConditionList>
		</securityRule>
	</securityRuleList>""" % (mapi_config.rule_mapping["Instance User Data"], "MatchAll", "equal", mapi_util.SPECIAL_CHARS)

	"""
	print createSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					device_id_list,image_id_list, security_rule_list, False, formatted_security_rule)
	"""



	# Instance Location,MatchAll, equal, special chars
	# result: fail,HTTP Error 500: There is an error in XML document (8, 87).

	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list= None
	formatted_security_rule = """<securityRuleList>
		<securityRule dataMissing="Failed" description="" id="%s" matchType="%s">
			<securityRuleConditionList>
				<securityRuleCondition evaluator="%s" expectedValue="%s"/>
			</securityRuleConditionList>
		</securityRule>
	</securityRuleList>""" % (mapi_config.rule_mapping["Instance Location"], "MatchAll", "equal", mapi_util.SPECIAL_CHARS)

	"""
	print createSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					device_id_list,image_id_list, security_rule_list, False, formatted_security_rule)
	"""


	# Network Services,MatchAll, equal, special chars
	# result: fail,HTTP Error 500: There is an error in XML document (8, 87).

	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list= None
	formatted_security_rule = """<securityRuleList>
		<securityRule dataMissing="Failed" description="" id="%s" matchType="%s">
			<securityRuleConditionList>
				<securityRuleCondition evaluator="%s" expectedValue="%s"/>
			</securityRuleConditionList>
		</securityRule>
	</securityRuleList>""" % (mapi_config.rule_mapping["Network Services"], "MatchAll", "equal", mapi_util.SPECIAL_CHARS)

	"""
	print createSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					device_id_list,image_id_list, security_rule_list, False, formatted_security_rule)
	"""
	



	# Trend Micro softwares,MatchAll, Has, $L10N_PRD_DSA_NAME$
	# result: ok

	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list= None
	formatted_security_rule = """<securityRuleList>
		<securityRule dataMissing="Failed" description="" id="%s" matchType="%s">
			<securityRuleConditionList>
				<securityRuleCondition evaluator="%s" expectedValue="%s"/>
			</securityRuleConditionList>
		</securityRule>
	</securityRuleList>""" % (mapi_config.rule_mapping["Trend Micro softwares"], "MatchAll", "Has", "$L10N_PRD_DSA_NAME$")

	"""
	print createSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					device_id_list,image_id_list, security_rule_list, False, formatted_security_rule)
	"""
	

	# Trend Micro softwares,MatchAll, Has, $L10N_PRD_OSCE_NAME$
	# result: ok

	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list= None
	formatted_security_rule = """<securityRuleList>
		<securityRule dataMissing="Failed" description="" id="%s" matchType="%s">
			<securityRuleConditionList>
				<securityRuleCondition evaluator="%s" expectedValue="%s"/>
			</securityRuleConditionList>
		</securityRule>
	</securityRuleList>""" % (mapi_config.rule_mapping["Trend Micro softwares"], "MatchAll", "Has", "$L10N_PRD_OSCE_NAME$")

	"""
	print createSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					device_id_list,image_id_list, security_rule_list, False, formatted_security_rule)
	"""

	# Trend Micro softwares,MatchAll, Has, $L10N_PRD_SPLX_NAME$
	# result: ok

	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list= None
	formatted_security_rule = """<securityRuleList>
		<securityRule dataMissing="Failed" description="" id="%s" matchType="%s">
			<securityRuleConditionList>
				<securityRuleCondition evaluator="%s" expectedValue="%s"/>
			</securityRuleConditionList>
		</securityRule>
	</securityRuleList>""" % (mapi_config.rule_mapping["Trend Micro softwares"], "MatchAll", "Has", "$L10N_PRD_SPLX_NAME$")

	"""
	print createSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					device_id_list,image_id_list, security_rule_list, False, formatted_security_rule)
	"""

	# Trend Micro softwares,MatchAny, Has, $L10N_PRD_DSA_NAME$
	# result: ok, bug should only has MatchAll

	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list= None
	formatted_security_rule = """<securityRuleList>
		<securityRule dataMissing="Failed" description="" id="%s" matchType="%s">
			<securityRuleConditionList>
				<securityRuleCondition evaluator="%s" expectedValue="%s"/>
			</securityRuleConditionList>
		</securityRule>
	</securityRuleList>""" % (mapi_config.rule_mapping["Trend Micro softwares"], "MatchAny", "Has", "$L10N_PRD_DSA_NAME$")

	"""
	print createSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					device_id_list,image_id_list, security_rule_list, False, formatted_security_rule)
	"""


	# Trend Micro softwares,"", Has, $L10N_PRD_DSA_NAME$
	# result: fail,HTTP Error 500: There is an error in XML document (6, 108).

	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list= None
	formatted_security_rule = """<securityRuleList>
		<securityRule dataMissing="Failed" description="" id="%s" matchType="%s">
			<securityRuleConditionList>
				<securityRuleCondition evaluator="%s" expectedValue="%s"/>
			</securityRuleConditionList>
		</securityRule>
	</securityRuleList>""" % (mapi_config.rule_mapping["Trend Micro softwares"], "", "Has", "$L10N_PRD_DSA_NAME$")

	"""
	print createSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					device_id_list,image_id_list, security_rule_list, False, formatted_security_rule)
	"""
	
	# Trend Micro softwares,matchall, Has, $L10N_PRD_DSA_NAME$
	# result: fail,HTTP Error 500: There is an error in XML document (6, 116).

	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list= None
	formatted_security_rule = """<securityRuleList>
		<securityRule dataMissing="Failed" description="" id="%s" matchType="%s">
			<securityRuleConditionList>
				<securityRuleCondition evaluator="%s" expectedValue="%s"/>
			</securityRuleConditionList>
		</securityRule>
	</securityRuleList>""" % (mapi_config.rule_mapping["Trend Micro softwares"], "matchall", "Has", "$L10N_PRD_DSA_NAME$")

	"""
	print createSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					device_id_list,image_id_list, security_rule_list, False, formatted_security_rule)
	"""
	

	# Trend Micro softwares,random 20 chars, Has, $L10N_PRD_DSA_NAME$
	# result: fail,HTTP Error 500: There is an error in XML document (6, 128).

	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list= None
	formatted_security_rule = """<securityRuleList>
		<securityRule dataMissing="Failed" description="" id="%s" matchType="%s">
			<securityRuleConditionList>
				<securityRuleCondition evaluator="%s" expectedValue="%s"/>
			</securityRuleConditionList>
		</securityRule>
	</securityRuleList>""" % (mapi_config.rule_mapping["Trend Micro softwares"], mapi_util.random_str(20), "Has", "$L10N_PRD_DSA_NAME$")

	"""
	print createSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					device_id_list,image_id_list, security_rule_list, False, formatted_security_rule)
	"""
	

	# Trend Micro softwares,MatchAll, equal, $L10N_PRD_DSA_NAME$
	# result: ok, bug not a valid option

	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list= None
	formatted_security_rule = """<securityRuleList>
		<securityRule dataMissing="Failed" description="" id="%s" matchType="%s">
			<securityRuleConditionList>
				<securityRuleCondition evaluator="%s" expectedValue="%s"/>
			</securityRuleConditionList>
		</securityRule>
	</securityRuleList>""" % (mapi_config.rule_mapping["Trend Micro softwares"], "MatchAll", "equal", "$L10N_PRD_DSA_NAME$")

	"""
	print createSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					device_id_list,image_id_list, security_rule_list, False, formatted_security_rule)
	"""


	# Trend Micro softwares,MatchAll, notequal, $L10N_PRD_DSA_NAME$
	# result: ok, bug not a valid option

	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list= None
	formatted_security_rule = """<securityRuleList>
		<securityRule dataMissing="Failed" description="" id="%s" matchType="%s">
			<securityRuleConditionList>
				<securityRuleCondition evaluator="%s" expectedValue="%s"/>
			</securityRuleConditionList>
		</securityRule>
	</securityRuleList>""" % (mapi_config.rule_mapping["Trend Micro softwares"], "MatchAll", "notequal", "$L10N_PRD_DSA_NAME$")

	"""
	print createSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					device_id_list,image_id_list, security_rule_list, False, formatted_security_rule)
	"""

	# Trend Micro softwares,MatchAll, greaterThan, $L10N_PRD_DSA_NAME$
	# result: ok, not a valid option

	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list= None
	formatted_security_rule = """<securityRuleList>
		<securityRule dataMissing="Failed" description="" id="%s" matchType="%s">
			<securityRuleConditionList>
				<securityRuleCondition evaluator="%s" expectedValue="%s"/>
			</securityRuleConditionList>
		</securityRule>
	</securityRuleList>""" % (mapi_config.rule_mapping["Trend Micro softwares"], "MatchAll", "greaterThan", "$L10N_PRD_DSA_NAME$")

	"""
	print createSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					device_id_list,image_id_list, security_rule_list, False, formatted_security_rule)
	"""
	

	# Trend Micro softwares,MatchAll, lessThan, $L10N_PRD_DSA_NAME$
	# result: ok, bug not a valid option

	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list= None
	formatted_security_rule = """<securityRuleList>
		<securityRule dataMissing="Failed" description="" id="%s" matchType="%s">
			<securityRuleConditionList>
				<securityRuleCondition evaluator="%s" expectedValue="%s"/>
			</securityRuleConditionList>
		</securityRule>
	</securityRuleList>""" % (mapi_config.rule_mapping["Trend Micro softwares"], "MatchAll", "lessThan", "$L10N_PRD_DSA_NAME$")

	"""
	print createSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					device_id_list,image_id_list, security_rule_list, False, formatted_security_rule)
	"""
	

	# Trend Micro softwares,MatchAll, equalGreaterThan, $L10N_PRD_DSA_NAME$
	# result: ok, bug not valid option

	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list= None
	formatted_security_rule = """<securityRuleList>
		<securityRule dataMissing="Failed" description="" id="%s" matchType="%s">
			<securityRuleConditionList>
				<securityRuleCondition evaluator="%s" expectedValue="%s"/>
			</securityRuleConditionList>
		</securityRule>
	</securityRuleList>""" % (mapi_config.rule_mapping["Trend Micro softwares"], "MatchAll", "equalGreaterThan", "$L10N_PRD_DSA_NAME$")

	"""
	print createSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					device_id_list,image_id_list, security_rule_list, False, formatted_security_rule)
	"""
	

	# Trend Micro softwares,MatchAll, equalLessThan, $L10N_PRD_DSA_NAME$
	# result: ok, bug not a valid option

	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list= None
	formatted_security_rule = """<securityRuleList>
		<securityRule dataMissing="Failed" description="" id="%s" matchType="%s">
			<securityRuleConditionList>
				<securityRuleCondition evaluator="%s" expectedValue="%s"/>
			</securityRuleConditionList>
		</securityRule>
	</securityRuleList>""" % (mapi_config.rule_mapping["Trend Micro softwares"], "MatchAll", "equalLessThan", "$L10N_PRD_DSA_NAME$")

	"""
	print createSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					device_id_list,image_id_list, security_rule_list, False, formatted_security_rule)
	"""
	
	# Trend Micro softwares,MatchAll, information, $L10N_PRD_DSA_NAME$
	# result: ok, if information, security rule is not saved

	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list= None
	formatted_security_rule = """<securityRuleList>
		<securityRule dataMissing="Failed" description="" id="%s" matchType="%s">
			<securityRuleConditionList>
				<securityRuleCondition evaluator="%s" expectedValue="%s"/>
			</securityRuleConditionList>
		</securityRule>
	</securityRuleList>""" % (mapi_config.rule_mapping["Trend Micro softwares"], "MatchAll", "information", "$L10N_PRD_DSA_NAME$")

	"""
	print createSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					device_id_list,image_id_list, security_rule_list, False, formatted_security_rule)
	"""


	# Trend Micro softwares,MatchAll, Has, $L10N_PRD_DSA_NAME$
	# result: ok

	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list= None
	formatted_security_rule = """<securityRuleList>
		<securityRule dataMissing="Failed" description="" id="%s" matchType="%s">
			<securityRuleConditionList>
				<securityRuleCondition evaluator="%s" expectedValue="%s"/>
			</securityRuleConditionList>
		</securityRule>
	</securityRuleList>""" % (mapi_config.rule_mapping["Trend Micro softwares"], "MatchAll", "Has", "$L10N_PRD_DSA_NAME$")

	"""
	print createSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					device_id_list,image_id_list, security_rule_list, False, formatted_security_rule)
	"""

	# Trend Micro softwares,MatchAll, NotHave, $L10N_PRD_DSA_NAME$
	# result: ok

	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list= None
	formatted_security_rule = """<securityRuleList>
		<securityRule dataMissing="Failed" description="" id="%s" matchType="%s">
			<securityRuleConditionList>
				<securityRuleCondition evaluator="%s" expectedValue="%s"/>
			</securityRuleConditionList>
		</securityRule>
	</securityRuleList>""" % (mapi_config.rule_mapping["Trend Micro softwares"], "MatchAll", "NotHave", "$L10N_PRD_DSA_NAME$")

	"""
	print createSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					device_id_list,image_id_list, security_rule_list, False, formatted_security_rule)
	"""

	# Trend Micro softwares,MatchAll, NotHave, $L10N_PRD_OSCE_NAME$
	# result: ok

	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list= None
	formatted_security_rule = """<securityRuleList>
		<securityRule dataMissing="Failed" description="" id="%s" matchType="%s">
			<securityRuleConditionList>
				<securityRuleCondition evaluator="%s" expectedValue="%s"/>
			</securityRuleConditionList>
		</securityRule>
	</securityRuleList>""" % (mapi_config.rule_mapping["Trend Micro softwares"], "MatchAll", "NotHave", "$L10N_PRD_OSCE_NAME$")

	"""
	print createSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					device_id_list,image_id_list, security_rule_list, False, formatted_security_rule)
	"""


	# Trend Micro softwares,MatchAll, NotHave, $L10N_PRD_SPLX_NAME$
	# result: ok

	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list= None
	formatted_security_rule = """<securityRuleList>
		<securityRule dataMissing="Failed" description="" id="%s" matchType="%s">
			<securityRuleConditionList>
				<securityRuleCondition evaluator="%s" expectedValue="%s"/>
			</securityRuleConditionList>
		</securityRule>
	</securityRuleList>""" % (mapi_config.rule_mapping["Trend Micro softwares"], "MatchAll", "NotHave", "$L10N_PRD_SPLX_NAME$")

	"""
	print createSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					device_id_list,image_id_list, security_rule_list, False, formatted_security_rule)
	"""


	# Trend Micro softwares,MatchAll, Containing, $L10N_PRD_DSA_NAME$
	# result: ok, bug not a valid option

	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list= None
	formatted_security_rule = """<securityRuleList>
		<securityRule dataMissing="Failed" description="" id="%s" matchType="%s">
			<securityRuleConditionList>
				<securityRuleCondition evaluator="%s" expectedValue="%s"/>
			</securityRuleConditionList>
		</securityRule>
	</securityRuleList>""" % (mapi_config.rule_mapping["Trend Micro softwares"], "MatchAll", "Containing", "$L10N_PRD_DSA_NAME$")

	"""
	print createSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					device_id_list,image_id_list, security_rule_list, False, formatted_security_rule)
	"""


	# Trend Micro softwares,MatchAll, NotContaining, $L10N_PRD_DSA_NAME$
	# result: ok, bug not a valid option

	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list= None
	formatted_security_rule = """<securityRuleList>
		<securityRule dataMissing="Failed" description="" id="%s" matchType="%s">
			<securityRuleConditionList>
				<securityRuleCondition evaluator="%s" expectedValue="%s"/>
			</securityRuleConditionList>
		</securityRule>
	</securityRuleList>""" % (mapi_config.rule_mapping["Trend Micro softwares"], "MatchAll", "NotContaining", "$L10N_PRD_DSA_NAME$")

	"""
	print createSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					device_id_list,image_id_list, security_rule_list, False, formatted_security_rule)
	"""


	# Trend Micro softwares,MatchAll, "", $L10N_PRD_DSA_NAME$
	# result: fail,HTTP Error 500: There is an error in XML document (8, 78).

	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list= None
	formatted_security_rule = """<securityRuleList>
		<securityRule dataMissing="Failed" description="" id="%s" matchType="%s">
			<securityRuleConditionList>
				<securityRuleCondition evaluator="%s" expectedValue="%s"/>
			</securityRuleConditionList>
		</securityRule>
	</securityRuleList>""" % (mapi_config.rule_mapping["Trend Micro softwares"], "MatchAll", "", "$L10N_PRD_DSA_NAME$")

	"""
	print createSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					device_id_list,image_id_list, security_rule_list, False, formatted_security_rule)
	"""


	# Trend Micro softwares,MatchAll, EQUAL, $L10N_PRD_DSA_NAME$
	# result: fail,HTTP Error 500: There is an error in XML document (8, 83).

	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list= None
	formatted_security_rule = """<securityRuleList>
		<securityRule dataMissing="Failed" description="" id="%s" matchType="%s">
			<securityRuleConditionList>
				<securityRuleCondition evaluator="%s" expectedValue="%s"/>
			</securityRuleConditionList>
		</securityRule>
	</securityRuleList>""" % (mapi_config.rule_mapping["Trend Micro softwares"], "MatchAll", "EQUAL", "$L10N_PRD_DSA_NAME$")

	"""
	print createSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					device_id_list,image_id_list, security_rule_list, False, formatted_security_rule)
	"""
	
	# Trend Micro softwares,MatchAll, random 20 chars, $L10N_PRD_DSA_NAME$
	# result: fail,HTTP Error 500: There is an error in XML document (8, 98).

	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list= None
	formatted_security_rule = """<securityRuleList>
		<securityRule dataMissing="Failed" description="" id="%s" matchType="%s">
			<securityRuleConditionList>
				<securityRuleCondition evaluator="%s" expectedValue="%s"/>
			</securityRuleConditionList>
		</securityRule>
	</securityRuleList>""" % (mapi_config.rule_mapping["Trend Micro softwares"], "MatchAll", mapi_util.random_str(20), "$L10N_PRD_DSA_NAME$")

	"""
	print createSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					device_id_list,image_id_list, security_rule_list, False, formatted_security_rule)
	"""

	# Trend Micro softwares,MatchAll, Has, ""
	# result: ok, bug empty should not be allowed

	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list= None
	formatted_security_rule = """<securityRuleList>
		<securityRule dataMissing="Failed" description="" id="%s" matchType="%s">
			<securityRuleConditionList>
				<securityRuleCondition evaluator="%s" expectedValue="%s"/>
			</securityRuleConditionList>
		</securityRule>
	</securityRuleList>""" % (mapi_config.rule_mapping["Trend Micro softwares"], "MatchAll", "Has", "")

	"""
	print createSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					device_id_list,image_id_list, security_rule_list, False, formatted_security_rule)
	"""
	
	# Trend Micro softwares,MatchAll, Has, random 4000 chars
	# result: fail

	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list= None
	formatted_security_rule = """<securityRuleList>
		<securityRule dataMissing="Failed" description="" id="%s" matchType="%s">
			<securityRuleConditionList>
				<securityRuleCondition evaluator="%s" expectedValue="%s"/>
			</securityRuleConditionList>
		</securityRule>
	</securityRuleList>""" % (mapi_config.rule_mapping["Trend Micro softwares"], "MatchAll", "Has", mapi_util.random_str(4000))

	"""
	print createSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					device_id_list,image_id_list, security_rule_list, False, formatted_security_rule)
	"""
	
	# Trend Micro softwares,MatchAll, Has, random 4001 chars
	# result: ok, bug extra char is truncated

	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list= None
	formatted_security_rule = """<securityRuleList>
		<securityRule dataMissing="Failed" description="" id="%s" matchType="%s">
			<securityRuleConditionList>
				<securityRuleCondition evaluator="%s" expectedValue="%s"/>
			</securityRuleConditionList>
		</securityRule>
	</securityRuleList>""" % (mapi_config.rule_mapping["Trend Micro softwares"], "MatchAll", "Has", mapi_util.random_str(4001))

	"""
	print createSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					device_id_list,image_id_list, security_rule_list, False, formatted_security_rule)
	"""

	# Trend Micro softwares,MatchAll, Has, special chars
	# result: fail,HTTP Error 500: There is an error in XML document (8, 85).

	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list= None
	formatted_security_rule = """<securityRuleList>
		<securityRule dataMissing="Failed" description="" id="%s" matchType="%s">
			<securityRuleConditionList>
				<securityRuleCondition evaluator="%s" expectedValue="%s"/>
			</securityRuleConditionList>
		</securityRule>
	</securityRuleList>""" % (mapi_config.rule_mapping["Trend Micro softwares"], "MatchAll", "Has", mapi_util.SPECIAL_CHARS)

	"""
	print createSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					device_id_list,image_id_list, security_rule_list, False, formatted_security_rule)
	"""


	# Trend Micro softwares,MatchAll, Has, "$l10n_prd_dsa_name$"
	# result: fail,HTTP Error 500: There is an error in XML document (8, 87).

	EnableIC="true"

	ICAction="Nothing"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	
	policy_name = "mapi_test"
	isResourcePool = "false"
	description= "test description"
	successAction="ManualApprove"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["createSecurityGroup_device1"]
	image_id_list=["createSecurityGroup_image"]
	security_rule_list= None
	formatted_security_rule = """<securityRuleList>
		<securityRule dataMissing="Failed" description="" id="%s" matchType="%s">
			<securityRuleConditionList>
				<securityRuleCondition evaluator="%s" expectedValue="%s"/>
			</securityRuleConditionList>
		</securityRule>
	</securityRuleList>""" % (mapi_config.rule_mapping["Trend Micro softwares"], "MatchAll", "Has", "$l10n_prd_dsa_name$")

	"""
	print createSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					device_id_list,image_id_list, security_rule_list, False, formatted_security_rule)
	"""








	# -------------------------------------

	# policy_id = "00000000-0000-0000-0000-000000000000"
	# http 400 bad request
	# TMEG.Cloud9.Exceptions.InvalidResourceIDException: Policy Invalid GUID ---> TMEG.Cloud9.Exceptions.DatabaseException: Data Error: -1301

	# policy_id = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"
	# http 500
	# System.FormatException: Guid should contain 32 digits with 4 dashes (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx).

	# policy_id = "asdfsdf5sd4f564sdf56as4df56a"
	# http 500
	# ERROR SecureCloud.BrokerService - System.FormatException: Guid should contain 32 digits with 4 dashes (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx).

	#print deleteSecurityGroup(policy_id)


	# -------------------------------------

	"""
	EnableIC="true"
	ICAction="Revoke"
	PostponeEnable="true"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	policy_name="mapi_test_updated"
	isResourcePool="false"
	description="this is after update"
	successAction="Approve"
	successActionDelay=""
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=["updateSecurityGroup_device1"]
	image_id_list=["updateSecurityGroup_image"]
	security_rule_list=["Device Mount Point,MatchAll,equal#/mnt/policytest"]
	"""


	#print updateSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
	#				RevokeIntervalType, policy_name, isResourcePool, description, \
	#				successAction, successActionDelay, failAction, failActionDelay, \
	#				device_id_list,image_id_list, security_rule_list)

	# -------------------------------------

	#print getSecurityGroupSetting()

	# -------------------------------------

	#7:50 on UI = 3:50

	#scheduleType="Weekly"
	#result : ok
	"""
	scheduleType="Weekly"
	scheduleIntervalTime="8:00:00"
	scheduleIntervalPeriod="AM"
	scheduleIntervalDay="Wed"
	reAttemptInterval="2"
	reAttemptIntervalType="hours"
	reAttemptICRepeat="200"
	"""

	#scheduleType="Daily"
	#result : ok
	"""
	scheduleType="Daily"
	scheduleIntervalTime="8:00:00"
	scheduleIntervalPeriod="AM"
	scheduleIntervalDay="Wed"
	reAttemptInterval="2"
	reAttemptIntervalType="hours"
	reAttemptICRepeat="200"
	"""

	#scheduleType=""
	#result : HTTP Error 500: Internal Server Error
	"""
	scheduleType=""
	scheduleIntervalTime="8:00:00"
	scheduleIntervalPeriod="AM"
	scheduleIntervalDay="Wed"
	reAttemptInterval="2"
	reAttemptIntervalType="hours"
	reAttemptICRepeat="200"
	"""

	#scheduleType= random 20 chars
	#result : HTTP Error 500: Internal Server Error
	"""
	scheduleType=mapi_util.random_str(20)
	scheduleIntervalTime="8:00:00"
	scheduleIntervalPeriod="AM"
	scheduleIntervalDay="Wed"
	reAttemptInterval="2"
	reAttemptIntervalType="hours"
	reAttemptICRepeat="200"
	"""

	#scheduleIntervalTime=""
	#result : HTTP Error 400: Bad Request
	#TMEG.Cloud9.Exceptions.ValidationException: request.ScheduleIntervalTime: Invalid ScheduleIntervalTime.
	"""
	scheduleType="Daily"
	scheduleIntervalTime=""
	scheduleIntervalPeriod="AM"
	scheduleIntervalDay="Wed"
	reAttemptInterval="2"
	reAttemptIntervalType="hours"
	reAttemptICRepeat="200"
	"""
	
	#scheduleIntervalTime=random 20 chars
	#result : ok
	#Bug: should not be save and extra chars are truncated
	"""
	scheduleType="Daily"
	scheduleIntervalTime=mapi_util.random_str(11)
	scheduleIntervalPeriod="AM"
	scheduleIntervalDay="Wed"
	reAttemptInterval="2"
	reAttemptIntervalType="hours"
	reAttemptICRepeat="200"
	"""

	#scheduleIntervalTime=99:99:99, right format but wrong time
	#result : ok
	#Bug
	"""
	scheduleType="Daily"
	scheduleIntervalTime="99:99:99"
	scheduleIntervalPeriod="AM"
	scheduleIntervalDay="Wed"
	reAttemptInterval="2"
	reAttemptIntervalType="hours"
	reAttemptICRepeat="200"
	"""

	#scheduleIntervalPeriod="AM"
	#result : ok
	"""
	scheduleType="Daily"
	scheduleIntervalTime="09:30:15"
	scheduleIntervalPeriod="AM"
	scheduleIntervalDay="Wed"
	reAttemptInterval="2"
	reAttemptIntervalType="hours"
	reAttemptICRepeat="200"
	"""
	
	#scheduleIntervalPeriod="PM"
	#result : ok
	"""
	scheduleType="Daily"
	scheduleIntervalTime="09:30:15"
	scheduleIntervalPeriod="PM"
	scheduleIntervalDay="Wed"
	reAttemptInterval="2"
	reAttemptIntervalType="hours"
	reAttemptICRepeat="200"
	"""

	#scheduleIntervalPeriod="am", case sensitive test
	#result : HTTP Error 500: Internal Server Error
	"""
	scheduleType="Daily"
	scheduleIntervalTime="09:30:15"
	scheduleIntervalPeriod="am"
	scheduleIntervalDay="Wed"
	reAttemptInterval="2"
	reAttemptIntervalType="hours"
	reAttemptICRepeat="200"
	"""

	#scheduleIntervalPeriod=""
	#result : HTTP Error 500: Internal Server Error
	"""	
	scheduleType="Daily"
	scheduleIntervalTime="09:30:15"
	scheduleIntervalPeriod=""
	scheduleIntervalDay="Wed"
	reAttemptInterval="2"
	reAttemptIntervalType="hours"
	reAttemptICRepeat="200"
	"""
	
	#scheduleIntervalPeriod= random 20 chars
	#result : HTTP Error 500: Internal Server Error
	"""	
	scheduleType="Daily"
	scheduleIntervalTime="09:30:15"
	scheduleIntervalPeriod=mapi_util.random_str(20)
	scheduleIntervalDay="Wed"
	reAttemptInterval="2"
	reAttemptIntervalType="hours"
	reAttemptICRepeat="200"
	"""

	#scheduleIntervalPeriod= special chars
	#result : HTTP Error 500: There is an error in XML document (5, 53).
	"""
	scheduleType="Daily"
	scheduleIntervalTime="09:30:15"
	scheduleIntervalPeriod=mapi_util.SPECIAL_CHARS
	scheduleIntervalDay="Wed"
	reAttemptInterval="2"
	reAttemptIntervalType="hours"
	reAttemptICRepeat="200"
	"""

	# Valid scheduleIntervalDay=Sun/Mon/Tue/Wed/Thu/Fri/Sat
	# scheduleIntervalDay="Sun"
	# result : ok
	"""
	scheduleType="Daily"
	scheduleIntervalTime="09:30:15"
	scheduleIntervalPeriod="AM"
	scheduleIntervalDay="Sun"
	reAttemptInterval="2"
	reAttemptIntervalType="hours"
	reAttemptICRepeat="200"
	"""

	# Valid scheduleIntervalDay=Sun/Mon/Tue/Wed/Thu/Fri/Sat
	# scheduleIntervalDay="Mon"
	# result : ok
	"""
	scheduleType="Daily"
	scheduleIntervalTime="09:30:15"
	scheduleIntervalPeriod="AM"
	scheduleIntervalDay="Mon"
	reAttemptInterval="2"
	reAttemptIntervalType="hours"
	reAttemptICRepeat="200"
	"""
	

	# Valid scheduleIntervalDay=Sun/Mon/Tue/Wed/Thu/Fri/Sat
	# scheduleIntervalDay="Tue"
	# result : ok
	"""
	scheduleType="Daily"
	scheduleIntervalTime="09:30:15"
	scheduleIntervalPeriod="AM"
	scheduleIntervalDay="Tue"
	reAttemptInterval="2"
	reAttemptIntervalType="hours"
	reAttemptICRepeat="200"
	"""

	# Valid scheduleIntervalDay=Sun/Mon/Tue/Wed/Thu/Fri/Sat
	# scheduleIntervalDay="Wed"
	# result : ok
	"""
	scheduleType="Daily"
	scheduleIntervalTime="09:30:15"
	scheduleIntervalPeriod="AM"
	scheduleIntervalDay="Wed"
	reAttemptInterval="2"
	reAttemptIntervalType="hours"
	reAttemptICRepeat="200"
	"""

	# Valid scheduleIntervalDay=Sun/Mon/Tue/Wed/Thu/Fri/Sat
	# scheduleIntervalDay="Thu"
	# result : ok
	"""
	scheduleType="Daily"
	scheduleIntervalTime="09:30:15"
	scheduleIntervalPeriod="AM"
	scheduleIntervalDay="Thu"
	reAttemptInterval="2"
	reAttemptIntervalType="hours"
	reAttemptICRepeat="200"
	"""

	# Valid scheduleIntervalDay=Sun/Mon/Tue/Wed/Thu/Fri/Sat
	# scheduleIntervalDay="Fri"
	# result : ok
	"""
	scheduleType="Daily"
	scheduleIntervalTime="09:30:15"
	scheduleIntervalPeriod="AM"
	scheduleIntervalDay="Fri"
	reAttemptInterval="2"
	reAttemptIntervalType="hours"
	reAttemptICRepeat="200"
	"""

	# Valid scheduleIntervalDay=Sun/Mon/Tue/Wed/Thu/Fri/Sat
	# scheduleIntervalDay="Sat"
	# result : ok
	"""
	scheduleType="Daily"
	scheduleIntervalTime="09:30:15"
	scheduleIntervalPeriod="AM"
	scheduleIntervalDay="Sat"
	reAttemptInterval="2"
	reAttemptIntervalType="hours"
	reAttemptICRepeat="200"
	"""

	# Valid scheduleIntervalDay=Sun/Mon/Tue/Wed/Thu/Fri/Sat
	# scheduleIntervalDay=""
	# result : HTTP Error 500: Internal Server Error
	"""
	scheduleType="Daily"
	scheduleIntervalTime="09:30:15"
	scheduleIntervalPeriod="AM"
	scheduleIntervalDay=""
	reAttemptInterval="2"
	reAttemptIntervalType="hours"
	reAttemptICRepeat="200"
	"""

	# Valid scheduleIntervalDay=Sun/Mon/Tue/Wed/Thu/Fri/Sat
	# scheduleIntervalDay= random char 20
	# result : HTTP Error 500: Internal Server Error
	"""
	scheduleType="Daily"
	scheduleIntervalTime="09:30:15"
	scheduleIntervalPeriod="AM"
	scheduleIntervalDay=mapi_util.random_str(20)
	reAttemptInterval="2"
	reAttemptIntervalType="hours"
	reAttemptICRepeat="200"
	"""

	# Valid scheduleIntervalDay=Sun/Mon/Tue/Wed/Thu/Fri/Sat
	# scheduleIntervalDay= special chars
	# result : HTTP Error 500: There is an error in XML document (6, 50).
	"""
	scheduleType="Daily"
	scheduleIntervalTime="09:30:15"
	scheduleIntervalPeriod="AM"
	scheduleIntervalDay=mapi_util.SPECIAL_CHARS
	reAttemptInterval="2"
	reAttemptIntervalType="hours"
	reAttemptICRepeat="200"
	"""

	# Valid scheduleIntervalDay=Sun/Mon/Tue/Wed/Thu/Fri/Sat
	# scheduleIntervalDay= mon, case sensitive test
	# result : HTTP Error 500: Internal Server Error
	"""
	scheduleType="Daily"
	scheduleIntervalTime="09:30:15"
	scheduleIntervalPeriod="AM"
	scheduleIntervalDay="mon"
	reAttemptInterval="2"
	reAttemptIntervalType="hours"
	reAttemptICRepeat="200"
	"""


	# reAttemptInterval=""
	# result : HTTP Error 500: Internal Server Error
	"""
	scheduleType="Daily"
	scheduleIntervalTime="09:30:15"
	scheduleIntervalPeriod="AM"
	scheduleIntervalDay="Mon"
	reAttemptInterval=""
	reAttemptIntervalType="hours"
	reAttemptICRepeat="200"
	"""


	# reAttemptInterval="0"
	# result : HTTP Error 400: Bad Request
	"""
	scheduleType="Daily"
	scheduleIntervalTime="09:30:15"
	scheduleIntervalPeriod="AM"
	scheduleIntervalDay="Mon"
	reAttemptInterval="0"
	reAttemptIntervalType="hours"
	reAttemptICRepeat="200"
	"""
	

	# reAttemptInterval="-1"
	# result : HTTP Error 400: Bad Request
	"""
	scheduleType="Daily"
	scheduleIntervalTime="09:30:15"
	scheduleIntervalPeriod="AM"
	scheduleIntervalDay="Mon"
	reAttemptInterval="-1"
	reAttemptIntervalType="hours"
	reAttemptICRepeat="200"
	"""
	

	# reAttemptInterval=as tested out only allow 1-12, other will get HTTP Error 400: Bad Request
	# result : ok
	"""
	scheduleType="Daily"
	scheduleIntervalTime="09:30:15"
	scheduleIntervalPeriod="AM"
	scheduleIntervalDay="Mon"
	reAttemptInterval="12"
	reAttemptIntervalType="hours"
	reAttemptICRepeat="200"
	"""


	# reAttemptInterval=should be within 1-59 with reAttemptIntervalType="minutes
	# result : ok
	"""
	scheduleType="Daily"
	scheduleIntervalTime="09:30:15"
	scheduleIntervalPeriod="AM"
	scheduleIntervalDay="Mon"
	reAttemptInterval="60"
	reAttemptIntervalType="minutes"
	reAttemptICRepeat="200"
	"""
	
	# reAttemptInterval=not integer, true
	# result : HTTP Error 500: Internal Server Error
	"""
	scheduleType="Daily"
	scheduleIntervalTime="09:30:15"
	scheduleIntervalPeriod="AM"
	scheduleIntervalDay="Mon"
	reAttemptInterval="true"
	reAttemptIntervalType="hours"
	reAttemptICRepeat="200"
	"""

	# reAttemptIntervalType="hours/minutes"
	# reAttemptIntervalType="hours"
	# result : ok
	"""
	scheduleType="Daily"
	scheduleIntervalTime="09:30:15"
	scheduleIntervalPeriod="AM"
	scheduleIntervalDay="Mon"
	reAttemptInterval="10"
	reAttemptIntervalType="hours"
	reAttemptICRepeat="200"
	"""

	# reAttemptIntervalType="hours/minutes"
	# reAttemptIntervalType="minutes"
	# result : ok
	"""
	scheduleType="Daily"
	scheduleIntervalTime="09:30:15"
	scheduleIntervalPeriod="AM"
	scheduleIntervalDay="Mon"
	reAttemptInterval="10"
	reAttemptIntervalType="hours"
	reAttemptICRepeat="200"
	"""

	# reAttemptIntervalType="hours/minutes"
	# reAttemptIntervalType=""
	# result : HTTP Error 500: Internal Server Error
	"""
	scheduleType="Daily"
	scheduleIntervalTime="09:30:15"
	scheduleIntervalPeriod="AM"
	scheduleIntervalDay="Mon"
	reAttemptInterval="10"
	reAttemptIntervalType=""
	reAttemptICRepeat="200"
	"""

	# reAttemptIntervalType="hours/minutes"
	# reAttemptIntervalType=random 20 chars
	# result : HTTP Error 500: Internal Server Error
	"""
	scheduleType="Daily"
	scheduleIntervalTime="09:30:15"
	scheduleIntervalPeriod="AM"
	scheduleIntervalDay="Mon"
	reAttemptInterval="10"
	reAttemptIntervalType=mapi_util.random_str(20)
	reAttemptICRepeat="200"
	"""

	# reAttemptIntervalType="hours/minutes"
	# reAttemptIntervalType=special chars
	# result : HTTP Error 500: There is an error in XML document (8, 52).
	"""
	scheduleType="Daily"
	scheduleIntervalTime="09:30:15"
	scheduleIntervalPeriod="AM"
	scheduleIntervalDay="Mon"
	reAttemptInterval="10"
	reAttemptIntervalType=mapi_util.SPECIAL_CHARS
	reAttemptICRepeat="200"
	"""

	# reAttemptIntervalType="hours/minutes"
	# reAttemptIntervalType="HOURS", case sensitive test
	# result : HTTP Error 500: Internal Server Error
	"""
	scheduleType="Daily"
	scheduleIntervalTime="09:30:15"
	scheduleIntervalPeriod="AM"
	scheduleIntervalDay="Mon"
	reAttemptInterval="10"
	reAttemptIntervalType="HOURS"
	reAttemptICRepeat="200"
	"""


	# reAttemptICRepeat=100 ? this field is changable by API
	# result : ok
	"""
	scheduleType="Daily"
	scheduleIntervalTime="09:30:15"
	scheduleIntervalPeriod="AM"
	scheduleIntervalDay="Mon"
	reAttemptInterval="10"
	reAttemptIntervalType="hours"
	reAttemptICRepeat="50"
	"""

	# reAttemptICRepeat=""
	# result : HTTP Error 500: Internal Server Error
	"""
	scheduleType="Daily"
	scheduleIntervalTime="09:30:15"
	scheduleIntervalPeriod="AM"
	scheduleIntervalDay="Mon"
	reAttemptInterval="10"
	reAttemptIntervalType="hours"
	reAttemptICRepeat=""
	"""

	# reAttemptICRepeat="0"
	# result : ok
	"""
	scheduleType="Daily"
	scheduleIntervalTime="09:30:15"
	scheduleIntervalPeriod="AM"
	scheduleIntervalDay="Mon"
	reAttemptInterval="10"
	reAttemptIntervalType="hours"
	reAttemptICRepeat="0"
	"""

	# reAttemptICRepeat="-1" ? can take negative integers?
	# result : ok
	"""
	scheduleType="Daily"
	scheduleIntervalTime="09:30:15"
	scheduleIntervalPeriod="AM"
	scheduleIntervalDay="Mon"
	reAttemptInterval="10"
	reAttemptIntervalType="hours"
	reAttemptICRepeat="-1"
	"""

	# reAttemptICRepeat="2147483647" max int
	# result : ok
	"""
	scheduleType="Daily"
	scheduleIntervalTime="09:30:15"
	scheduleIntervalPeriod="AM"
	scheduleIntervalDay="Mon"
	reAttemptInterval="10"
	reAttemptIntervalType="hours"
	reAttemptICRepeat="2147483647"
	"""

	# reAttemptICRepeat="2147483648" max int + 1
	# result : HTTP Error 500: Internal Server Error
	"""
	scheduleType="Daily"
	scheduleIntervalTime="09:30:15"
	scheduleIntervalPeriod="AM"
	scheduleIntervalDay="Mon"
	reAttemptInterval="10"
	reAttemptIntervalType="hours"
	reAttemptICRepeat="2147483648"
	"""

	# reAttemptICRepeat="aaaa", not integer test
	# result : HTTP Error 500: Internal Server Error
	"""
	scheduleType="Daily"
	scheduleIntervalTime="09:30:15"
	scheduleIntervalPeriod="AM"
	scheduleIntervalDay="Mon"
	reAttemptInterval="10"
	reAttemptIntervalType="hours"
	reAttemptICRepeat="aaaa"
	"""

	"""
	print putSecurityGroupSetting(scheduleType,
							scheduleIntervalTime,
							scheduleIntervalPeriod,
							scheduleIntervalDay,
							reAttemptInterval,
							reAttemptIntervalType,
							reAttemptICRepeat)
	"""