import time
import mapi_lib
import logging
import mapi_util
import simulator_lib

policy_log = logging.getLogger('policy_logger')
policy_log.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(levelname)s][%(filename)s][%(funcName)s][%(lineno)d]-%(message)s ')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
policy_log.addHandler(handler)



def listAllSecurityRules():
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")

	xml_result = broker_api_lib.listAllSecurityRules()
	if not xml_result:
		policy_log.debug("call listAllSecurityRules return False")
		return False

	sg_rule_nodes = xml_result.getElementsByTagName("SecurityRuleTypeList")[0]
	sg_rule_type_nodes = sg_rule_nodes.getElementsByTagName("securityRuleType")

	if sg_rule_type_nodes:
		return True
	else:
		policy_log.debug("no security rules are found")
		return False


def getSecurityRule(sr_id):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")

	xml_result = broker_api_lib.getSecurityRule(sr_id)
	if not xml_result:
		policy_log.debug("call getSecurityRule return False")
		return False

	sg_rule_type_node = xml_result.getElementsByTagName("securityRuleType")[0]

	if sg_rule_type_node:
		return True
	else:
		policy_log.debug("rule:%s is not found" % (sr_id))
		return False


def listAllSecurityGroups(policy_name):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	xml_result = broker_api_lib.listAllSecurityGroups()
	if not xml_result:
		policy_log.debug("call listAllSecurityGroups return False")
		return False
	
	policy_list = xml_result.getElementsByTagName("securityGroupList")[0]
	policies = policy_list.getElementsByTagName("securityGroup")
	for policy in policies:
		if policy_name == policy.attributes["name"].value.strip():
			return True

	policy_log.debug("cannot find default policy")
	return False


def getSecurityGroup(policy_name):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	policy_id = broker_api_lib.get_policy_id_from_policy_name(policy_name)
	if not policy_id:
		policy_log.debug("cannot find the policy ID")
		return False

	xml_result = broker_api_lib.getSecurityGroup(policy_id)
	if not xml_result:
		policy_log.debug("call getSecurityGroup return False")
		return False
	
	policy = xml_result.getElementsByTagName("securityGroup")[0]
	if policy_name == policy.attributes["name"].value.strip():
		return True
	else:
		policy_log.debug("fail to find the default policy")
		return False



# ToDo: for now support only auto-create 1 image with many devices
# device to be included in the policy has to be encrypted
def createSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					device_id_list,image_id_list, security_rule_list):

	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")

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
		policy_log.error("Failed to get source device msuid")
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
		policy_log.error("call updateDevice return False")
		return False

	xml_result = broker_api_lib.encryptDevice(device_msuid)
	if not xml_result:
		policy_log.error("call encryptDevice return False")
		return False

	simulator_lib.encrypt_device(config_name, image_id, [device_id])

	# create policy
	xml_result = broker_api_lib.createSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					device_id_list,image_id_list, security_rule_list)
	if not xml_result:
		policy_log.error("call createSecurityGroup return False")
		return False

	# check if policy is created
	policy_id = broker_api_lib.get_policy_id_from_policy_name(policy_name)

	#delete policy
	xml_result = broker_api_lib.deleteSecurityGroup(policy_id)
	if not xml_result:
		policy_log.error("call deleteSecurityGroup return False")
		return False

	if policy_id:
		return True
	else:
		policy_log.error("policy is not found after create")
		return False


def updateSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					new_device_id_list, new_image_id_list, security_rule_list):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")

	#upload and encrypt device for policy test
	config_name="updateSecurityGroup_orig"
	csp_provider="updateSecurityGroup_orig_csp"
	csp_zone="updateSecurityGroup_orig_zone"
	device_id_list=["updateSecurityGroup_orig_device1"]
	image_id_list=["updateSecurityGroup_orig_image"]

	image_id=image_id_list[0]

	simulator_lib.create_config(config_name, csp_provider, csp_zone, image_id, device_id_list)
	simulator_lib.upload_inventory(config_name, image_id)

	device_id = device_id_list[0]
	device_msuid = broker_api_lib.get_device_msuid_from_device_id(device_id)
	if not device_msuid:
		policy_log.error("Failed to get source device msuid")
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
		policy_log.error("call updateDevice return False")
		return False

	xml_result = broker_api_lib.encryptDevice(device_msuid)
	if not xml_result:
		policy_log.error("call encryptDevice return False")
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
		policy_log.debug("call createSecurityGroup return False")
		return Fals


	# find if there is such policy existing
	policy_id = broker_api_lib.get_policy_id_from_policy_name(policy_name_orig)
	if not policy_id:
		policy_log.debug("policy is not found after create")
		return False



	#create another device for policy update
	#upload and encrypt device for policy test
	config_name="updateSecurityGroup"
	csp_provider="updateSecurityGroup_csp"
	csp_zone="updateSecurityGroup_zone"
	image_id_list = new_image_id_list
	device_id_list = new_device_id_list
	image_id=image_id_list[0]

	simulator_lib.create_config(config_name, csp_provider, csp_zone, image_id, device_id_list)
	simulator_lib.upload_inventory(config_name, image_id)

	device_id = device_id_list[0]
	device_msuid = broker_api_lib.get_device_msuid_from_device_id(device_id)
	if not device_msuid:
		policy_log.error("Failed to get source device msuid")
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
		policy_log.error("call updateDevice return False")
		return False

	xml_result = broker_api_lib.encryptDevice(device_msuid)
	if not xml_result:
		policy_log.error("call encryptDevice return False")
		return False

	simulator_lib.encrypt_device(config_name, image_id, [device_id])





	# update policy
	xml_result = broker_api_lib.updateSecurityGroup(policy_id, EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					new_device_id_list,new_image_id_list, security_rule_list)
	if not xml_result:
		policy_log.debug("call updateSecurityGroup return False")
		return False


	xml_result = broker_api_lib.getSecurityGroup(policy_id)
	if not xml_result:
		policy_log.debug("call getSecurityGroup return False")
		return False

	current_policy = xml_result.getElementsByTagName("securityGroup")[0]
	
	result = broker_api_lib.compare_policy(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					new_device_id_list,new_image_id_list, security_rule_list, current_policy)


	#delete policy
	xml_result = broker_api_lib.deleteSecurityGroup(policy_id)
	if not xml_result:
		policy_log.debug("call deleteSecurityGroup return False")
		return False


	if result:
		return True
	else:
		policy_log.debug("Values are not the same after update")



