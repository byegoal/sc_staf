import sys
import time
import broker_api
import xml
import logging

try:
	import uuid
except ImportError:
	print("import uuid error")
import mapi_util
import mapi_config

logging.basicConfig(level=mapi_config.log_level)

IS_LOGGING = mapi_config.mapi_lib_IS_LOGGING
LOG_TO_FILE = mapi_config.mapi_lib_LOG_TO_FILE
XML_LOG_PATH = mapi_config.mapi_lib_XML_LOG_PATH
LOG_PATH = mapi_config.mapi_lib_LOG_PATH
IS_SHOW = mapi_config.mapi_lib_IS_SHOW
import secureCloud.agentBVT.util
import secureCloud.scAgent.file
import secureCloud.config.result_config
log_path = secureCloud.config.result_config.result_path
chefLogger = secureCloud.config.result_config.chefLogger
stafLogger = secureCloud.config.result_config.stafLogger
errorLogger = secureCloud.config.result_config.errorLogger

class mapi_lib:

	def __init__(self, auth_type=None, broker=None, broker_passphrase=None, realm=None, access_key_id=None, secret_access_key=None, api_account_id=None, api_passphrase=None, user_name=None, user_pass=None, no_init=False):
		self.broker_api = broker_api.broker_api(auth_type, broker, broker_passphrase, realm, access_key_id, secret_access_key, api_account_id, api_passphrase, user_name, user_pass, no_init)

		#log setting
		# To-Do get logging from config and set

	def log_xml(self, result, log_name):
		if(IS_SHOW):
			print result
		if(LOG_TO_FILE):
			xml_obj = xml.dom.minidom.parseString(result)
			pretty_xml = xml_obj.toprettyxml()
			new_log_name = XML_LOG_PATH+log_name+"-formated.xml"
			#print log_name
			f = open(new_log_name, "w")
			f.write(pretty_xml)
			f.close()
			new_log_name2 = XML_LOG_PATH+log_name+".xml"
			f2 = open(new_log_name2, "w")
			f2.write(result)
			f2.close()
			

	# VM
	def listVM(self):
		result = self.broker_api.listVM()
		if not result:
			return False
		self.log_xml(result, self.listVM.__name__)
		xmldata = xml.dom.minidom.parseString(result)
		return xmldata


	def readVM(self, vm_guid):
		result = self.broker_api.readVM(vm_guid)
		stafLogger.debug("readVM() result=%s"%str())
		if not result:
			return False		
		self.log_xml(result, self.readVM.__name__)
		xmldata = xml.dom.minidom.parseString(result)
		return xmldata

	def updateVM(self,vm_guid,vm_name,auto_prov,securityGroupID):
		request_data = """<vm imageGUID="%s" """ %vm_guid
		request_data += """imageName="%s" """ %vm_name
		request_data += """autoProvision="%s" """ %auto_prov
		request_data += """SecurityGroupGUID="%s" """ %securityGroupID
		request_data += """><imageDescription/></vm>""" 
		stafLogger.debug(request_data)
		result = self.broker_api.updateVM(vm_guid, request_data)	
		stafLogger.debug(result)						
		if not result:
			return False		
		self.log_xml(result, self.updateVM.__name__)
		xmldata = xml.dom.minidom.parseString(result)
		return xmldata
	
	def deleteDevice(self, vm_guid, device_id):
		result = self.broker_api.deleteDevice(vm_guid, device_id)
		return result
	
	def deleteDeviceKey(self, vm_guid, device_guid):
		result = self.broker_api.deleteDeviceKey(vm_guid, device_guid)
		return result

	def cancelPending(self, vm_guid, device_guid):
		result = self.broker_api.cancelPending(vm_guid, device_guid)
		return result

	def deleteVM(self, vm_guid):
		result = self.broker_api.deleteVM(vm_guid)
		stafLogger.debug('deleteVM vm_guid=%s, result=%s'%(vm_guid,str(result)))
		return result

 
	def runningVM(self):
		result = self.broker_api.runningVM()
		if not result:
			return False
		self.log_xml(result, self.runningVM.__name__)
		xmldata = xml.dom.minidom.parseString(result)
		return xmldata

	"""
	<vm imageGUID="639F2224-637D-49AA-876B-AFBAD59AFADA">
      <devices>
            <device msUID="6068C4CA-A5A0-45AF-9266-6A2E9BC929EB" preserveData="no">
                  <fileSystem>ext3</fileSystem>
                  <volume>
                        <mountPoint>/mnt/hd1</mountPoint>
                  </volume>
            </device>
            ...
      </devices>
</vm>
	"""
	def create_ecnrypt_data(self,vm_guid,device_msuid,preserve_data,file_system,mount_point):
		encrypt_data = """<?xml version="1.0" encoding="utf-8"?> """
       
		encrypt_data  += """<vm imageGUID="%s"> """ % (vm_guid)

		encrypt_data += """ <devices> """ 


		encrypt_data += """ <device msUID="%s" preserveData="%s">""" % (device_msuid,preserve_data)
		# for preserve, no nned filesystem and mount point
		if preserve_data =='no':
			if file_system is not None:
					encrypt_data += """<fileSystem>%s</fileSystem>""" % (file_system)
			if mount_point is not None:
					encrypt_data += """<volume><mountPoint>%s</mountPoint></volume>""" % (mount_point)
		encrypt_data += "</device>"
		encrypt_data += """ </devices></vm> """ 
		return encrypt_data
	
	def encryptVM(self,vm_guid,encrypt_data):       	   
		result = self.broker_api.encryptVM(vm_guid, encrypt_data)
		stafLogger.debug("Invoke encryptVM() result=%s"%result)
		return result
	
	""" Sample
	<?xml version="1.0" encoding="utf-8"?>
	<device
		msUID="6068C4CA-A5A0-45AF-9266-6A2E9BC929EB"
		name="/dev/raid"
		raidLevel="RAID0">
		<description />
		<fileSystem>ext3</fileSystem>
		<volume><mountPoint>/mnt/hd1</mountPoint></volume>
		<subDevices><device msUID="20429344-1a3b-4676-bbc9-7b8b6db66d67" /></subDevices>
	</device>
	"""
	def create_raid_data(self, raid_msuid, raid_name, raid_level, raid_fs, device_id_list, raid_desc, mount_point):
		raid_data = """<device xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" version="1" """

		if not raid_msuid:
			raid_data += """ msUID="%s" """ % (uuid.uuid4())
		else:
			raid_data += """ msUID="%s" """ % (raid_msuid)

		if raid_name is not None:
			raid_data += """ name="%s" """ % (raid_name)

		if raid_level is not None:
			raid_data += """ raidLevel="%s" """ % (raid_level)

		raid_data += ">"

		if raid_desc is not None:
			if raid_desc:
				raid_data += """<description>%s</description>""" % (raid_desc)

		if raid_fs is not None:
			if raid_fs:
				raid_data += """<fileSystem>%s</fileSystem>""" % (raid_fs)

		if device_id_list is not None:
			raid_data += """<subDevices>"""
			for device_id in device_id_list:
				raid_data += """<device msUID="%s" />""" % (device_id)
			raid_data += """</subDevices>"""

		if mount_point is not None:
			raid_data += """<volume><mountPoint>%s</mountPoint></volume>""" % (mount_point)

		raid_data += """</device>"""

		return raid_data


	def createRAID(self, vm_guid, raid_msuid, raid_name, raid_level, raid_fs, device_id_list, raid_desc, mount_point):
		raid_data = self.create_raid_data(raid_msuid, raid_name, raid_level, raid_fs, device_id_list, raid_desc, mount_point)
		logging.debug(raid_data)
		result = self.broker_api.createRAID(vm_guid, raid_data)
		#self.log_xml(result, self.createRAID.__name__)
		#xmldata = xml.dom.minidom.parseString(result)
		return result


	def encryptRAID(self, vm_guid, raid_guid, file_system, mount_point):
		#encrypt_data = """<device xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" version="1" msUID="%s" provisionState="%s" />""" % (raid_msuid, provision_state)
		encrypt_data = """<vm imageGUID="%s" ><devices>
		<device msUID="%s" preserveData="no">
			<fileSystem>%s</fileSystem>
			<volume><mountPoint>%s</mountPoint></volume>
		</device></devices></vm>""" % (vm_guid, raid_guid, file_system, mount_point)
		logging.debug(encrypt_data)
		result = self.broker_api.encryptRAID(vm_guid, encrypt_data)
		return result


	#reference
	"""
<?xml version="1.0" encoding="utf-8"?>
<securityGroup 
	version="3.5" 
	id="9d010e91-f2e4-492a-b148-3cac5193c272" 
	name="mapi_test" 
	isDeleteble="true" 
	isNameEditable="true" 
	href="http://ms.lab.securecloud.com:80/Broker/API.svc/v3.5/securityGroup/9d010e91-f2e4-492a-b148-3cac5193c272/" 
	lastModified="2013-07-24T09:11:46" 
	ruleCount="0" 
	imageCount="0" 
	EnableIC="true" 
	ICAction="Revoke" 
	PostponeEnable="true" 
	RevokeIntervalType="Hour" 
	RevokeIntervalNumber="2" 
	xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
		<description>this is mapi test</description>
		<successAction action="Approve" autoDelay="-1"/>
		<failedAction action="ManualApprove" autoDelay="15"/>
		<vmList>
			<vms>
				<vm 
					imageGUID="7891e33f-7235-4de2-abf8-816320ba50ad" 
					imageID="7891E33F-7235-4DE2-ABF8-816320BA50AD" 
					imageName="Agent-BVT.AgentBVT_org.vApp_agentBVT.AgentBVT-Vcloud-Win2k8-R2-x64">
					<imageDescription/>
				</vm>
			</vms>
		</vmList>
		<securityRuleList>
			<securityRule 
			id="1338779b-2683-474b-a9a7-298176564a6f" 
			description="" 
			matchType="MatchAll" 
			dataMissing="Failed">
				<securityRuleType 
					id="1338779b-2683-474b-a9a7-298176564a6f" 
					name="Key Request Date" 
					evaluator="lessThan" 
					context="" 
					dataType="Date"/>
				<securityRuleConditionList>
					<securityRuleCondition evaluator="equalGreaterThan" expectedValue="6/1/2012"/>
				</securityRuleConditionList>
			</securityRule>
		</securityRuleList>
	</securityGroup>
	"""
	# ICAction="Revoke" / "Nothing"
	# successAction= ManualApprove/Approve/Deny
	def create_policy_data(self, policy_id, EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
						RevokeIntervalType, policy_name, isResourcePool, description, \
						successAction, successActionDelay, failAction, failActionDelay, \
						device_id_list,image_id_list, security_rule_list, \
						formatted_security_rule_list, isDeleteble="true", isNameEditable="true"):
		policy_data = """<?xml version="1.0" ?>
	<securityGroup
		id="%s" """ % (policy_id)

		if EnableIC:
			policy_data += """ EnableIC="%s" """ % (EnableIC)

		if ICAction:
			policy_data += """ ICAction="%s" """ % (ICAction)

		if PostponeEnable:
			policy_data += """ PostponeEnable="%s" """ % (PostponeEnable)

		if RevokeIntervalNumber:
			policy_data += """ RevokeIntervalNumber="%s" """ % (RevokeIntervalNumber)

		if RevokeIntervalType:
			policy_data += """ RevokeIntervalType="%s" """ % (RevokeIntervalType)

		if policy_name:
			policy_data += """ name="%s" """ % (policy_name)

		if isDeleteble:
			policy_data += """ isDeleteble="%s" """ % (isDeleteble)

		if isNameEditable:
			policy_data += """ isNameEditable="%s" """ %(isNameEditable)

		if isResourcePool:
			policy_data += """ isResourcePool="%s" """ % (isResourcePool)

		policy_data += """ version="1"
		xmlns:xsd="http://www.w3.org/2001/XMLSchema"
		xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"> """

		if description:
			policy_data += """<description>%s</description>""" % (description)
		else:
			policy_data += """<description/>"""

		if successActionDelay:
			policy_data += """<successAction action="%s" autoDelay="%s"/>""" % (successAction, successActionDelay)
		else:
			policy_data += """<successAction action="%s" autoDelay="-1"/>""" % (successAction)
			
		if failActionDelay:
			policy_data += """<failedAction action="%s" autoDelay="%s"/>""" % (failAction, failActionDelay)
		else:
			policy_data += """<failedAction action="%s" autoDelay="-1"/>""" % (failAction)


		if image_id_list:
			policy_data += """<vmList><vms>"""
			for image_id in image_id_list:
				policy_data += """<vm imageID="%s" imageGUID="%s"></vm>""" % (image_id, image_id)
				#policy_data += """<vm id="Agent-BVT.AgentBVT_org.vApp_agentBVT.AgentBVT-Vcloud-Centos63-x86" msUID="%s"></vm>""" % (image_id)
			policy_data += """</vms></vmList>"""


		if formatted_security_rule_list == None:
			security_rule_data = self.create_security_rule(security_rule_list)
		else:
			security_rule_data = formatted_security_rule_list
		policy_data += security_rule_data

		policy_data += "</securityGroup>"
		logging.error(policy_data)
		return policy_data

	def createSecurityGroup(self, EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
						RevokeIntervalType, policy_name, isResourcePool, description, \
						successAction, successActionDelay, failAction, failActionDelay, \
						device_id_list,image_id_list, security_rule_list, formatted_security_rule_list=None):

		policy_data = self.create_policy_data("", EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
						RevokeIntervalType, policy_name, isResourcePool, description, \
						successAction, successActionDelay, failAction, failActionDelay, \
						device_id_list,image_id_list, security_rule_list, formatted_security_rule_list)
		result = self.broker_api.createSecurityGroup(policy_data)
		return result


	def updateSecurityGroup(self, policy_id, EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
						RevokeIntervalType, policy_name, isResourcePool, description, \
						successAction, successActionDelay, failAction, failActionDelay, \
						device_id_list,image_id_list, security_rule_list, formatted_security_rule_list=None):

		policy_data = self.create_policy_data(policy_id, EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
						RevokeIntervalType, policy_name, isResourcePool, description, \
						successAction, successActionDelay, failAction, failActionDelay, \
						device_id_list,image_id_list, security_rule_list, formatted_security_rule_list)
		result = self.broker_api.updateSecurityGroup(policy_id, policy_data)
		if not result:
			return False
		self.log_xml(result, self.updateSecurityGroup.__name__)
		xmldata = xml.dom.minidom.parseString(result)
		return xmldata

	def deleteSecurityGroup(self, sg_id):
		result = self.broker_api.deleteSecurityGroup(sg_id)
		return result
	

	def runningVMKeyRequest(self, key_request_id, action):
		result = self.broker_api.runningVMKeyRequest(key_request_id, action)
		if not result:
			return False
		self.log_xml(result, self.runningVMKeyRequest.__name__)
		xmldata = xml.dom.minidom.parseString(result)
		return xmldata

























	#Legacy


	# inventory
	def cloneDevice(self, from_device_msuid, to_device_msuid):
		clone_data = """<device xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" version="1" msUID="%s" />""" % (to_device_msuid)
		result = self.broker_api.cloneDevice(from_device_msuid, clone_data)
		if not result:
			return False
		self.log_xml(result, self.cloneDevice.__name__)
		xmldata = xml.dom.minidom.parseString(result)
		return xmldata


	def listAllDevices(self):
		result = self.broker_api.listAllDevices()
		if not result:
			return False
		self.log_xml(result, self.listAllDevices.__name__)
		xmldata = xml.dom.minidom.parseString(result)
		return xmldata


	def getDevice(self, device_id):
		result = self.broker_api.getDevice(device_id)
		if not result:
			return False		
		self.log_xml(result, self.getDevice.__name__)
		xmldata = xml.dom.minidom.parseString(result)
		return xmldata


	""" Sample
	<device 
		xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
		xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
		version="1" 
		msUID="675615ab-8bd0-47d1-aa10-2be26fafa6eb" 
		id="test_device" 
		name="test_device_update" 
		os="windows" 
		fs="ntfs" 
		configured="true" 
		writeaccess="true">
		<description>this is test device</description>
		<connections read="1" write="1" />
		<provider name="test_csp" />
		<image />
		<volume><mountPoint>G</mountPoint></volume>
		<keyGen keySize="256" cipher="aes" mode="cbc" />
	</device>
	"""
	def create_device_data(self, device_msuid, device_id, device_name, device_os, device_fs, write_permission, \
						   device_desc, device_mount_point, device_key_size, image_id, is_configure, key_mode):
		device_data = """<?xml version="1.0" encoding="utf-8"?><device xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" version="1" """

		if device_msuid is not None:
			device_data += """ msUID="%s" """ % (device_msuid)

		if device_id is not None:
			device_data += """ id="%s" """ % (device_id)

		if device_name is not None:
			device_data += """ name="%s" """ % (device_name)

		if device_os is not None:
			device_data += """ os="%s" """ % (device_os)

		if device_fs is not None:
			device_data += """ fs="%s" """ % (device_fs)

		if is_configure is not None:
			device_data += """ configured="%s" """ % (is_configure)

		if device_data is not None:
			device_data += """ writeaccess="%s" """ % (write_permission)

		# device status cannot be updated
		#device_data += """ deviceStatus="Encrypted" """
			
		device_data += ">"

		if device_desc is not None:
			if device_desc:
				device_data += """<description>%s</description>""" % (device_desc)
			else:
				device_data += """<description></description>"""

		# it's for resource pool
		#device_data += """<connections read="1" write="1" />"""

		if image_id is not None:
			device_data += """<image id="%s"></image>""" % (image_id)

		if device_mount_point is not None:
			device_data += """<volume><mountPoint>%s</mountPoint></volume>""" % (device_mount_point)


		# only keySize, mode can be updated
		#device_data += """<keyGen keySize="%s" cipher="des" mode="cfb" iv="plain" hash="sha-512" />""" % (device_key_size)
		device_data += """<keyGen keySize="%s" mode="%s" />""" % (device_key_size, key_mode)
		device_data += "</device>"

		return device_data


	def updateDevice(self, device_msuid, device_id, device_name, device_os, device_fs, write_permission, device_desc, device_mount_point, device_key_size, image_id, is_configure="true", key_mode="cbc"):
		device_data = self.create_device_data(device_msuid, device_id, device_name, device_os, device_fs, write_permission, device_desc, device_mount_point, device_key_size, image_id, is_configure, key_mode)
		result = self.broker_api.updateDevice(device_msuid, device_data)
		if not result:
			return False
		self.log_xml(result, self.updateDevice.__name__)
		xmldata = xml.dom.minidom.parseString(result)
		return xmldata


	def encryptDevice(self, device_id, provision_state="pending"):
		encrypt_data = """<device xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" version="1" msUID="%s" provisionState="%s" />""" % (device_id, provision_state)
		result = self.broker_api.encryptDevice(device_id, encrypt_data)
		if not result:
			return False
		self.log_xml(result, self.encryptDevice.__name__)
		xmldata = xml.dom.minidom.parseString(result)
		return xmldata


	#later, need security admin account
	def exportDevice(self, device_id, passphrase):
		device_data = """<?xml version="1.0" encoding="utf-8"?><string>%s</string>""" % (passphrase)
		result = self.broker_api.exportDevice(device_id, device_data)
		if not result:
			return False
		self.log_xml(result, self.exportDevice.__name__)
		#xmldata = xml.dom.minidom.parseString(result)
		#return xmldata

		return result


	def listAllImages(self):
		result = self.broker_api.listAllImages()
		if not result:
			return False
		self.log_xml(result, self.listAllImages.__name__)
		xmldata = xml.dom.minidom.parseString(result)
		return xmldata


	def getImage(self, image_id):
		result = self.broker_api.getImage(image_id)
		if not result:
			return False
		self.log_xml(result, self.getImage.__name__)
		xmldata = xml.dom.minidom.parseString(result)
		return xmldata


	"""<?xml version="1.0" ?>
		<image 
			encryptSwap="true" 
			id="test_image"
			msUID="af7bbda7-e53f-4e78-8f9d-dadccbbb01c5"
			name="test_image">
			<description>%s<description/>
			<provider href="https://mapi_server.securecloud.com:8443/Broker/API.svc/provider/test_csp/" name="test_csp"/>
		</image>"""
	def create_image_data(self, image_msuid, image_id, image_name, image_desc, image_encrypt_swap):
		image_data = """<?xml version="1.0" ?><image xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" version="1" msUID="%s" """ % (image_msuid)
		if image_encrypt_swap is not None:
			image_data += """ encryptSwap="%s" """ % (image_encrypt_swap)

		if image_id is not None:
			image_data += """ id="%s" """ % (image_id)

		if image_name is not None:
			image_data += """ name="%s" """ % (image_name)

		image_data += ">"

		if image_desc is not None:
			image_data += """ <description>%s</description> """ % (image_desc)
		else:
			image_data += """ <description/> """

		image_data += "</image>"

		return image_data


	def updateImage(self, image_msuid, image_id, image_name, image_desc, image_encrypt_swap, provider_name=""):
		image_data = self.create_image_data(image_msuid, image_id, image_name, image_desc, image_encrypt_swap)
		result = self.broker_api.updateImage(image_msuid, image_data)
		if not result:
			return False
		self.log_xml(result, self.updateImage.__name__)
		xmldata = xml.dom.minidom.parseString(result)
		return xmldata


	def deleteImage(self, image_id):
		result = self.broker_api.deleteImage(image_id)
		return result




	def readRAID(self, raid_id):
		result = self.broker_api.readRAID(raid_id)
		if not result:
			return False
		self.log_xml(result, self.readRAID.__name__)
		xmldata = xml.dom.minidom.parseString(result)
		return xmldata


	def updateRAID(self, raid_msuid, raid_id, raid_name, raid_level, raid_os, raid_fs, write_permission, provider_zone, device_id_list, raid_desc, provider, image_id, mount_point, key_size, is_configure="true", key_mode="cbc", is_detachable="false"):
		raid_data = self.create_raid_data(raid_msuid, raid_id, raid_name, raid_level, raid_os, raid_fs, write_permission, provider_zone, device_id_list, raid_desc, provider, image_id, mount_point, key_size, is_configure, key_mode, is_detachable)
		result = self.broker_api.updateRAID(raid_msuid, raid_data)
		if not result:
			return False
		self.log_xml(result, self.updateRAID.__name__)
		xmldata = xml.dom.minidom.parseString(result)
		return xmldata


	def deleteRAID(self, raid_msuid):
		result = self.broker_api.deleteRAID(raid_msuid)
		return result


	# policy
	def listAllSecurityGroups(self):
		result = self.broker_api.listAllSecurityGroups()
		if not result:
			return False
		self.log_xml(result, self.listAllSecurityGroups.__name__)
		xmldata = xml.dom.minidom.parseString(result)
		return xmldata

	def getSecurityGroup(self, sg_id):
		result = self.broker_api.getSecurityGroup(sg_id)
		if not result:
			return False
		self.log_xml(result, self.getSecurityGroup.__name__)
		xmldata = xml.dom.minidom.parseString(result)
		return xmldata







	def getSecurityGroupSetting(self):
		result = self.broker_api.getSecurityGroupSetting()
		if not result:
			return False
		self.log_xml(result, self.createSecurityGroup.__name__)
		xmldata = xml.dom.minidom.parseString(result)
		return xmldata


	# example
	"""
	def putSecurityGroupSetting(scheduleType="Daily",
								scheduleIntervalTime="1:00:00",
								scheduleIntervalPeriod="PM",
								scheduleIntervalDay="Sun",
								reAttemptInterval="30",
								reAttemptIntervalType="minutes",
								reAttemptICRepeat="100"):
	"""
	def putSecurityGroupSetting(self, scheduleType,
								scheduleIntervalTime,
								scheduleIntervalPeriod,
								scheduleIntervalDay,
								reAttemptInterval,
								reAttemptIntervalType,
								reAttemptICRepeat):
		sgs_data = """<?xml version="1.0" encoding="utf-8"?>
		<securityGroupSetting
		ScheduleType="%s"
		ScheduleIntervalTime="%s"
		ScheduleIntervalPeriod="%s"
		ScheduleIntervalDay="%s"
		ReAttemptInterval="%s"
		ReAttemptIntervalType="%s"
		ReAttemptICRepeat="%s"/>""" % (scheduleType,scheduleIntervalTime,scheduleIntervalPeriod,scheduleIntervalDay,reAttemptInterval,reAttemptIntervalType,reAttemptICRepeat)
		result = self.broker_api.putSecurityGroupSetting(sgs_data)
		if not result:
			return False
		self.log_xml(result, self.putSecurityGroupSetting.__name__)
		xmldata = xml.dom.minidom.parseString(result)
		return xmldata

	def listAllSecurityRules(self):
		result = self.broker_api.listAllSecurityRules()
		if not result:
			return False
		self.log_xml(result, self.listAllSecurityRules.__name__)
		xmldata = xml.dom.minidom.parseString(result)
		return xmldata

	def getSecurityRule(self, sr_id):
		result = self.broker_api.getSecurityRule(sr_id)
		if not result:
			return False
		self.log_xml(result, self.getSecurityRule.__name__)
		xmldata = xml.dom.minidom.parseString(result)
		return xmldata


	#Instance
	def getDeviceKeyRequest(self, kr_id):
		result = self.broker_api.getDeviceKeyRequest(kr_id)
		if not result:
			return False
		self.log_xml(result, self.getDeviceKeyRequest.__name__)
		xmldata = xml.dom.minidom.parseString(result)
		return xmldata

	#reference
	"""<?xml version="1.0" encoding="utf-8"?>
	<deviceKeyRequest
		version="1"
		id="0fde4b98-f327-4976-a360-8d9574fa2ad4"
		xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
		xmlns:xsd="http://www.w3.org/2001/XMLSchema">
			<deviceKeyRequestState>pending</deviceKeyRequestState>
			<mountPoint>H</mountPoint>
			<keyRequest id="cd718d5e-b12b-4c84-9fe3-a74a2dde518d">
				<request date="2012-06-28T09:51:46.66">
					<ipAddress>172.18.3.76</ipAddress>
				</request>
				<instance id="getDeviceKeyRequest_instance" >
					<location><name>us-east-1a</name></location>
					<status
						instanceStatus="Unknown"
						firstSeen="2012-06-28T09:50:30.857"
						lastSeen="2012-06-28T09:51:45.86"/>
					<image
						id="getDeviceKeyRequest_image"
						name="getDeviceKeyRequest_image"
						lastModified="2012-06-28T09:51:47.7695223Z"
						encryptSwap="false">
						<description/>
						<provider name="getDeviceKeyRequest_csp" />
					</image>
				</instance>
			</keyRequest>
			<options hasKey="True"/>
			<linkList><link res="RuleEvaluations" /></linkList>
	</deviceKeyRequest>"""
	def create_dkr_data(self, dkr_id, dkr_status):
		dkr_data = """<?xml version="1.0" encoding="utf-8"?>"""
		#dkr_data += """<deviceKeyRequest id="%s" version="1" """ % (dkr_id)
		dkr_data += """<deviceKeyRequest version="1" """
		dkr_data += """ xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">"""
			
		dkr_data += """<deviceKeyRequestState>%s</deviceKeyRequestState>""" % (dkr_status)
		#dkr_data += """<mountPoint>%s</mountPoint>""" % (mount_point)

		"""
				<keyRequest id="cd718d5e-b12b-4c84-9fe3-a74a2dde518d">
					<request date="2012-06-28T09:51:46.66">
						<ipAddress>172.18.3.76</ipAddress>
					</request>
					<instance id="getDeviceKeyRequest_instance" >
						<location><name>us-east-1a</name></location>
						<status
							instanceStatus="Unknown"
							firstSeen="2012-06-28T09:50:30.857"
							lastSeen="2012-06-28T09:51:45.86"/>
						<image
							id="getDeviceKeyRequest_image"
							name="getDeviceKeyRequest_image"
							lastModified="2012-06-28T09:51:47.7695223Z"
							encryptSwap="false">
							<description/>
							<provider name="getDeviceKeyRequest_csp" />
						</image>
					</instance>
				</keyRequest>
		"""

		#dkr_data += """<options hasKey="True"/>"""
		#dkr_data += """<linkList><link res="RuleEvaluations" /></linkList>"""
		dkr_data += """</deviceKeyRequest>"""

		return dkr_data

	def updateDeviceKeyRequest(self, dkr_id, dkr_status):
		dkr_data = self.create_dkr_data(dkr_id, dkr_status)
		result = self.broker_api.updateDeviceKeyRequest(dkr_id, dkr_data)
		if not result:
			return False
		self.log_xml(result, self.updateDeviceKeyRequest.__name__)
		xmldata = xml.dom.minidom.parseString(result)
		return xmldata


	def getInstance(self, instance_id):
		result = self.broker_api.getInstance(instance_id)
		if not result:
			return False
		self.log_xml(result, self.getInstance.__name__)
		xmldata = xml.dom.minidom.parseString(result)
		return xmldata

	def flatRequests(self):
		result = self.broker_api.flatRequests()
		if not result:
			return False
		self.log_xml(result, self.flatRequests.__name__)
		xmldata = xml.dom.minidom.parseString(result)
		return xmldata

	def listAllRuleResults(self, dkr_id):
		result = self.broker_api.listAllRuleResults(dkr_id)
		if not result:
			return False
		self.log_xml(result, self.listAllRuleResults.__name__)
		xmldata = xml.dom.minidom.parseString(result)
		return xmldata

	def listLimitedRuleResults(self, dkr_id, rule_pattern):
		result = self.broker_api.listLimitedRuleResults(dkr_id, rule_pattern)
		if not result:
			return False
		self.log_xml(result, self.listLimitedRuleResults.__name__)
		xmldata = xml.dom.minidom.parseString(result)
		return xmldata

	#no more this API
	def keyRequestTree(self, pattern):
		result = self.broker_api.keyRequestTree(pattern)
		if not result:
			return False
		self.log_xml(result, self.keyRequestTree.__name__)
		xmldata = xml.dom.minidom.parseString(result)
		return xmldata


	# accounts and users
	def listCurrentUserAccounts(self):
		result = self.broker_api.listCurrentUserAccounts()
		if not result:
			return False
		self.log_xml(result, self.listCurrentUserAccounts.__name__)
		xmldata = xml.dom.minidom.parseString(result)
		return xmldata

	def getCurrentAccount(self):
		result = self.broker_api.getCurrentAccount()
		if not result:
			return False
		
		self.log_xml(result, self.getCurrentAccount.__name__)

		objWriteFile = open("C:\\Documents and Settings\\Administrator\\Desktop\\result.log","a")
		objWriteFile.writelines(result+"\n")
		objWriteFile.close()
	
		xmldata = xml.dom.minidom.parseString(result)
		
		return xmldata


	def create_account_data(self, account_id, account_name=None, passphrase=None, timezone=None, dateFormat=None, session_timeout=None):
		account_data = "<account id=\"%s\" " % (account_id)

		if account_name is not None:
			account_data += """ name="%s" """ % (account_name)

		if passphrase is not None:
			account_data += """ passphrase="%s" """ % (passphrase)

		if timezone is not None:
			account_data += """ timezoneID="%s" """ % (timezone)

		if dateFormat is not None:
			account_data += """ dateFormat="%s" """ % (dateFormat)

		if session_timeout is not None:
			account_data += """ sessionTimeout="%s" """ % (session_timeout)
			
		account_data += " />"

		return account_data

	def updateAccountSettings(self, account_id, new_timezone, new_dateFormat, new_session_timeout):
		account_info = self.create_account_data(account_id, timezone=new_timezone, dateFormat=new_dateFormat, session_timeout=new_session_timeout)
		result = self.broker_api.updateAccountSettings(account_info)
		if not result:
			return False
		self.log_xml(result, self.updateAccountSettings.__name__)
		xmldata = xml.dom.minidom.parseString(result)
		return xmldata



	# authentication 

	def digest_authentication_test(self, realm, digest_broker_name, digest_broker_pass, header_broker_name):
		result = self.broker_api.digest_authentication_test(realm, digest_broker_name, digest_broker_pass, header_broker_name)
		return result


	def get_certificate(self):
		result = self.broker_api.get_certificate()
		if result:
			return True
		else:
			return False


	def basic_auth(self, encrypt_pass=True):
		result = self.broker_api.basic_auth(encrypt_pass)
		if result:
			return True
		else:
			return False


	def userAuthenticationRequest(self):
		result = self.broker_api.userAuthenticationRequest()
		if result:
			return True
		else:
			return False


	def userAuthenticationResponse(self, ext_auth_id=None, ext_random_data=None, auth_id_sensitive=False, random_data_sensitive=False, use_external_data=False):
		auth_id, random_data = self.broker_api.userAuthenticationRequest()

		if not auth_id:
			return False

		if ext_auth_id is not None:
			auth_id = ext_auth_id

		if ext_random_data is not None:
			random_data = ext_random_data

		if auth_id_sensitive:
			auth_id = auth_id.upper()

		result = self.broker_api.userAuthenticationResponse(auth_id, random_data, use_external_data, random_data_sensitive)

		if result:
			return True
		else:
			return False






	# --------------------------------------------------------------------------------
	# helper functions
	def get_account_id_from_account_name(self, account_name):
		accounts_xml = self.listCurrentUserAccounts()
		account_list = accounts_xml.getElementsByTagName("accountList")[0]
		accounts = account_list.getElementsByTagName("account")

		for account in accounts:
			if account_name == account.attributes["name"].value.strip():
				return account.attributes["id"].value.strip()

		return ""

	def get_user_id_from_user_name(self, user_name):
		users_xml = self.listAllUsers()
		user_list = users_xml.getElementsByTagName("userList")[0]
		users = user_list.getElementsByTagName("user")

		for user in users:
			if user_name == user.attributes["loginname"].value.strip():
				return user.attributes["id"].value.strip()

		return ""

	def get_device_msuid_from_device_id(self, device_id):
		devices_xml = self.listAllDevices()
		device_list = devices_xml.getElementsByTagName("deviceList")[0]
		devices = device_list.getElementsByTagName("device")

		for device in devices:
			if device_id == device.attributes["id"].value.strip():
				return device.attributes["msUID"].value.strip()

		return ""

	def get_image_msuid_from_image_id(self, image_id):
		images_xml = self.listAllImages()
		image_list = images_xml.getElementsByTagName("imageList")[0]
		images = image_list.getElementsByTagName("image")

		for image in images:
			if image_id == image.attributes["id"].value.strip():
				return image.attributes["msUID"].value.strip()

		return ""


	def get_instance_msuid_from_instance_id(self, instance_id):
		xml_result = self.flatRequests()
		if not xml_result:
			return ""

		keyRequestTree_node = xml_result.getElementsByTagName("keyRequestTree")[0]
		flatRequests_node = keyRequestTree_node.getElementsByTagName("flatRequests")[0]
		flat_requests = flatRequests_node.getElementsByTagName("flatRequest")

		for flat_request in flat_requests:
			if instance_id == flat_request.attributes["instanceID"].value.strip():
				return flat_request.attributes["instanceMsUID"].value.strip()

		return ""


	def get_dkr_id_from_instance_id(self, instance_id):
		xml_result = self.flatRequests()
		if not xml_result:
			return ""

		keyRequestTree_node = xml_result.getElementsByTagName("keyRequestTree")[0]
		flatRequests_node = keyRequestTree_node.getElementsByTagName("flatRequests")[0]
		flat_requests = flatRequests_node.getElementsByTagName("flatRequest")

		for flat_request in flat_requests:
			if instance_id == flat_request.attributes["instanceID"].value.strip():
				return flat_request.attributes["deviceRequestID"].value.strip()

		return ""


	def get_policy_id_from_policy_name(self, policy_name):
		policy_xml = self.listAllSecurityGroups()
		policy_list = policy_xml.getElementsByTagName("securityGroupList")[0]
		policies = policy_list.getElementsByTagName("securityGroup")

		for policy in policies:
			if policy_name == policy.attributes["name"].value.strip():
				return policy.attributes["id"].value.strip()

		return ""




	"""
	take input string:
	"Request Source IPv6 Address,MatchAll,equal#1.2.3.4$notEqual#1.2.3.5"

	output
	<securityRuleList>
		<securityRule dataMissing="Failed" description="" id="1338779b-2683-474b-a9a7-298176564a6f" matchType="MatchAll">
			<securityRuleConditionList>
				<securityRuleCondition evaluator="equalGreaterThan" expectedValue="6/1/2012"/>
			</securityRuleConditionList>
		</securityRule>
	</securityRuleList>
	"""
	def create_security_rule(self, security_rule_list):

		import mapi_config

		result = "<securityRuleList>"
		
		for security_rule_str in security_rule_list:
			tokens = security_rule_str.split(",")

			rule_name = tokens[0]
			match_type = tokens[1]
			condition_list = tokens[2]
			condition_list = condition_list.split("$")
			
			rule_id = mapi_config.rule_mapping[rule_name]
			result += """<securityRule dataMissing="Failed" description="" id="%s" matchType="%s">""" % (rule_id, match_type)
			result += "<securityRuleConditionList>"
			for condition in condition_list:
				condition_token = condition.split("#")
				evaluator = condition_token[0]
				expected_value = condition_token[1]
				if not evaluator and not expected_value:
					continue

				result += """<securityRuleCondition evaluator="%s" expectedValue="%s"/>""" % (evaluator, expected_value)

		result += "</securityRuleConditionList></securityRule></securityRuleList>"

		return result





	# Notification
	def listAllNotifiers(self):
		result = self.broker_api.listAllNotifiers()
		if not result:
			return False
		self.log_xml(result, self.listAllNotifiers.__name__)
		xmldata = xml.dom.minidom.parseString(result)
		return xmldata

	def getNotificationEvents(self, notify_id):
		result = self.broker_api.getNotificationEvents(notify_id)
		if not result:
			return False
		self.log_xml(result, self.getNotificationEvents.__name__)
		xmldata = xml.dom.minidom.parseString(result)
		return xmldata

	"""
	Reference:
	<?xml version="1.0" ?>
	<notifier 
		xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" 
		xmlns:xsd="http://www.w3.org/2001/XMLSchema" 
		notificationRuleDBID="0" 
		name="mapi_test1" 
		description="this is auto MAPI test" 
		subject="this is MAPI auto-create test" 
		header="this is header" 
		footer="this is footer" 
		frequencyValue="1" 
		frequencyUnit="Minutes">
			<recipients><notificationRecipient emailAddress="danny_shao@trend.com.tw" /></recipients>
			<eventGroups>
				<eventGroup eventGroupCode="KEY_EVENTS">
					<notificationEvent notificationRuleEventDBID="32" enabledInThisNotifier="true" notificationText="The key request for device, [Dev_Name] requires your manual approval." />
					<notificationEvent notificationRuleEventDBID="33" enabledInThisNotifier="true" notificationText="SecureCloud has automatically denied your key request for device, [Dev_Name]." />
					<notificationEvent notificationRuleEventDBID="34" enabledInThisNotifier="true" notificationText="SecureCloud has automatically approved your key request for device, [Dev_Name]." />
					<notificationEvent notificationRuleEventDBID="35" enabledInThisNotifier="true" notificationText="SecureCloud has automatically approved your key request for device, [Dev_Name] after no action was taken." />
					<notificationEvent notificationRuleEventDBID="38" enabledInThisNotifier="true" notificationText="SecureCloud has received a key request for a device ([Dev_Name]) that is not a member of the same policy as the machine image." />
					<notificationEvent notificationRuleEventDBID="43" enabledInThisNotifier="true" notificationText="Instance [Inst_ID] is no longer in compliance with the policy rules as of [Check_Date]." />
				</eventGroup>
				<eventGroup eventGroupCode="PROVISION_EVENTS">
					<notificationEvent notificationRuleEventDBID="57" enabledInThisNotifier="true" notificationText="Device, [Dev_Name] has encountered an error during the encryption process on [Err_Date]" />
					<notificationEvent notificationRuleEventDBID="58" enabledInThisNotifier="true" notificationText="Device, [Dev_Name] is encrypted successfully and is ready for use as of [Complete_Date]" />
					<notificationEvent notificationRuleEventDBID="59" enabledInThisNotifier="true" notificationText="Device, [Dev_Name] has not been seen or modified [Idle_Time] minutes ago from [Start_Date].">
						<userConfigItems><userConfig configName="IDLE_TIME" configValue="5" /></userConfigItems>
					</notificationEvent>
				</eventGroup>
				<eventGroup eventGroupCode="EXTCONN_EVENTS">
					<notificationEvent notificationRuleEventDBID="60" enabledInThisNotifier="true" notificationText="Connection to the ([KMIP_Url]) key server has encountered an error on [Fail_Date]. This error occurred because [Fail_Reason]. You can check your settings with the [Account_Name] account." />
					<notificationEvent notificationRuleEventDBID="61" enabledInThisNotifier="true" notificationText="Connection to the Deep Security Manager ([DSM_Url]) has encountered an error on [Fail_Date]. This error occurred because [Fail_Reason]. You can check your settings with the [Account_Name] account." />
				</eventGroup>
			</eventGroups>
	</notifier>

	frequencyUnit="1"
	frequencyValue="Minutes"

	frequencyUnit="Individual"
	frequencyValue="0"

	requencyValue="5"
	frequencyUnit="Occurrence"
	"""
	def create_notify_data(self, notify_id, notify_name, desc, header, footer, frequencyUnit, frequencyValue, 
						from_email, subject, recipients_list, key_manual_approve_notify, key_manual_approve_notify_text, 
						key_auto_deny_notify, key_auto_deny_notify_text, key_auto_approve_notify, key_auto_approve_notify_text, 
						key_auto_approve_after_delay_notify, key_auto_approve_after_delay_notify_text, 
						kr_device_and_image_belong_diff_policy_notify, kr_device_and_image_belong_diff_policy_notify_text, 
						scim_fail_notify, scim_fail_notify_text, device_provision_notify, device_provision_notify_text, 
						provision_done_notify, provision_done_notify_text, provision_idle_notify, provision_idle_notify_text, provision_idle_time,
						kmip_connection_fail_notify, kmip_connection_fail_notify_text, dsm_connection_fail_notify, dsm_connection_fail_notify_text):

		if notify_id == "":
			notify_id = "0"

		notify_data = """<?xml version="1.0" ?>
	<notifier
		notificationRuleDBID="%s"
		name="%s"
		description="%s"
		header="%s"
		footer="%s"
		frequencyUnit="%s"
		frequencyValue="%s"
		from="%s"
		subject="%s"
		xmlns:xsd="http://www.w3.org/2001/XMLSchema"
		xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">""" % (notify_id,notify_name,desc,header,footer,frequencyUnit,frequencyValue,from_email, subject)

		notify_data += "<recipients>"
		for recipient in recipients_list:
			notify_data += """<notificationRecipient emailAddress="%s"/>""" % (recipient)
		notify_data += "</recipients>"

		notify_data += "<eventGroups>"

		if key_manual_approve_notify or key_auto_deny_notify or key_auto_approve_notify \
		or key_auto_approve_after_delay_notify or kr_device_and_image_belong_diff_policy_notify or scim_fail_notify:
			notify_data += """<eventGroup eventGroupCode="KEY_EVENTS">"""

			if key_manual_approve_notify:
				if key_manual_approve_notify_text == "":
					key_manual_approve_notify_text = "The key request for device, [Dev_Name] requires your manual approval."
				notify_data += """<notificationEvent enabledInThisNotifier="true" notificationRuleEventDBID="32" notificationText="%s" />""" % (key_manual_approve_notify_text)

			if key_auto_deny_notify:
				if key_auto_deny_notify_text == "":
					key_auto_deny_notify_text = "SecureCloud has automatically denied your key request for device, [Dev_Name]."
				notify_data += """<notificationEvent enabledInThisNotifier="true" notificationRuleEventDBID="33" notificationText="%s" />""" % (key_auto_deny_notify_text)

			if key_auto_approve_notify:
				if key_auto_approve_notify_text == "":
					key_auto_approve_notify_text = "SecureCloud has automatically approved your key request for device, [Dev_Name]."
				notify_data += """<notificationEvent enabledInThisNotifier="true" notificationRuleEventDBID="34" notificationText="%s" />""" % (key_auto_approve_notify_text)

			if key_auto_approve_after_delay_notify:
				if key_auto_approve_after_delay_notify_text == "":
					key_auto_approve_after_delay_notify_text = "SecureCloud has automatically approved your key request for device, [Dev_Name] after no action was taken."
				notify_data += """<notificationEvent enabledInThisNotifier="true" notificationRuleEventDBID="35" notificationText="%s" />""" % (key_auto_approve_after_delay_notify_text)

			if kr_device_and_image_belong_diff_policy_notify:
				if kr_device_and_image_belong_diff_policy_notify_text == "":
					kr_device_and_image_belong_diff_policy_notify_text = "SecureCloud has received a key request for a device ([Dev_Name]) that is not a member of the same policy as the machine image."
				notify_data += """<notificationEvent enabledInThisNotifier="true" notificationRuleEventDBID="38" notificationText="%s" />""" % (kr_device_and_image_belong_diff_policy_notify_text)

			if scim_fail_notify:
				if scim_fail_notify_text == "":
					scim_fail_notify_text = "Instance [Inst_ID] is no longer in compliance with the policy rules as of [Check_Date]."
				notify_data += """<notificationEvent enabledInThisNotifier="true" notificationRuleEventDBID="43" notificationText="%s" />""" % (scim_fail_notify_text)

			notify_data += "</eventGroup>"


		if device_provision_notify or provision_done_notify or provision_idle_notify:
			notify_data += """<eventGroup eventGroupCode="PROVISION_EVENTS">"""

			if device_provision_notify:
				if device_provision_notify_text == "":
					device_provision_notify_text = "Device, [Dev_Name] has encountered an error during the encryption process on [Err_Date]"
				notify_data += """<notificationEvent enabledInThisNotifier="true" notificationRuleEventDBID="57" notificationText="%s" />""" % (device_provision_notify_text)

			if provision_done_notify:
				if provision_done_notify_text == "":
					provision_done_notify_text = "Device, [Dev_Name] is encrypted successfully and is ready for use as of [Complete_Date]"
				notify_data += """<notificationEvent enabledInThisNotifier="true" notificationRuleEventDBID="58" notificationText="%s" />""" % (provision_done_notify_text)

			if provision_idle_notify:
				if provision_idle_notify_text == "":
					provision_idle_notify_text = "Device, [Dev_Name] has not been seen or modified [Idle_Time] minutes ago from [Start_Date]."
				if provision_idle_time == "":
					provision_idle_time = "5"
				notify_data += """<notificationEvent enabledInThisNotifier="true" notificationRuleEventDBID="59" notificationText="%s">
					<userConfigItems>
						<userConfig configName="IDLE_TIME" configValue="%s"/>
					</userConfigItems>
				</notificationEvent>""" % (provision_idle_notify_text, provision_idle_time)

			notify_data += "</eventGroup>"


		if kmip_connection_fail_notify or dsm_connection_fail_notify:
			notify_data += """<eventGroup eventGroupCode="EXTCONN_EVENTS">"""

			if kmip_connection_fail_notify:
				if kmip_connection_fail_notify_text == "":
					kmip_connection_fail_notify_text = "Connection to the ([KMIP_Url]) key server has encountered an error on [Fail_Date]. This error occurred because [Fail_Reason]. You can check your settings with the [Account_Name] account."
			notify_data += """<notificationEvent enabledInThisNotifier="true" notificationRuleEventDBID="60" notificationText="%s" />""" % (kmip_connection_fail_notify_text)

			if dsm_connection_fail_notify:
				if dsm_connection_fail_notify_text == "":
					dsm_connection_fail_notify_text = "Connection to the Deep Security Manager ([DSM_Url]) has encountered an error on [Fail_Date]. This error occurred because [Fail_Reason]. You can check your settings with the [Account_Name] account."
				notify_data += """<notificationEvent enabledInThisNotifier="true" notificationRuleEventDBID="61" notificationText="%s" />""" % (dsm_connection_fail_notify_text)

			notify_data += "</eventGroup>"
			
		notify_data += "</eventGroups>"
		notify_data += "</notifier>"
		return notify_data


	def createNotifier(self, notify_name, desc, header, footer, frequencyUnit, frequencyValue, \
						from_email, subject, recipients_list, key_manual_approve_notify, key_manual_approve_notify_text, \
						key_auto_deny_notify, key_auto_deny_notify_text, key_auto_approve_notify, key_auto_approve_notify_text, \
						key_auto_approve_after_delay_notify, key_auto_approve_after_delay_notify_text, \
						kr_device_and_image_belong_diff_policy_notify, kr_device_and_image_belong_diff_policy_notify_text, \
						scim_fail_notify, scim_fail_notify_text, device_provision_notify, device_provision_notify_text, \
						provision_done_notify, provision_done_notify_text, provision_idle_notify, provision_idle_notify_text, provision_idle_time, \
						kmip_connection_fail_notify, kmip_connection_fail_notify_text, dsm_connection_fail_notify, dsm_connection_fail_notify_text):

		notify_data = self.create_notify_data("", notify_name, desc, header, footer, frequencyUnit, frequencyValue, \
						from_email, subject, recipients_list, key_manual_approve_notify, key_manual_approve_notify_text, \
						key_auto_deny_notify, key_auto_deny_notify_text, key_auto_approve_notify, key_auto_approve_notify_text, \
						key_auto_approve_after_delay_notify, key_auto_approve_after_delay_notify_text, \
						kr_device_and_image_belong_diff_policy_notify, kr_device_and_image_belong_diff_policy_notify_text, \
						scim_fail_notify, scim_fail_notify_text, device_provision_notify, device_provision_notify_text, \
						provision_done_notify, provision_done_notify_text, provision_idle_notify, provision_idle_notify_text, provision_idle_time, \
						kmip_connection_fail_notify, kmip_connection_fail_notify_text, dsm_connection_fail_notify, dsm_connection_fail_notify_text)
		result = self.broker_api.createNotifier(notify_data)
		if not result:
			return False
		self.log_xml(result, self.createNotifier.__name__)
		xmldata = xml.dom.minidom.parseString(result)
		return xmldata


	def updateNotifier(self, notify_id, notify_name, desc, header, footer, frequencyUnit, frequencyValue, \
						from_email, subject, recipients_list, key_manual_approve_notify, key_manual_approve_notify_text, \
						key_auto_deny_notify, key_auto_deny_notify_text, key_auto_approve_notify, key_auto_approve_notify_text, \
						key_auto_approve_after_delay_notify, key_auto_approve_after_delay_notify_text, \
						kr_device_and_image_belong_diff_policy_notify, kr_device_and_image_belong_diff_policy_notify_text, \
						scim_fail_notify, scim_fail_notify_text, device_provision_notify, device_provision_notify_text, \
						provision_done_notify, provision_done_notify_text, provision_idle_notify, provision_idle_notify_text, provision_idle_time, \
						kmip_connection_fail_notify, kmip_connection_fail_notify_text, dsm_connection_fail_notify, dsm_connection_fail_notify_text):

		notify_data = self.create_notify_data(notify_id, notify_name, desc, header, footer, frequencyUnit, frequencyValue, \
						from_email, subject, recipients_list, key_manual_approve_notify, key_manual_approve_notify_text, \
						key_auto_deny_notify, key_auto_deny_notify_text, key_auto_approve_notify, key_auto_approve_notify_text, \
						key_auto_approve_after_delay_notify, key_auto_approve_after_delay_notify_text, \
						kr_device_and_image_belong_diff_policy_notify, kr_device_and_image_belong_diff_policy_notify_text, \
						scim_fail_notify, scim_fail_notify_text, device_provision_notify, device_provision_notify_text, \
						provision_done_notify, provision_done_notify_text, provision_idle_notify, provision_idle_notify_text, provision_idle_time, \
						kmip_connection_fail_notify, kmip_connection_fail_notify_text, dsm_connection_fail_notify, dsm_connection_fail_notify_text)
		result = self.broker_api.updateNotifier(notify_id, notify_data)
		if not result:
			return False
		self.log_xml(result, self.updateNotifier.__name__)
		xmldata = xml.dom.minidom.parseString(result)
		return xmldata


	def deleteNotifier(self, notify_id):
		result = self.broker_api.deleteNotifier(notify_id)
		return result


	def get_notify_id_from_notify_name(self, notify_name):
		xml_result = self.listAllNotifiers()
		if not xml_result:
			logging.debug("call createNotifier return False")
			return False
		
		notify_list = xml_result.getElementsByTagName("notifierList")[0]
		notify_summaries = notify_list.getElementsByTagName("notifierSummary")
		for notify_summary in notify_summaries:
			if notify_name == notify_summary.attributes["name"].value.strip():
				return notify_summary.attributes["notificationRuleDBID"].value.strip()

		return ""



















if __name__ == '__main__':

	#listAllDevices()

	#get single device and update
	#device_id = "32dd93f4-d539-4c9a-a9e5-fd2c0fb8aa62"
	#getDevice(device_id)
	
	#f = open(XML_LOG_PATH+"getDevice_update.xml","r")
	#device_data = f.read()
	#updateDevice(device_id, device_data)


	#device_id = "629fa79b-8fde-48fa-b8f9-14b315aaf412"
	#deleteDevice(device_id)

	#device_id = "aae492bc-1aa8-4281-a880-1d5d2fc5e437"
	#encryptDevice(device_id)

	#device_id = "6d7865ff-3602-49ec-8e5d-951088673c60"
	#exportDevice(device_id, "this-is-passphrase")

	#listAllImages()

	#image_id = "6b46e0af-2da0-414f-87d0-169084348aaf"
	#getImage(image_id)

	#image_id = "6b46e0af-2da0-414f-87d0-169084348aaf"
	#f = open(XML_LOG_PATH+"getImage_update.xml","r")
	#image_data = f.read()
	#updateImage(image_id, image_data)

	#image_id = "6b46e0af-2da0-414f-87d0-169084348aaf"
	#deleteImage(image_id)

	#listAllProviders()

	#getProvider("Amazon-EC2")

	#listAllSecurityGroups()



	#listAllSecurityRules()
	
	#sr_id = "5d14057d-3277-4ab9-9d3e-e808acbb9c65"
	#getSecurityRule(sr_id)

	#getSecurityGroupSetting()

	# 7:50 on UI = 3:50
	#putSecurityGroupSetting(scheduleType="Daily",scheduleIntervalTime="7:50:00",scheduleIntervalPeriod="PM",scheduleIntervalDay="Sun",reAttemptInterval="30",reAttemptIntervalType="minutes",reAttemptICRepeat="100")


	

	#sg_id = "6123dce7-f7ef-4924-a9c8-d71d426fda58"
	#f = open(XML_LOG_PATH+"createSecurityGroup_update.xml","r")
	#sg_data = f.read()
	#updateSecurityGroup(sg_id, sg_data)



	#listCurrentUserAccounts()

	#userRights()

	#listAllRoles()

	#listAllUsers()

	#getCurrentUser()

	#user_id = "d8dada6e-3ba6-4209-98a0-3340ff8ce0cb"
	#getUser(user_id)

	#getCurrentAccount()

	account_id = "1FB18C52-2D33-4983-9704-7915133759A7"
	account_name="danny_shao@trend.com.tw"
	#new_user_id = createUser("auto_user@trend.com.tw", "localuser", "auto", "user", "auto_user@trend.com.tw", account_id, account_name, "Administrator")
	#print new_user_id

	#passphrase="P@ssw0rd"
	#updatePassphrase(account_id, new_passphrase=passphrase)

	#listTimezones()

	#new_timezone = "Taipei Standard Time"
	#new_dateFormat = "yyyy/MM/dd"
	#updateTimeInfo(account_id, new_timezone, new_dateFormat)


	#helper functions
	account_name = "danny_shao@trend.com.tw"
	user_name = "danny_shao@trend.com.tw"
	#print get_account_id_from_account_name(account_name)
	#print get_user_id_from_user_name(user_name)

	#listLanguages()

	"""
	x = mapi_lib(auth_type="api_auth", broker="danny", broker_passphrase="ClOuD9", realm="securecloud@trend.com", access_key_id="grVAP1k5xBE3xUhVt7tO", secret_access_key="c1yiaB6l2MqkNChb3oDv7xtN7qeCl8B6LVdi3hDT", api_account_id="250C5CF1-62B6-4CDD-91C6-58F0307FE75E", api_passphrase="P@ssw0rd")
	x.listAllDevices()
	"""

	# RAT case
	#realm = "securecloud@trend.com"
	#digest_broker_name = "danny"
	#digest_broker_pass = "ClOuD9"
	#header_broker_name = "danny"

	#x = mapi_lib(no_init=True)
	#print x.digest_authentication_test(realm, digest_broker_name, digest_broker_pass, header_broker_name)

	#x = mapi_lib()
	#print x.get_certificate()

	# -------------------------------------------------
	
	#vm 
	x = mapi_lib(auth_type="api_auth")
	x.listVM()

	#vm_guid = "6133b187-ab40-4a80-b1f1-3e794b272f9b"
	#x.readVM(vm_guid)

	EnableIC="true"
	ICAction="Revoke"
	PostponeEnable="false"
	RevokeIntervalNumber="2"
	RevokeIntervalType="Hour"
	policy_name="mapi_test"
	isResourcePool="false"
	description="this is mapi test"
	successAction="Approve"
	successActionDelay="15"
	failAction="ManualApprove"
	failActionDelay="15"
	device_id_list=[]
	image_id_list=["c336a574-0890-45dc-9435-94fae83a5597"]
	security_rule = "%s,%s,%s#%s" % ("Key Request Date", "MatchAll", "equalGreaterThan", "06/01/2012")
	security_rule_list=[security_rule]


	"""
	xml_result = x.createSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
					RevokeIntervalType, policy_name, isResourcePool, description, \
					successAction, successActionDelay, failAction, failActionDelay, \
					device_id_list,image_id_list, security_rule_list)
	"""

	sg_id = "9d010e91-f2e4-492a-b148-3cac5193c272"
	#x.getSecurityGroup(sg_id)

	sg_id = "89fd786b-aebc-4aa0-9f4f-30655d80fec9"
	#x.deleteSecurityGroup(sg_id)

	#x.runningVM()

	dkr_id = "bcb513fa-cecc-45dc-9f98-2071af3d8fc3"
	dkr_status = "approved"
	#x.updateDeviceKeyRequest(dkr_id, dkr_status)
	