def deleteSecurityGroup(policy_name):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	#upload and encrypt device for policy test
	config_name="deleteSecurityGroup"
	csp_provider="deleteSecurityGroup_csp"
	csp_zone="deleteSecurityGroup_zone"
	device_id_list=["deleteSecurityGroup_device1"]
	image_id_list=["deleteSecurityGroup_image"]

	image_id=image_id_list[0]

	simulator_lib.create_config(config_name, csp_provider, csp_zone, image_id, device_id_list)
	simulator_lib.upload_inventory(config_name, image_id)

	device_id = device_id_list[0]
	device_msuid = broker_api_lib.get_device_msuid_from_device_id(device_id)
	if not device_msuid:
		policy_log.error("Failed to get source device msuid")
		return False

	#configure device
	device_name=device_id
	device_os="windows"
	device_fs="ntfs"
	write_permission="true"
	device_desc="this is deleteSecurityGroup"
	device_mount_point="H"
	device_key_size="128"
	xml_result = broker_api_lib.updateDevice(device_msuid, device_id, device_name, device_os, device_fs, write_permission, device_desc, device_mount_point, device_key_size, image_id)
	if not xml_result:
		policy_log.error("call updateDevice return False")
		return False

	xml_result = broker_api_lib.encryptDevice(device_msuid)
	if not xml_result:
		policy_log.error("call encryptDevice return False")
		return False

	simulator_lib.encrypt_device(config_name, image_id, [device_id])


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
	security_rule_list=["Key Request Date,MatchAll,equalGreaterThan#6/1/2012"]

	# create policy
	xml_result = broker_api_lib.createSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					device_id_list,image_id_list, security_rule_list)
	if not xml_result:
		policy_log.debug("call createSecurityGroup return False")
		return False

	# check if policy is created
	policy_id = broker_api_lib.get_policy_id_from_policy_name(policy_name)
	if not policy_id:
		policy_log.debug("policy is not found after create")
		return False

	#delete policy
	xml_result = broker_api_lib.deleteSecurityGroup(policy_id)
	if not xml_result:
		policy_log.debug("call deleteSecurityGroup return False")
		return False


	policy_id = broker_api_lib.get_policy_id_from_policy_name(policy_name)
	if not policy_id:
		return True
	else:
		policy_log.debug("policy still existing after deleting")
		return False


def getSecurityGroupSetting():
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	xml_result = broker_api_lib.getSecurityGroupSetting()
	if not xml_result:
		policy_log.debug("call getSecurityGroupSetting return False")
		return False

	#todo check settings	
	sg_setting = xml_result.getElementsByTagName("securityGroupSetting")[0]
	if sg_setting:
		return True
	else:
		policy_log.debug("security setting is not found")
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
		policy_log.debug("call putSecurityGroupSetting return False")
		return False

	xml_result = broker_api_lib.getSecurityGroupSetting()
	if not xml_result:
		policy_log.debug("call getSecurityGroupSetting return False")
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
		policy_log.debug("some values are not the same after update")
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
		policy_log.debug("fail to change security group setting back")
		return False

	if is_the_same:
		return True
	else:
		return False




if __name__ == '__main__':

	rule_mapping ={"Device Access Type":"5d14057d-3277-4ab9-9d3e-e808acbb9c65",
				  "Device Mount Point":"c91f0521-a6cc-4e78-bb37-4a41dc378d3c",
				  "Device Access Type":"5d14057d-3277-4ab9-9d3e-e808acbb9c65",
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


	#print listAllSecurityRules()

	#print getSecurityRule(rule_mapping["Instance First Seen"])

	policy_name = "Default Policy"
	#print listAllSecurityGroups(policy_name)

	policy_name = "Default Policy"
	#policy_name = "test"
	#print getSecurityGroup(policy_name)


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


	#print createSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
	#				RevokeIntervalType, policy_name, isResourcePool, description, \
	#				successAction, successActionDelay, failAction, failActionDelay, \
	#				device_id_list,image_id_list, security_rule_list)

	#policy_name = "delete_policy_test"
	#print deleteSecurityGroup(policy_name)


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
	#print updateSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
	#				RevokeIntervalType, policy_name, isResourcePool, description, \
	#				successAction, successActionDelay, failAction, failActionDelay, \
	#				device_id_list,image_id_list, security_rule_list)


	#print getSecurityGroupSetting()

	#7:50 on UI = 3:50 
	scheduleType="Weekly"
	scheduleIntervalTime="8:00:00"
	scheduleIntervalPeriod="AM"
	scheduleIntervalDay="Wed"
	reAttemptInterval="2"
	reAttemptIntervalType="hours"
	reAttemptICRepeat="200"

	print putSecurityGroupSetting(scheduleType,
							scheduleIntervalTime,
							scheduleIntervalPeriod,
							scheduleIntervalDay,
							reAttemptInterval,
							reAttemptIntervalType,
							reAttemptICRepeat)