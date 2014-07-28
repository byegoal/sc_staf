import sys
import time
import broker_api
import xml
import logging
import uuid
import mapi_util
import mapi_config

logging.basicConfig(level=mapi_config.log_level)

IS_LOGGING = mapi_config.mapi_lib_IS_LOGGING
LOG_TO_FILE = mapi_config.mapi_lib_LOG_TO_FILE
XML_LOG_PATH = mapi_config.mapi_lib_XML_LOG_PATH
LOG_PATH = mapi_config.mapi_lib_LOG_PATH
IS_SHOW = mapi_config.mapi_lib_IS_SHOW


class mapi_lib:

    def __init__(self, auth_type=None, broker=None, broker_passphrase=None, realm=None, access_key_id=None,
                 secret_access_key=None, api_account_id=None, api_passphrase=None):

        print "auth_type:%s, broker:%s, broker_passphrase:%s, realm:%s, access_key_id:%s, secret_access_key:%s, api_account_id:%s, api_passphrase:%s" \
            % (auth_type, broker, broker_passphrase, realm, access_key_id, secret_access_key, api_account_id, api_passphrase)
        self.broker_api = broker_api.broker_api(
            auth_type, broker, broker_passphrase, realm, access_key_id, secret_access_key, api_account_id, api_passphrase)
                # secret_access_key, api_account_id, api_passphrase, user_name, user_pass, no_init)

        # log setting
        # To-Do get logging from config and set

    def log_xml(self, result, log_name):
        if(IS_SHOW):
            print result
        if(LOG_TO_FILE):
            xml_obj = xml.dom.minidom.parseString(result)
            pretty_xml = xml_obj.toprettyxml()
            new_log_name = XML_LOG_PATH + log_name + "-formated.xml"
            # print log_name
            f = open(new_log_name, "w")
            f.write(pretty_xml)
            f.close()
            new_log_name2 = XML_LOG_PATH + log_name + ".xml"
            f2 = open(new_log_name2, "w")
            f2.write(result)
            f2.close()

    def listVM(self):
        result = self.broker_api.listVM()
        if not result:
            return False
        self.log_xml(result, self.listVM.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    def readVM(self, vm_guid):
        result = self.broker_api.readVM(vm_guid)
        if not result:
            return False
        self.log_xml(result, self.readVM.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    def deleteDeviceKey(self, vm_guid, device_guid):
        result = self.broker_api.deleteDeviceKey(vm_guid, device_guid)
        return result

    def deleteVM(self, vm_guid):
        result = self.broker_api.deleteVM(vm_guid)
        return result

    # inventory
    def cloneDevice(self, from_device_msuid, to_device_msuid):
        clone_data = """<device xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" version="1" msUID="%s" />""" % (
            to_device_msuid)
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
    def create_device_data(self, device_msuid, device_id, device_name, device_os, device_fs, write_permission,
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
        # device_data += """ deviceStatus="Encrypted" """

        device_data += ">"

        if device_desc is not None:
            if device_desc:
                device_data += """<description>%s</description>""" % (device_desc)
            else:
                device_data += """<description></description>"""

        # it's for resource pool
        # device_data += """<connections read="1" write="1" />"""

        if image_id is not None:
            device_data += """<image id="%s"></image>""" % (image_id)

        if device_mount_point is not None:
            device_data += """<volume><mountPoint>%s</mountPoint></volume>""" % (device_mount_point)

        # only keySize, mode can be updated
        # device_data += """<keyGen keySize="%s" cipher="des" mode="cfb" iv="plain" hash="sha-512" />""" % (device_key_size)
        device_data += """<keyGen keySize="%s" mode="%s" />""" % (device_key_size, key_mode)
        device_data += "</device>"

        return device_data

    def updateDevice(self, device_msuid, device_id, device_name, device_os, device_fs, write_permission, device_desc, device_mount_point, device_key_size, image_id, is_configure="true", key_mode="cbc"):
        device_data = self.create_device_data(
            device_msuid, device_id, device_name, device_os, device_fs, write_permission, device_desc,
            device_mount_point, device_key_size, image_id, is_configure, key_mode)
        result = self.broker_api.updateDevice(device_msuid, device_data)
        if not result:
            return False
        self.log_xml(result, self.updateDevice.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    def deleteDevice(self, device_id):
        result = self.broker_api.deleteDevice(device_id)
        return result

    def encryptDevice(self, device_id, provision_state="pending"):
        encrypt_data = """<device xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" version="1" msUID="%s" provisionState="%s" />""" % (
            device_id, provision_state)
        result = self.broker_api.encryptDevice(device_id, encrypt_data)
        if not result:
            return False
        self.log_xml(result, self.encryptDevice.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    # later, need security admin account
    def exportDevice(self, device_id, passphrase):
        device_data = """<?xml version="1.0" encoding="utf-8"?><string>%s</string>""" % (passphrase)
        result = self.broker_api.exportDevice(device_id, device_data)
        if not result:
            return False
        self.log_xml(result, self.exportDevice.__name__)
        # xmldata = xml.dom.minidom.parseString(result)
        # return xmldata

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
        image_data = """<?xml version="1.0" ?><image xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" version="1" msUID="%s" """ % (
            image_msuid)
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

    def listAllProviders(self):
        result = self.broker_api.listAllProviders()
        if not result:
            return False
        self.log_xml(result, self.listAllProviders.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    def getProvider(self, provider_id):
        result = self.broker_api.getProvider(provider_id)
        if not result:
            return False
        self.log_xml(result, self.getProvider.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    """ Sample
	<device
		xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
		xmlns:xsd="http://www.w3.org/2001/XMLSchema"
		version="1"
		msUID="2e80bb04-99eb-4e3e-9323-3bbec00fe776"
		id="test_raid1"
		name="test_raid1"
		type="1"
		raidLevel="RAID0"
		os="linux"
		fs="ext3"
		configured="true"
		writeaccess="true"
		providerLocation="test_zone2"
		detachable="false">
			<subDevices>
				<device msUID="f6070d9b-a676-41af-b21b-cd850b99e686" />
				<device msUID="f9ef31b9-43b1-4553-85a9-85103efffe2e" />
			</subDevices>
			<description>this is test raid 1</description>
			<provider name="test_csp2" />
			<image id="raid_image" />
			<volume size=""><mountPoint>/test_raid1</mountPoint></volume>
			<keyGen keySize="256" cipher="aes" mode="cbc" />
	</device>
	"""
    def create_raid_data(self, raid_msuid, raid_id, raid_name, raid_level, raid_os, raid_fs, write_permission, provider_zone,
                         device_id_list, raid_desc, provider, image_id, mount_point, key_size, is_configure, key_mode, is_detachable):
        raid_data = """<device xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" version="1" """

        if not raid_msuid:
            raid_data += """ msUID="%s" """ % (uuid.uuid4())
        else:
            raid_data += """ msUID="%s" """ % (raid_msuid)

        if raid_id is not None:
            raid_data += """ id="%s" """ % (raid_id)

        if raid_name is not None:
            raid_data += """ name="%s" """ % (raid_name)

        raid_data += """ cspDeviceType="RAID" """

        if raid_level is not None:
            raid_data += """ raidLevel="%s" """ % (raid_level)

        if raid_os is not None:
            raid_data += """ os="%s" """ % (raid_os)

        if raid_fs is not None:
            raid_data += """ fs="%s" """ % (raid_fs)

        if is_configure is not None:
            raid_data += """ configured="%s" """ % (is_configure)

        if write_permission is not None:
            raid_data += """ writeaccess="%s" """ % (write_permission)

        # if provider_zone is not None:
        #	raid_data += """ providerLocation="%s" """ % (provider_zone)

        raid_data += """ detachable="%s" """ % (is_detachable)

        raid_data += ">"

        if device_id_list is not None:
            raid_data += """<subDevices>"""
            for device_id in device_id_list:
                raid_data += """<device msUID="%s" />""" % (device_id)
            raid_data += """</subDevices>"""

        if raid_desc is not None:
            if raid_desc:
                raid_data += """<description>%s</description>""" % (raid_desc)
            else:
                raid_data += """<description />"""

        if provider is not None and provider_zone is not None:
            raid_data += """<provider name="%s" providerLocation="%s" />""" % (provider, provider_zone)

        if image_id is not None:
            raid_data += """<image id="%s" />""" % (image_id)

        if mount_point is not None:
            raid_data += """<volume><mountPoint>%s</mountPoint></volume>""" % (mount_point)

        if key_size is not None or key_mode is not None:
            raid_data += """<keyGen """

            if key_size is not None:
                raid_data += """ keySize="%s" """ % (key_size)

            if key_mode is not None:
                raid_data += """ mode="%s" """ % (key_mode)

            raid_data += """ />"""

        raid_data += """</device>"""

        return raid_data

    def createRAID(self, raid_msuid, raid_id, raid_name, raid_level, raid_os, raid_fs, write_permission, provider_zone, device_id_list, raid_desc, provider, image_id, mount_point, key_size, is_configure="true", key_mode="cbc", is_detachable="false"):
        raid_data = self.create_raid_data(
            raid_msuid, raid_id, raid_name, raid_level, raid_os, raid_fs, write_permission, provider_zone, device_id_list,
            raid_desc, provider, image_id, mount_point, key_size, is_configure, key_mode, is_detachable)
        result = self.broker_api.createRAID(raid_data)
        if not result:
            return False
        self.log_xml(result, self.createRAID.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    def readRAID(self, raid_id):
        result = self.broker_api.readRAID(raid_id)
        if not result:
            return False
        self.log_xml(result, self.readRAID.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    def updateRAID(self, raid_msuid, raid_id, raid_name, raid_level, raid_os, raid_fs, write_permission, provider_zone, device_id_list, raid_desc, provider, image_id, mount_point, key_size, is_configure="true", key_mode="cbc", is_detachable="false"):
        raid_data = self.create_raid_data(
            raid_msuid, raid_id, raid_name, raid_level, raid_os, raid_fs, write_permission, provider_zone, device_id_list,
            raid_desc, provider, image_id, mount_point, key_size, is_configure, key_mode, is_detachable)
        result = self.broker_api.updateRAID(raid_msuid, raid_data)
        if not result:
            return False
        self.log_xml(result, self.updateRAID.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    def deleteRAID(self, raid_msuid):
        result = self.broker_api.deleteRAID(raid_msuid)
        return result

    def encryptRAID(self, raid_msuid, provision_state="pending"):
        logging.debug("in " + self.encryptRAID.__name__)
        encrypt_data = """<device xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" version="1" msUID="%s" provisionState="%s" />""" % (
            raid_msuid, provision_state)
        logging.debug(encrypt_data)
        result = self.broker_api.encryptRAID(raid_msuid, encrypt_data)
        if not result:
            logging.debug("out " + self.encryptRAID.__name__)
            return False
        self.log_xml(result, self.encryptRAID.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        logging.debug("out " + self.encryptRAID.__name__)
        return xmldata

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

    # reference
    """
		policy_data = <?xml version="1.0" ?>
	<securityGroup
		id="25778531-f36c-4083-b797-b2ba7c93b2bd"
		EnableIC="true"
		ICAction="Revoke"
		PostponeEnable="true"
		RevokeIntervalNumber="1"
		RevokeIntervalType="Hour"
		name="test"
		isDeleteble="true"
		isNameEditable="true"
		isResourcePool="false"
		version="1"
		xmlns:xsd="http://www.w3.org/2001/XMLSchema"
		xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
		<description/>
		<successAction action="ManualApprove" autoDelay="30"/>
		<failedAction action="ManualApprove" autoDelay="-1"/>
		<deviceList>
			<device id="%s"></device>
		</deviceList>
		<imageList>
			<image id="%s"></image>
		</imageList>
		<securityRuleList>
			<securityRule dataMissing="Failed" description="" id="1338779b-2683-474b-a9a7-298176564a6f" matchType="MatchAll">
				<securityRuleType context="" dataType="Date" evaluator="lessThan" id="1338779b-2683-474b-a9a7-298176564a6f" name="Key Request Date"/>
				<securityRuleConditionList>
					<securityRuleCondition evaluator="equalGreaterThan" expectedValue="6/1/2012"/>
				</securityRuleConditionList>
			</securityRule>
		</securityRuleList>
	</securityGroup>
	"""
    # ICAction="Revoke" / "Nothing"
    # successAction= ManualApprove/Approve/Deny
    def create_policy_data(self, policy_id, EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber,
                           RevokeIntervalType, policy_name, isResourcePool, description,
                           successAction, successActionDelay, failAction, failActionDelay,
                           device_id_list, image_id_list, security_rule_list,
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
            policy_data += """ isNameEditable="%s" """ % (isNameEditable)

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

        if device_id_list:
            policy_data += """<deviceList>"""
            for device_id in device_id_list:
                policy_data += """<device id="%s"></device>""" % (device_id)
            policy_data += """</deviceList>"""

        if image_id_list:
            policy_data += """<imageList>"""
            for image_id in image_id_list:
                policy_data += """<image id="%s"></image>""" % (image_id)
            policy_data += """</imageList>"""

        if formatted_security_rule_list == None:
            security_rule_data = self.create_security_rule(security_rule_list)
        else:
            security_rule_data = formatted_security_rule_list
        policy_data += security_rule_data

        policy_data += "</securityGroup>"
        logging.error(policy_data)
        return policy_data

    def createSecurityGroup(self, EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber,
                            RevokeIntervalType, policy_name, isResourcePool, description,
                            successAction, successActionDelay, failAction, failActionDelay,
                            device_id_list, image_id_list, security_rule_list, formatted_security_rule_list=None):

        policy_data = self.create_policy_data("", EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber,
                                              RevokeIntervalType, policy_name, isResourcePool, description,
                                              successAction, successActionDelay, failAction, failActionDelay,
                                              device_id_list, image_id_list, security_rule_list, formatted_security_rule_list)
        result = self.broker_api.createSecurityGroup(policy_data)
        if not result:
            return False
        self.log_xml(result, self.createSecurityGroup.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    def updateSecurityGroup(self, policy_id, EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber,
                            RevokeIntervalType, policy_name, isResourcePool, description,
                            successAction, successActionDelay, failAction, failActionDelay,
                            device_id_list, image_id_list, security_rule_list, formatted_security_rule_list=None):

        policy_data = self.create_policy_data(policy_id, EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber,
                                              RevokeIntervalType, policy_name, isResourcePool, description,
                                              successAction, successActionDelay, failAction, failActionDelay,
                                              device_id_list, image_id_list, security_rule_list, formatted_security_rule_list)
        result = self.broker_api.updateSecurityGroup(policy_id, policy_data)
        if not result:
            return False
        self.log_xml(result, self.updateSecurityGroup.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    def deleteSecurityGroup(self, sg_id):
        result = self.broker_api.deleteSecurityGroup(sg_id)
        return result

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
		ReAttemptICRepeat="%s"/>""" % (scheduleType, scheduleIntervalTime, scheduleIntervalPeriod, scheduleIntervalDay, reAttemptInterval, reAttemptIntervalType, reAttemptICRepeat)
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

    # Instance
    def getDeviceKeyRequest(self, kr_id):
        result = self.broker_api.getDeviceKeyRequest(kr_id)
        if not result:
            return False
        self.log_xml(result, self.getDeviceKeyRequest.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    # reference
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
        # dkr_data += """<deviceKeyRequest id="%s" version="1" """ % (dkr_id)
        dkr_data += """<deviceKeyRequest version="1" """
        dkr_data += """ xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">"""

        dkr_data += """<deviceKeyRequestState>%s</deviceKeyRequestState>""" % (dkr_status)
        # dkr_data += """<mountPoint>%s</mountPoint>""" % (mount_point)

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

        # dkr_data += """<options hasKey="True"/>"""
        # dkr_data += """<linkList><link res="RuleEvaluations" /></linkList>"""
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

    # no more this API
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

        objWriteFile = open("C:\\Documents and Settings\\Administrator\\Desktop\\result.log", "a")
        objWriteFile.writelines(result + "\n")
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
        account_info = self.create_account_data(
            account_id, timezone=new_timezone, dateFormat=new_dateFormat, session_timeout=new_session_timeout)
        result = self.broker_api.updateAccountSettings(account_info)
        if not result:
            return False
        self.log_xml(result, self.updateAccountSettings.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    # tobe - update what?
    def updateCurrentUsersAccount(self, new_account_id):
        result = self.broker_api.updateCurrentUsersAccount(new_account_id, "")
        if not result:
            return False
        self.log_xml(result, self.updateCurrentUsersAccount.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    def updatePassphrase(self, account_id, new_passphrase):
        account_data = self.create_account_data(account_id, passphrase=new_passphrase)
        result = self.broker_api.updatePassphrase(account_data)
        if not result:
            return False
        self.log_xml(result, self.updatePassphrase.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    def userRights(self):
        result = self.broker_api.userRights()
        if not result:
            return False
        self.log_xml(result, self.userRights.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    def listAllRoles(self):
        result = self.broker_api.listAllRoles()
        if not result:
            return False
        self.log_xml(result, self.listAllRoles.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    def listAllUsers(self):
        result = self.broker_api.listAllUsers()
        if not result:
            return False
        self.log_xml(result, self.listAllUsers.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    def getCurrentUser(self):
        result = self.broker_api.getCurrentUser()
        if not result:
            return False
        self.log_xml(result, self.getCurrentUser.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    def getUser(self, user_id):
        result = self.broker_api.getUser(user_id)
        if not result:
            return False
        self.log_xml(result, self.getUser.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    """
	<?xml version="1.0" encoding="utf-8"?>
	<user
		xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
		xmlns:xsd="http://www.w3.org/2001/XMLSchema"
		loginname="api_user1@trend.com.tw"
		logintext="UEBzc3cwcmQ="
		usertype="localuser"
		authType="localuser"
		isLicensedUser="false">
		<contact>
			<firstName>api</firstName>
			<lastName>user1</lastName>
			<email>api_user1@trend.com.tw</email>
		</contact>
		<role name="Security Administrator" MFAStatus="false" />
	</user>
	"""
    def create_user_data(self, id, login_name, login_pass, user_type, first_name, last_name, email, user_role, mfa_status=None):

        user_data = """<?xml version="1.0" encoding="utf-8"?>
		<user
			xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
			xmlns:xsd="http://www.w3.org/2001/XMLSchema" """

        if id is not None:
            user_data += """ id="%s" """ % (id)

        if login_name is not None:
            user_data += """ loginname="%s" """ % (login_name)

        if login_pass is not None:
            user_data += """ logintext="%s" """ % (login_pass)

        if user_type is not None:
            user_data += """ usertype="%s" """ % (user_type)
            # user_data += """ authType="%s" """ % (user_type)

        user_data += ">"

        if first_name is not None or last_name is not None or email is not None:
            user_data += "<contact>"

            if first_name is not None:
                user_data += "<firstName>%s</firstName>" % (first_name)

            if last_name is not None:
                user_data += "<lastName>%s</lastName>" % (last_name)

            if email is not None:
                user_data += "<email>%s</email>" % (email)

            user_data += "</contact>"

        user_data += """ <role name="%s" """ % (user_role)
        if mfa_status is not None:
            user_data += """ MFAStatus="%s" """ % (mfa_status)
        user_data += "/>"

        user_data += """ </user>"""

        # user_data = """<user
        #	id="%s"
        #	isLicensedUser="false"
        #	loginname="%s"
        #	usertype="%s">
        #	<contact>
        #		<firstName>%s</firstName>
        #		<lastName>%s</lastName>
        #		<email>%s</email>
        #	</contact>
        #	<role name="%s" MFAStatus="%s" />
        #</user>""" % (id, login_name, user_type, first_name, last_name, email, user_role)

        return user_data

    def createUser(self, login_name, login_pass, user_type, first_name, last_name, email, user_role, mfa_status=None):
        user_data = self.create_user_data(
            "", login_name, login_pass, user_type, first_name, last_name, email, user_role, mfa_status)
        result = self.broker_api.createUser(user_data)
        if not result:
            return False
        self.log_xml(result, self.createUser.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    # when update, email, login_name, login_pass, user_type won't be changed
    def updateUser(self, user_id, first_name, last_name, user_role, email=None, login_name=None, login_pass=None, user_type=None, mfa_status=None):
        user_data = self.create_user_data(
            user_id, login_name, login_pass, user_type, first_name, last_name, email, user_role, mfa_status)
        result = self.broker_api.updateUser(user_id, user_data)
        if not result:
            return False
        self.log_xml(result, self.updateUser.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    def deleteUser(self, user_id):
        result = self.broker_api.deleteUser(user_id)
        return result

    def listTimezones(self):
        result = self.broker_api.listTimezones()
        if not result:
            return False
        self.log_xml(result, self.listTimezones.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    # no more this API
    """
	def readTimezone(time_zone_id):
		result = broker_api.readTimezone(time_zone_id)
		log_xml(result, readTimezone.__name__)
		xmldata = xml.dom.minidom.parseString(result)
		return xmldata
	"""

    def listLanguages(self):
        result = self.broker_api.listLanguages()
        if not result:
            return False
        self.log_xml(result, self.listLanguages.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    def getUserPreference(self):
        result = self.broker_api.getUserPreference()
        if not result:
            return False
        self.log_xml(result, self.getUserPreference.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    def create_user_pref(self, language_code):
        user_pref = """<userPreference languageCode="%s" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"/>""" % (language_code)
        return user_pref

    def updateUserPreference(self, language_code):
        user_pref = self.create_user_pref(language_code)
        result = self.broker_api.updateUserPreference(user_pref)
        if not result:
            return False
        self.log_xml(result, self.updateUserPreference.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    # tobe test
    def updateUserlogin(self, user_login, last_pass, new_pass):
        user_login_data = """<user xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
		xmlns:xsd="http://www.w3.org/2001/XMLSchema"
		logintext="%s"
		lastlogintext="%s"
		isLicensedUser="false" />""" % (new_pass, last_pass)

        result = self.broker_api.updateUserlogin(user_login, user_login_data)
        # to-do: how to check result

        if result == "":
            return True
        else:
            return False

    # tobe test
    def updateRolesMFAMode(self, user_id):
        create_mfa_data = self.create_mfa_data()
        result = self.broker_api.updateRolesMFAMode(user_id)
        if not result:
            return False
        self.log_xml(result, self.updateRolesMFAMode.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    # tobe test
    def unregisterUserMFADevice(self, user_id):
        result = self.broker_api.unregisterUserMFADevice(user_id)
        return result

    # Administration
    def readDSMConnSettings(self):
        result = self.broker_api.readDSMConnSettings()
        if not result:
            return False
        self.log_xml(result, self.readDSMConnSettings.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    # test again cuz when enable need to connect the test server
    def updateDSMConnSettings(self, dsm_enable, dsm_server, dsm_port, dsm_user, dsm_pass):
        dsm_data = """<?xml version="1.0" ?>
		<DSMConnSettings
			xmlns:xsd="http://www.w3.org/2001/XMLSchema"
			xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
			<Enabled>%s</Enabled>
			<ServerAddress>%s</ServerAddress>
			<Port>%s</Port>
			<Username>%s</Username>
			<Password>%s</Password>
		</DSMConnSettings>""" % (dsm_enable, dsm_server, dsm_port, dsm_user, dsm_pass)
        result = self.broker_api.updateDSMConnSettings(dsm_data)
        if not result:
            return False
        self.log_xml(result, self.updateDSMConnSettings.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    def getKmipConnectionSetting(self):
        result = self.broker_api.getKmipConnectionSetting()
        if not result:
            return False
        self.log_xml(result, self.getKmipConnectionSetting.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    # tobe test
    def setKmipConnectionSetting(self, kmip_data):
        kmip_data = """<?xml version="1.0" encoding="utf-8"?>
		<kmipConnectionSetting
			id="150"
			accountDBID="208"
			enabled="false"
			hostname=""
			port="9013"
			clientCertPassword=""
			active="true"
			doTestConnection="false"
			canModify="true">
			<clientCertificateFileName/><clientCertificate/>
			<clientPrivateKeyFileName/><clientPrivateKey/>
			<serverCertificateFileName/><serverCertificate/>
		</kmipConnectionSetting>"""
        result = self.broker_api.setKmipConnectionSetting(kmip_data)
        if not result:
            return False
        self.log_xml(result, self.setKmipConnectionSetting.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    # License
    def listLicenses(self):
        result = self.broker_api.listLicenses()
        if not result:
            return False
        self.log_xml(result, self.listLicenses.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    def getLicense(self, license_id):
        result = self.broker_api.getLicense(license_id)
        if not result:
            return False
        self.log_xml(result, self.getLicense.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    """<?xml version="1.0" ?>
		<license
			ac="SD-D5L6-3GZJ9-LV58P-CXGNB-MTYZV-KAQMD"
			account="1FB18C52-2D33-4983-9704-7915133759A7"
			activationDate="2012-06-07T07:16:50"
			expirationDate="2012-12-31T00:00:00"
			expireNotificationDate="2012-12-01T00:00:00"
			gracePeriod="720"
			id="373"
			inUse="40"
			isPRLicense="true"
			isTrial="false"
			lastUpdate="2012-06-07T07:16:50"
			seats="1000"
			updateInterval="720"
			verifyStatus="VALID">
				<LicenseProfile>
				AQEJHh5vFmxpHQAQYxYMb2IKGQIdFBgXDgMADBEbCxceCR4ebxZsaR0AEGMWDG9iChkCHRQYFw4DAAwRGwsXHgY7PU8hfi28vMQAsYgtpLY=
				</LicenseProfile>
		</license>"""
    def create_license_data(self, license_id, ac):
        license_data = """<?xml version="1.0" ?>
		<license
			id="%s"
			ac="%s">
		</license>""" % (license_id, ac)

        return license_data

    def create_license_data2(self):
        license_data = """<?xml version="1.0" ?>
		<license
			id="1"
			ac="SD-5TW9-53R6H-ESPNW-W5QVL-XDFZ4-ZWWZE">
		</license>"""

        return license_data

    def addLicense(self, ac):
        license_data = self.create_license_data("", ac)
        result = self.broker_api.addLicense(license_data)
        if not result:
            return False
        self.log_xml(result, self.addLicense.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    def updateLicense(self, license_id):
        license_data = self.create_license_data2()
        result = self.broker_api.updateLicense(license_id, license_data)
        if not result:
            return False
        self.log_xml(result, self.updateLicense.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    def updateLicenseOnline(self, license_id):
        result = self.broker_api.updateLicenseOnline(license_id)
        if not result:
            return False
        self.log_xml(result, self.updateLicense.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    # Log
    def listLogGroups(self):
        result = self.broker_api.listLogGroups()
        if not result:
            return False
        self.log_xml(result, self.listLogGroups.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    """
	<logQuery
		xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
		xmlns:xsd="http://www.w3.org/2001/XMLSchema"
		version="1"
		from="2012-06-01T01:58"
		to="2012-06-08T00:00">
		<logGroups>
			<logGroup code="AGENT_EVENTS" />
		</logGroups>
	</logQuery>
	"""
    """
	AGENT_EVENTS,SYSTEM_EVENTS,KEY_EVENTS,POLICY_EVENTS
	"""

    def create_log_data(self, from_time, to_time, log_type):
        log_data = """<logQuery
		xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
		xmlns:xsd="http://www.w3.org/2001/XMLSchema"
		version="1"
		from="%s"
		to="%s">
		<logGroups>
			<logGroup code="%s" />
		</logGroups>
	</logQuery>""" % (from_time, to_time, log_type)

        return log_data

    def queryLog(self, from_time, to_time, log_type):
        log_data = self.create_log_data(from_time, to_time, log_type)
        result = self.broker_api.queryLog(log_data)
        if not result:
            return False
        self.log_xml(result, self.queryLog.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    def exportLogQuery(self, from_time, to_time, log_type):
        log_data = self.create_log_data(from_time, to_time, log_type)
        result = self.broker_api.exportLogQuery(log_data)
        if not result:
            return False
        self.log_xml(result, self.exportLogQuery.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    def listLogArchives(self):
        result = self.broker_api.listLogArchives()
        if not result:
            return False
        self.log_xml(result, self.listLogArchives.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    def getLogArchive(self, log_id):
        result = self.broker_api.getLogArchive(log_id)
        if not result:
            return False
        self.log_xml(result, self.getLogArchive.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    def deleteLog(self, log_id):
        result = self.broker_api.deleteLog(log_id)
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
		xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">""" % (notify_id, notify_name, desc, header, footer, frequencyUnit, frequencyValue, from_email, subject)

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
                notify_data += """<notificationEvent enabledInThisNotifier="true" notificationRuleEventDBID="32" notificationText="%s" />""" % (
                    key_manual_approve_notify_text)

            if key_auto_deny_notify:
                if key_auto_deny_notify_text == "":
                    key_auto_deny_notify_text = "SecureCloud has automatically denied your key request for device, [Dev_Name]."
                notify_data += """<notificationEvent enabledInThisNotifier="true" notificationRuleEventDBID="33" notificationText="%s" />""" % (
                    key_auto_deny_notify_text)

            if key_auto_approve_notify:
                if key_auto_approve_notify_text == "":
                    key_auto_approve_notify_text = "SecureCloud has automatically approved your key request for device, [Dev_Name]."
                notify_data += """<notificationEvent enabledInThisNotifier="true" notificationRuleEventDBID="34" notificationText="%s" />""" % (
                    key_auto_approve_notify_text)

            if key_auto_approve_after_delay_notify:
                if key_auto_approve_after_delay_notify_text == "":
                    key_auto_approve_after_delay_notify_text = "SecureCloud has automatically approved your key request for device, [Dev_Name] after no action was taken."
                notify_data += """<notificationEvent enabledInThisNotifier="true" notificationRuleEventDBID="35" notificationText="%s" />""" % (
                    key_auto_approve_after_delay_notify_text)

            if kr_device_and_image_belong_diff_policy_notify:
                if kr_device_and_image_belong_diff_policy_notify_text == "":
                    kr_device_and_image_belong_diff_policy_notify_text = "SecureCloud has received a key request for a device ([Dev_Name]) that is not a member of the same policy as the machine image."
                notify_data += """<notificationEvent enabledInThisNotifier="true" notificationRuleEventDBID="38" notificationText="%s" />""" % (
                    kr_device_and_image_belong_diff_policy_notify_text)

            if scim_fail_notify:
                if scim_fail_notify_text == "":
                    scim_fail_notify_text = "Instance [Inst_ID] is no longer in compliance with the policy rules as of [Check_Date]."
                notify_data += """<notificationEvent enabledInThisNotifier="true" notificationRuleEventDBID="43" notificationText="%s" />""" % (
                    scim_fail_notify_text)

            notify_data += "</eventGroup>"

        if device_provision_notify or provision_done_notify or provision_idle_notify:
            notify_data += """<eventGroup eventGroupCode="PROVISION_EVENTS">"""

            if device_provision_notify:
                if device_provision_notify_text == "":
                    device_provision_notify_text = "Device, [Dev_Name] has encountered an error during the encryption process on [Err_Date]"
                notify_data += """<notificationEvent enabledInThisNotifier="true" notificationRuleEventDBID="57" notificationText="%s" />""" % (
                    device_provision_notify_text)

            if provision_done_notify:
                if provision_done_notify_text == "":
                    provision_done_notify_text = "Device, [Dev_Name] is encrypted successfully and is ready for use as of [Complete_Date]"
                notify_data += """<notificationEvent enabledInThisNotifier="true" notificationRuleEventDBID="58" notificationText="%s" />""" % (
                    provision_done_notify_text)

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
            notify_data += """<notificationEvent enabledInThisNotifier="true" notificationRuleEventDBID="60" notificationText="%s" />""" % (
                kmip_connection_fail_notify_text)

            if dsm_connection_fail_notify:
                if dsm_connection_fail_notify_text == "":
                    dsm_connection_fail_notify_text = "Connection to the Deep Security Manager ([DSM_Url]) has encountered an error on [Fail_Date]. This error occurred because [Fail_Reason]. You can check your settings with the [Account_Name] account."
                notify_data += """<notificationEvent enabledInThisNotifier="true" notificationRuleEventDBID="61" notificationText="%s" />""" % (
                    dsm_connection_fail_notify_text)

            notify_data += "</eventGroup>"

        notify_data += "</eventGroups>"
        notify_data += "</notifier>"
        return notify_data

    def createNotifier(self, notify_name, desc, header, footer, frequencyUnit, frequencyValue,
                       from_email, subject, recipients_list, key_manual_approve_notify, key_manual_approve_notify_text,
                       key_auto_deny_notify, key_auto_deny_notify_text, key_auto_approve_notify, key_auto_approve_notify_text,
                       key_auto_approve_after_delay_notify, key_auto_approve_after_delay_notify_text,
                       kr_device_and_image_belong_diff_policy_notify, kr_device_and_image_belong_diff_policy_notify_text,
                       scim_fail_notify, scim_fail_notify_text, device_provision_notify, device_provision_notify_text,
                       provision_done_notify, provision_done_notify_text, provision_idle_notify, provision_idle_notify_text, provision_idle_time,
                       kmip_connection_fail_notify, kmip_connection_fail_notify_text, dsm_connection_fail_notify, dsm_connection_fail_notify_text):

        notify_data = self.create_notify_data("", notify_name, desc, header, footer, frequencyUnit, frequencyValue,
                                              from_email, subject, recipients_list, key_manual_approve_notify, key_manual_approve_notify_text,
                                              key_auto_deny_notify, key_auto_deny_notify_text, key_auto_approve_notify, key_auto_approve_notify_text,
                                              key_auto_approve_after_delay_notify, key_auto_approve_after_delay_notify_text,
                                              kr_device_and_image_belong_diff_policy_notify, kr_device_and_image_belong_diff_policy_notify_text,
                                              scim_fail_notify, scim_fail_notify_text, device_provision_notify, device_provision_notify_text,
                                        provision_done_notify, provision_done_notify_text, provision_idle_notify, provision_idle_notify_text, provision_idle_time,
                                        kmip_connection_fail_notify, kmip_connection_fail_notify_text, dsm_connection_fail_notify, dsm_connection_fail_notify_text)
        result = self.broker_api.createNotifier(notify_data)
        if not result:
            return False
        self.log_xml(result, self.createNotifier.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    def updateNotifier(self, notify_id, notify_name, desc, header, footer, frequencyUnit, frequencyValue,
                                            from_email, subject, recipients_list, key_manual_approve_notify, key_manual_approve_notify_text,
                                            key_auto_deny_notify, key_auto_deny_notify_text, key_auto_approve_notify, key_auto_approve_notify_text,
                                            key_auto_approve_after_delay_notify, key_auto_approve_after_delay_notify_text,
                                            kr_device_and_image_belong_diff_policy_notify, kr_device_and_image_belong_diff_policy_notify_text,
                                            scim_fail_notify, scim_fail_notify_text, device_provision_notify, device_provision_notify_text,
                                            provision_done_notify, provision_done_notify_text, provision_idle_notify, provision_idle_notify_text, provision_idle_time,
                                            kmip_connection_fail_notify, kmip_connection_fail_notify_text, dsm_connection_fail_notify, dsm_connection_fail_notify_text):

        notify_data = self.create_notify_data(notify_id, notify_name, desc, header, footer, frequencyUnit, frequencyValue,
                                        from_email, subject, recipients_list, key_manual_approve_notify, key_manual_approve_notify_text,
                                        key_auto_deny_notify, key_auto_deny_notify_text, key_auto_approve_notify, key_auto_approve_notify_text,
                                        key_auto_approve_after_delay_notify, key_auto_approve_after_delay_notify_text,
                                        kr_device_and_image_belong_diff_policy_notify, kr_device_and_image_belong_diff_policy_notify_text,
                                        scim_fail_notify, scim_fail_notify_text, device_provision_notify, device_provision_notify_text,
                                        provision_done_notify, provision_done_notify_text, provision_idle_notify, provision_idle_notify_text, provision_idle_time,
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

    def getTemplateList(self, report_type):
        result = self.broker_api.getTemplateList(report_type)
        if not result:
            return False
        self.log_xml(result, self.getTemplateList.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    def loadTemplate(self, template_id):
        result = self.broker_api.loadTemplate(template_id)
        if not result:
            return False
        self.log_xml(result, self.loadTemplate.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    """
	Reference
	<ReportSchedule
		Name="createTemplate_test"
		Description="this is createTemplate test"
		MaintenanceInDays="15"
		ReportCode="0"
		SaveReport="true"
		Enabled="true"
		xmlns:xsd="http://www.w3.org/2001/XMLSchema"
		xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
		<Format PDF="true" XLS="true"/>
		<RequiredSections>
		<SectionNo>1</SectionNo>
		<SectionNo>2</SectionNo>
		<SectionNo>3</SectionNo>
		<SectionNo>4</SectionNo>
		<SectionNo>5</SectionNo>
		<SectionNo>6</SectionNo>
		<SectionNo>7</SectionNo>
		<SectionNo>8</SectionNo>
		<SectionNo>9</SectionNo>
		<SectionNo>10</SectionNo>
		<SectionNo>11//SectionNo>
		</RequiredSections>
		<Schedule>
				<Frequency>OneTime</Frequency>
				<DateTimeDuration EndDateTime="0" StartDateTime="0"/>
				<StartTime></StartTime>
				<StartDay></StartDay>
				<StartDate></StartDate>
		</Schedule>
		<Recipients EmailAddress="danny_shao@trend.com.tw" Enabled="true"/>
	</ReportSchedule>
	"""
    def create_template_data(self, name, desc, maintenance_days, has_pdf, has_xls,
                                                    num_key_approve, num_key_deny, num_key_request, interval_btn_kr_and_approve,
                                                    num_instance, num_image, num_device, console_audit, policy_audit,
                                                    kr_audit, instance_compute_time, frequency, start_datetime, end_datetime,
                                                    start_time, start_day, start_date, recipient_list, enable_email):
        template_data = """<?xml version="1.0" ?>
	<ReportSchedule
		Name="%s"
		Description="%s"
		MaintenanceInDays="%s"
		ReportCode="0"
		xmlns:xsd="http://www.w3.org/2001/XMLSchema"
		xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
		<Format PDF="%s" XLS="%s"/>""" % (name, desc, maintenance_days, has_pdf, has_xls)

        template_data += "<RequiredSections>"

        if num_key_approve:
            template_data += "<SectionNo>1</SectionNo>"

        if num_key_deny:
            template_data += "<SectionNo>2</SectionNo>"

        if num_key_request:
            template_data += "<SectionNo>3</SectionNo>"

        if interval_btn_kr_and_approve:
            template_data += "<SectionNo>4</SectionNo>"

        if num_instance:
            template_data += "<SectionNo>5</SectionNo>"

        if num_image:
            template_data += "<SectionNo>6</SectionNo>"

        if num_device:
            template_data += "<SectionNo>7</SectionNo>"

        if console_audit:
            template_data += "<SectionNo>8</SectionNo>"

        if policy_audit:
            template_data += "<SectionNo>9</SectionNo>"

        if kr_audit:
            template_data += "<SectionNo>10</SectionNo>"

        if instance_compute_time:
            template_data += "<SectionNo>11</SectionNo>"

        template_data += "</RequiredSections>"

        if not start_datetime:
            start_datetime = 0
        if not end_datetime:
            end_datetime = 0
        if not start_time:
            start_time = 0
        if not start_day:
            start_day = 0
        if not start_date:
            start_date = 0
        template_data += """<Schedule>
			<Frequency>%s</Frequency>
			<DateTimeDuration EndDateTime="%s" StartDateTime="%s"/>
			<StartTime>%s</StartTime>
			<StartDay>%s</StartDay>
			<StartDate>%s</StartDate>
		</Schedule>""" % (frequency, end_datetime, start_datetime, start_time, start_day, start_date)
        template_data += """<Recipients EmailAddress="%s" Enabled="%s"/>""" % (recipient_list, enable_email)
        template_data += "</ReportSchedule>"

        return template_data

    def createTemplate(self, name, desc, maintenance_days, has_pdf, has_xls,
                                                    num_key_approve, num_key_deny, num_key_request, interval_btn_kr_and_approve,
                                                    num_instance, num_image, num_device, console_audit, policy_audit,
                                                    kr_audit, instance_compute_time, frequency, start_datetime, end_datetime,
                                                    start_time, start_day, start_date, recipient_list, enable_email):

        template_data = self.create_template_data(name, desc, maintenance_days, has_pdf, has_xls,
                                                num_key_approve, num_key_deny, num_key_request, interval_btn_kr_and_approve,
                                                num_instance, num_image, num_device, console_audit, policy_audit,
                                                kr_audit, instance_compute_time, frequency, start_datetime, end_datetime,
                                                start_time, start_day, start_date, recipient_list, enable_email)

        result = self.broker_api.createTemplate(template_data)
        if not result:
            return False
        self.log_xml(result, self.createTemplate.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    def updateTemplate(self, template_id, name, desc, maintenance_days, has_pdf, has_xls,
                                                    num_key_approve, num_key_deny, num_key_request, interval_btn_kr_and_approve,
                                                    num_instance, num_image, num_device, console_audit, policy_audit,
                                                    kr_audit, instance_compute_time, frequency, start_datetime, end_datetime,
                                                    start_time, start_day, start_date, recipient_list, enable_email):

        template_data = self.create_template_data(name, desc, maintenance_days, has_pdf, has_xls,
                                                num_key_approve, num_key_deny, num_key_request, interval_btn_kr_and_approve,
                                                num_instance, num_image, num_device, console_audit, policy_audit,
                                                kr_audit, instance_compute_time, frequency, start_datetime, end_datetime,
                                                start_time, start_day, start_date, recipient_list, enable_email)
        result = self.broker_api.updateTemplate(template_id, template_data)
        if not result:
            return False
        self.log_xml(result, self.updateTemplate.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    def deleteTemplate(self, template_id):
        result = self.broker_api.deleteTemplate(template_id)
        return result

    # tobe test
    def generateReport(self, name, desc, maintenance_days, has_pdf, has_xls,
                                                    num_key_approve, num_key_deny, num_key_request, interval_btn_kr_and_approve,
                                                    num_instance, num_image, num_device, console_audit, policy_audit,
                                                    kr_audit, instance_compute_time, frequency, start_datetime, end_datetime,
                                                    start_time, start_day, start_date, recipient_list, enable_email):

        template_data = self.create_template_data(name, desc, maintenance_days, has_pdf, has_xls,
                                                num_key_approve, num_key_deny, num_key_request, interval_btn_kr_and_approve,
                                                num_instance, num_image, num_device, console_audit, policy_audit,
                                                kr_audit, instance_compute_time, frequency, start_datetime, end_datetime,
                                                start_time, start_day, start_date, recipient_list, enable_email)
        result = self.broker_api.generateReport(template_data)
        if not result:
            return False
        self.log_xml(result, self.generateReport.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    # report archive
    def getReportList(self, report_type):
        result = self.broker_api.getReportList(report_type)
        if not result:
            return False
        self.log_xml(result, self.getReportList.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    def getReport(self, report_id):
        result = self.broker_api.getReport(report_id)
        if not result:
            return False
        self.log_xml(result, self.getReport.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    def deleteReport(self, report_id):
        result = self.broker_api.deleteReport(report_id)
        return result

    def exportReport(self, report_data):
        result = self.broker_api.exportReport(report_data)
        if not result:
            return False
        self.log_xml(result, self.getReport.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    # server status
    def getServerData(self):
        result = self.broker_api.getServerData()
        if not result:
            return False
        self.log_xml(result, self.getServerData.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    def serviceStatus(self):
        result = self.broker_api.serviceStatus()
        if not result:
            return False
        self.log_xml(result, self.serviceStatus.__name__)
        xmldata = xml.dom.minidom.parseString(result)
        return xmldata

    def getEntryPoint(self):
        result = self.broker_api.getEntryPoint()
        if not result:
            return False
        self.log_xml(result, self.getEntryPoint.__name__)
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

    def get_template_id_from_template_name(self, template_name):
        xml_result = self.getTemplateList("A")
        if not xml_result:
            logging.debug("call getTemplateList return False")
            return False

        job_list = xml_result.getElementsByTagName("ScheduledJobs")[0]
        jobs = job_list.getElementsByTagName("ScheduledJob")
        for job in jobs:
            if template_name == job.attributes["Name"].value.strip():
                return job.attributes["JobGUID"].value.strip()

        return ""

    def get_report_id_from_report_name(self, report_name):
        xml_result = self.getReportList("A")
        if not xml_result:
            logging.debug("call getReportList return False")
            return False

        report_list = xml_result.getElementsByTagName("ArchivedReports")[0]
        reports = report_list.getElementsByTagName("ArchivedReport")
        for report in reports:
            if report_name == report.attributes["Name"].value.strip():
                return report.attributes["ReportGUID"].value.strip()

        return ""

    def get_license_id_from_ac(self, ac):
        xml_result = self.listLicenses()
        if not xml_result:
            logging.debug("call getReportList return False")
            return False

        license_list = xml_result.getElementsByTagName("licenseList")[0]
        licenses = license_list.getElementsByTagName("license")
        for license in licenses:
            if ac == license.attributes["ac"].value.strip():
                return license.attributes["id"].value.strip()

        return ""

    def compare_user(self, login_name, first_name, last_name, email, user_role, current_user):
        """<user
                id="%s"
                isLicensedUser="false"
                loginname="%s"
                usertype="%s">
                <contact>
                        <firstName>%s</firstName>
                        <lastName>%s</lastName>
                        <email>%s</email>
                </contact>
                <role name="%s"/>
        </user>"""

        if login_name:
            if login_name != current_user.attributes["loginname"].value.strip():
                logging.debug("login name not match")
                return False

        contact_node = current_user.getElementsByTagName("contact")[0]

        if first_name:
            first_name_node = contact_node.getElementsByTagName("firstName")[0]
            current_first_name = mapi_util.getText(first_name_node)
            if first_name != current_first_name:
                logging.debug("first name not match")
                logging.debug("current first name:%s" % (current_first_name))
                return False

        if last_name:
            last_name_node = contact_node.getElementsByTagName("lastName")[0]
            current_last_name = mapi_util.getText(last_name_node)
            if last_name != current_last_name:
                logging.debug("last name not match")
                logging.debug("current last name:%s" % (current_last_name))
                return False

        if email:
            email_node = contact_node.getElementsByTagName("email")[0]
            current_email = mapi_util.getText(email_node)
            if email != current_email:
                logging.debug("email not match")
                logging.debug("current email:%s" % (current_email))
                return False

        if user_role:
            role_node = current_user.getElementsByTagName("role")[0]
            current_role = role_node.attributes["name"].value.strip()
            if user_role != current_role:
                logging.debug("role not match")
                logging.debug("current role:%s" % (current_role))
                return False

        return True

    def compare_device(self, device_name, device_os, device_fs, write_permission, device_desc, device_mount_point, device_key_size, image_id, current_device):

        """ Sample
        <device
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

        if device_name:
            if device_name != current_device.attributes["name"].value.strip():
                logging.debug("device name not match")
                return False

        if device_os:
            if device_os != current_device.attributes["os"].value.strip():
                logging.debug("device os not match")
                return False

        if device_fs:
            if device_fs != current_device.attributes["fs"].value.strip():
                logging.debug("device fs not match")
                return False

        if write_permission:
            if write_permission != current_device.attributes["writeaccess"].value.strip():
                logging.debug("write permission not match")
                return False

        volume_node = current_device.getElementsByTagName("volume")[0]
        mount_point_node = volume_node.getElementsByTagName("mountPoint")[0]

        if device_mount_point:
            current_mount_point = mapi_util.getText(mount_point_node)
            if device_mount_point != current_mount_point:
                logging.debug("mount point not match")
                logging.debug("current mount point:%s" % (current_mount_point))
                return False

        desc_node = current_device.getElementsByTagName("description")[0]
        if device_desc:
            current_desc = mapi_util.getText(desc_node)
            if device_desc != current_desc:
                logging.debug("desc not match")
                logging.debug("current desc:%s" % (current_desc))
                return False

        key_node = current_device.getElementsByTagName("keyGen")[0]
        if device_key_size:
            current_key_size = key_node.attributes["keySize"].value.strip()
            if device_key_size != current_key_size:
                logging.debug("key size not match")
                logging.debug("current key size:%s" % (current_key_size))
                return False

        return True

    def compare_raid(self, raid_id, raid_name, raid_level, raid_os, raid_fs, write_permission, provider_zone, device_msuid_list, raid_desc, provider, image_id, mount_point, key_size, current_device):
        """ Sample
        <device
                msUID="2e80bb04-99eb-4e3e-9323-3bbec00fe776"
                id="test_raid1"
                name="test_raid1"
                type="1"
                raidLevel="RAID0"
                os="linux"
                fs="ext3"
                configured="true"
                writeaccess="true"
                providerLocation="test_zone2"
                detachable="false">
                        <subDevices>
                                <device msUID="f6070d9b-a676-41af-b21b-cd850b99e686" />
                                <device msUID="f9ef31b9-43b1-4553-85a9-85103efffe2e" />
                        </subDevices>
                        <description>this is test raid 1</description>
                        <provider name="test_csp2" />
                        <image id="raid_image" />
                        <volume size=""><mountPoint>/test_raid1</mountPoint></volume>
                        <keyGen keySize="256" cipher="aes" mode="cbc" />
        </device>
        """

        if raid_id:
            if raid_id != current_device.attributes["id"].value.strip():
                logging.debug("raid id not match")
                return False

        if raid_name:
            if raid_name != current_device.attributes["name"].value.strip():
                logging.debug("raid name not match")
                return False

        if raid_level:
            if raid_level != current_device.attributes["raidLevel"].value.strip():
                logging.debug("raid level not match")
                return False

        if raid_os:
            if raid_os != current_device.attributes["os"].value.strip():
                logging.debug("raid os not match")
                return False

        if raid_fs:
            if raid_fs != current_device.attributes["fs"].value.strip():
                logging.debug("raid fs not match")
                return False

        if write_permission:
            if write_permission != current_device.attributes["writeaccess"].value.strip():
                logging.debug("write permission not match")
                return False

        if provider_zone:
            if provider_zone != current_device.attributes["providerLocation"].value.strip():
                logging.debug("provider not match")
                return False

        sub_device_list = current_device.getElementsByTagName("subDevices")[0]
        sub_devices = sub_device_list.getElementsByTagName("device")
        for sub_device in sub_devices:
            current_device_msuid = sub_device.attributes["msUID"].value.strip()
            # print current_device_msuid
            found_device = False
            for device_id in device_msuid_list:
                if device_id == current_device_msuid:
                    found_device = True

            if found_device == False:
                logging.error("no such device")
                return False

        # to-do : don't know why cannot get the mount point
        raid_desc_node = current_device.getElementsByTagName("description")[0]
        current_raid_desc = mapi_util.getText(raid_desc_node)
        if raid_desc:
            if current_raid_desc != raid_desc:
                logging.error("desc is not the same")
                logging.error("current desc:%s", current_raid_desc)
                # return False

        raid_provider_node = current_device.getElementsByTagName("provider")[0]
        current_provider = raid_provider_node.attributes["name"].value.strip()
        if provider:
            if current_provider != provider:
                logging.error("provider is not the same")
                logging.error("current provider:%s", current_provider)
                # return False

        current_image_id_node = current_device.getElementsByTagName("image")[0]
        current_image_id = current_image_id_node.attributes["id"].value.strip()
        if image_id:
            if current_image_id != image_id:
                logging.error("image id is not the same")
                logging.error("current image:%s", current_image_id)
                # return False

        # to-do : don't know why cannot get the mount point
        volume_node = current_device.getElementsByTagName("volume")[0]
        mount_point_node = volume_node.getElementsByTagName("mountPoint")[0]
        current_mount_point = mapi_util.getText(mount_point_node)
        if mount_point:
            if current_mount_point != mount_point:
                logging.error("mount point is not the same")
                logging.error("current mount point:%s", current_mount_point)
                # return False

        key_node = current_device.getElementsByTagName("keyGen")[0]
        current_key_size = key_node.attributes["keySize"].value.strip()
        if key_size:
            if current_key_size != key_size:
                logging.error("key size is not the same")
                logging.error("current key size:%s", current_key_size)
                # return False

        return True

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

    """
		policy_data = <?xml version="1.0" ?>
	<securityGroup
		id="25778531-f36c-4083-b797-b2ba7c93b2bd"
		EnableIC="true"
		ICAction="Revoke"
		PostponeEnable="true"
		RevokeIntervalNumber="1"
		RevokeIntervalType="Hour"
		name="test"
		isDeleteble="true"
		isNameEditable="true"
		isResourcePool="false"
		version="1"
		xmlns:xsd="http://www.w3.org/2001/XMLSchema"
		xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
		<description/>
		<successAction action="ManualApprove" autoDelay="30"/>
		<failedAction action="ManualApprove" autoDelay="-1"/>
		<deviceList>
			<device id="%s"></device>
		</deviceList>
		<imageList>
			<image id="%s"></image>
		</imageList>
		<securityRuleList>
			<securityRule dataMissing="Failed" description="" id="1338779b-2683-474b-a9a7-298176564a6f" matchType="MatchAll">
				<securityRuleType context="" dataType="Date" evaluator="lessThan" id="1338779b-2683-474b-a9a7-298176564a6f" name="Key Request Date"/>
				<securityRuleConditionList>
					<securityRuleCondition evaluator="equalGreaterThan" expectedValue="6/1/2012"/>
				</securityRuleConditionList>
			</securityRule>
		</securityRuleList>
	</securityGroup>
	"""
    def compare_policy(self, EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber,
                                            RevokeIntervalType, policy_name, isResourcePool, description,
                                            successAction, successActionDelay, failAction, failActionDelay,
                                            device_id_list, image_id_list, security_rule_list, current_policy, formatted_security_rule_list=None):

        if EnableIC:
            if EnableIC != current_policy.attributes["EnableIC"].value.strip():
                self.broker_api_lib.debug("EnableID not match")
                return False

        if ICAction:
            if ICAction != current_policy.attributes["ICAction"].value.strip():
                self.broker_api_lib.debug("ICAction not match")
                return False

        if PostponeEnable:
            if PostponeEnable != current_policy.attributes["PostponeEnable"].value.strip():
                self.broker_api_lib.debug("PostponeEnable not match")
                return False

        if RevokeIntervalNumber:
            if RevokeIntervalNumber != current_policy.attributes["RevokeIntervalNumber"].value.strip():
                self.broker_api_lib.debug("RevokeIntervalNumber not match")
                return False

        if RevokeIntervalType:
            if RevokeIntervalType != current_policy.attributes["RevokeIntervalType"].value.strip():
                self.broker_api_lib.debug("RevokeIntervalType not match")
                return False

        if policy_name:
            if policy_name != current_policy.attributes["name"].value.strip():
                self.broker_api_lib.debug("policy_name not match")
                return False

        if isResourcePool:
            if isResourcePool != current_policy.attributes["isResourcePool"].value.strip():
                self.broker_api_lib.debug("isResourcePool not match")
                return False

        if description:
            desc_node = current_policy.getElementsByTagName("description")[0]
            current_desc = mapi_util.getText(desc_node)
            if description != current_desc:
                self.broker_api_lib.debug("description not match")
                return False

        success_node = current_policy.getElementsByTagName("successAction")[0]
        if successAction:
            if successAction != success_node.attributes["action"].value.strip():
                self.broker_api_lib.debug("successAction not match")
                return False

        if successActionDelay:
            if successActionDelay != success_node.attributes["autoDelay"].value.strip():
                self.broker_api_lib.debug("successActionDelay not match")
                return False

        fail_node = current_policy.getElementsByTagName("failedAction")[0]
        if failAction:
            if failAction != fail_node.attributes["action"].value.strip():
                self.broker_api_lib.debug("failAction not match")
                return False

        if failActionDelay:
            if failActionDelay != fail_node.attributes["autoDelay"].value.strip():
                self.broker_api_lib.debug("failActionDelay not match")
                return False

        device_list_node = current_policy.getElementsByTagName("deviceList")[0]
        devices_node = device_list_node.getElementsByTagName("device")
        for device_id in device_id_list:
            is_found = False
            for device_node in devices_node:
                if device_id == device_node.attributes["id"].value.strip():
                    is_found = True

            if not is_found:
                self.broker_api_lib.debug("device id:%s is not found" % (device_id))
                return False

        image_list_node = current_policy.getElementsByTagName("imageList")[0]
        images_node = image_list_node.getElementsByTagName("image")
        for image_id in image_id_list:
            is_found = False
            for image_node in images_node:
                if image_id == image_node.attributes["id"].value.strip():
                    is_found = True

            if not is_found:
                broker_api_lib.debug("image id:%s is not found" % (image_id))
                return False

        sr_list_node = current_policy.getElementsByTagName("securityRuleList")[0]
        sr_nodes = current_policy.getElementsByTagName("securityRule")

        if formatted_security_rule_list is None:
            import mapi_config
            for security_rule_str in security_rule_list:
                tokens = security_rule_str.split(",")

                rule_name = tokens[0]
                match_type = tokens[1]
                condition_list = tokens[2]
                condition_list = condition_list.split("$")

                rule_id = mapi_config.rule_mapping[rule_name]

                found_sr = False
                for sr_node in sr_nodes:
                    if rule_id == sr_node.attributes["id"].value.strip() and \
                    match_type == sr_node.attributes["matchType"].value.strip():
                        found_sr = True
                        sr_con_list_node = sr_node.getElementsByTagName("securityRuleConditionList")[0]
                        sr_con_nodes = sr_con_list_node.getElementsByTagName("securityRuleCondition")

                        found_sr_condition = False
                        for condition in condition_list:
                            condition_token = condition.split("#")
                            evaluator = condition_token[0]
                            expected_value = condition_token[1]

                            for sr_con_node in sr_con_nodes:
                                if evaluator == sr_con_node.attributes["evaluator"].value.strip() and \
                                expected_value == sr_con_node.attributes["expectedValue"].value.strip():
                                    found_sr_condition = True

                if not found_sr and not found_sr_condition:
                    self.broker_api_lib.debug("security rule not match")
                    return False
        else:
            # To-Do compare formatted string here
            pass

        return True

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
	"""
    def compare_notify(self, notify_name, desc, header, footer, frequencyUnit, frequencyValue,
                                            from_email, subject, recipients_list, key_manual_approve_notify, key_manual_approve_notify_text,
                                            key_auto_deny_notify, key_auto_deny_notify_text, key_auto_approve_notify, key_auto_approve_notify_text,
                                            key_auto_approve_after_delay_notify, key_auto_approve_after_delay_notify_text,
                                            kr_device_and_image_belong_diff_policy_notify, kr_device_and_image_belong_diff_policy_notify_text,
                                            scim_fail_notify, scim_fail_notify_text, device_provision_notify, device_provision_notify_text,
                                            provision_done_notify, provision_done_notify_text, provision_idle_notify, provision_idle_notify_text, provision_idle_time,
                                            kmip_connection_fail_notify, kmip_connection_fail_notify_text, dsm_connection_fail_notify, dsm_connection_fail_notify_text, current_notify):

        if notify_name:
            if notify_name != current_notify.attributes["name"].value.strip():
                self.broker_api_lib.debug("notify_name not match")
                return False

        if desc:
            if desc != current_notify.attributes["description"].value.strip():
                self.broker_api_lib.debug("description not match")
                return False

        if header:
            if header != current_notify.attributes["header"].value.strip():
                self.broker_api_lib.debug("header not match")
                return False

        if footer:
            if footer != current_notify.attributes["footer"].value.strip():
                self.broker_api_lib.debug("footer not match")
                return False

        if frequencyUnit:
            if frequencyUnit != current_notify.attributes["frequencyUnit"].value.strip():
                self.broker_api_lib.debug("frequencyUnit not match")
                return False

        if frequencyValue:
            if frequencyValue != current_notify.attributes["frequencyValue"].value.strip():
                self.broker_api_lib.debug("frequencyValue not match")
                return False

        if subject:
            if subject != current_notify.attributes["subject"].value.strip():
                self.broker_api_lib.debug("subject not match")
                return False

        if recipients_list:
            found_recipient = False
            for recipient in recipients_list:
                recipients_node = current_notify.getElementsByTagName("recipients")[0]
                notificationRecipient_nodes = recipients_node.getElementsByTagName("notificationRecipient")
                for notificationRecipient_node in notificationRecipient_nodes:
                    if recipient == notificationRecipient_node.attributes["emailAddress"].value.strip():
                        found_recipient = True

            if not found_recipient:
                self.broker_api_lib.debug("recipient is not found")
                return False

        eventGroups_node = current_notify.getElementsByTagName("eventGroups")[0]
        eventGroup_nodes = eventGroups_node.getElementsByTagName("eventGroup")

        for eventGroup_node in eventGroup_nodes:
            notificationEvent_nodes = eventGroup_node.getElementsByTagName("notificationEvent")
            for notificationEvent_node in notificationEvent_nodes:
                if notificationEvent_node.attributes["notificationRuleEventDBID"].value.strip() == "32" and \
                key_manual_approve_notify != "True" and \
                key_manual_approve_notify_text != notificationEvent_node.attributes["notificationText"].value.strip():
                    self.broker_api_lib.debug("key_manual_approve_notify is not updated")
                    return False

                if notificationEvent_node.attributes["notificationRuleEventDBID"].value.strip() == "33" and \
                key_auto_deny_notify != "True" and \
                key_auto_deny_notify_text != notificationEvent_node.attributes["notificationText"].value.strip():
                    self.broker_api_lib.debug("key_auto_deny_notify is not updated")
                    return False

                if notificationEvent_node.attributes["notificationRuleEventDBID"].value.strip() == "34" and \
                key_auto_approve_notify != "True" and \
                key_auto_approve_notify_text != notificationEvent_node.attributes["notificationText"].value.strip():
                    self.broker_api_lib.debug("key_auto_approve_notify is not updated")
                    return False

                if notificationEvent_node.attributes["notificationRuleEventDBID"].value.strip() == "35" and \
                key_auto_approve_after_delay_notify != "True" and \
                key_auto_approve_after_delay_notify_text != notificationEvent_node.attributes["notificationText"].value.strip():
                    self.broker_api_lib.debug("key_auto_approve_after_delay_notify is not updated")
                    return False

                if notificationEvent_node.attributes["notificationRuleEventDBID"].value.strip() == "38" and \
                kr_device_and_image_belong_diff_policy_notify != "True" and \
                kr_device_and_image_belong_diff_policy_notify_text != notificationEvent_node.attributes["notificationText"].value.strip():
                    self.broker_api_lib.debug("kr_device_and_image_belong_diff_policy_notify is not updated")
                    return False

                if notificationEvent_node.attributes["notificationRuleEventDBID"].value.strip() == "43" and \
                scim_fail_notify != "True" and \
                scim_fail_notify_text != notificationEvent_node.attributes["notificationText"].value.strip():
                    self.broker_api_lib.debug("scim_fail_notify is not updated")
                    return False

                if notificationEvent_node.attributes["notificationRuleEventDBID"].value.strip() == "57" and \
                device_provision_notify != "True" and \
                device_provision_notify_text != notificationEvent_node.attributes["notificationText"].value.strip():
                    self.broker_api_lib.debug("device_provision_notify is not updated")
                    return False

                if notificationEvent_node.attributes["notificationRuleEventDBID"].value.strip() == "58" and \
                provision_done_notify != "True" and \
                provision_done_notify_text != notificationEvent_node.attributes["notificationText"].value.strip():
                    self.broker_api_lib.debug("provision_done_notify is not updated")
                    return False

                if notificationEvent_node.attributes["notificationRuleEventDBID"].value.strip() == "59":
                    userConfigItems_node = notificationEvent_node.getElementsByTagName("userConfigItems")[0]
                    userConfig_node = userConfigItems_node.getElementsByTagName("userConfig")[0]
                    config_value = userConfig_node.attributes["configValue"].value.strip()

                    if provision_idle_notify != "True" and config_value != provision_idle_time and \
                    provision_idle_notify_text != notificationEvent_node.attributes["notificationText"].value.strip():
                        self.broker_api_lib.debug("provision_idle_notify is not updated")
                        return False

                if notificationEvent_node.attributes["notificationRuleEventDBID"].value.strip() == "60" and \
                kmip_connection_fail_notify != "True" and \
                kmip_connection_fail_notify_text != notificationEvent_node.attributes["notificationText"].value.strip():
                    self.broker_api_lib.debug("kmip_connection_fail_notify is not updated")
                    return False

                if notificationEvent_node.attributes["notificationRuleEventDBID"].value.strip() == "61" and \
                dsm_connection_fail_notify != "True" and \
                dsm_connection_fail_notify_text != notificationEvent_node.attributes["notificationText"].value.strip():
                    self.broker_api_lib.debug("dsm_connection_fail_notify is not updated")
                    return False

        return True

    """
	Reference
	<ReportSchedule
		Name="createTemplate_test"
		Description="this is createTemplate test"
		MaintenanceInDays="15"
		ReportCode="0"
		xmlns:xsd="http://www.w3.org/2001/XMLSchema"
		xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
		<Format PDF="true" XLS="true"/>
		<RequiredSections>
			<SectionNo>1</SectionNo>
			<SectionNo>2</SectionNo>
			<SectionNo>3</SectionNo>
			<SectionNo>4</SectionNo>
			<SectionNo>5</SectionNo>
			<SectionNo>6</SectionNo>
			<SectionNo>7</SectionNo>
			<SectionNo>8</SectionNo>
			<SectionNo>9</SectionNo>
			<SectionNo>10</SectionNo>
			<SectionNo>11</SectionNo>
		</RequiredSections>
		<Schedule>
			<Frequency>OneTime</Frequency>
			<DateTimeDuration EndDateTime="0" StartDateTime="0"/>
			<StartTime></StartTime>
			<StartDay></StartDay>
			<StartDate></StartDate>
		</Schedule>
		<Recipients EmailAddress="danny_shao@trend.com.tw" Enabled="true"/>
	</ReportSchedule>
	"""
    def compare_report(self, name, desc, maintenance_days, has_pdf, has_xls,
                                                    num_key_approve, num_key_deny, num_key_request, interval_btn_kr_and_approve,
                                                    num_instance, num_image, num_device, console_audit, policy_audit,
                                                    kr_audit, instance_compute_time, frequency, start_datetime, end_datetime,
                                                    start_time, start_day, start_date, recipient_list, enable_email, current_report):

        if name != current_report.attributes["Name"].value.strip():
            self.broker_api_lib.debug("name not match")
            return False

        if desc != current_report.attributes["Description"].value.strip():
            self.broker_api_lib.debug("desc not match")
            return False

        if maintenance_days != current_report.attributes["MaintenanceInDays"].value.strip():
            self.broker_api_lib.debug("maintenance_days not match")
            return False

        format_node = current_report.getElementsByTagName("Format")[0]
        if has_pdf != format_node.attributes["PDF"].value.strip():
            self.broker_api_lib.debug("has_pdf not match")
            return False

        if has_xls != format_node.attributes["XLS"].value.strip():
            self.broker_api_lib.debug("has_xls not match")
            return False

        require_section_node = current_report.getElementsByTagName("RequiredSections")[0]
        section_nodes = require_section_node.getElementsByTagName("SectionNo")
        for section_node in section_nodes:
            current_num = mapi_util.getText(section_node)
            if current_num == "1" and not num_key_approve:
                self.broker_api_lib.debug("num_key_approve should be checked")
                return False
            elif current_num == "2" and not num_key_deny:
                self.broker_api_lib.debug("num_key_deny should be checked")
                return False
            elif current_num == "3" and not num_key_request:
                self.broker_api_lib.debug("num_key_request should be checked")
                return False
            elif current_num == "4" and not interval_btn_kr_and_approve:
                self.broker_api_lib.debug("interval_btn_kr_and_approve should be checked")
                return False
            elif current_num == "5" and not num_instance:
                self.broker_api_lib.debug("num_instance should be checked")
                return False
            elif current_num == "6" and not num_image:
                self.broker_api_lib.debug("num_image should be checked")
                return False
            elif current_num == "7" and not num_device:
                self.broker_api_lib.debug("num_device should be checked")
                return False
            elif current_num == "8" and not console_audit:
                self.broker_api_lib.debug("console_audit should be checked")
                return False
            elif current_num == "9" and not policy_audit:
                self.broker_api_lib.debug("policy_audit should be checked")
                return False
            elif current_num == "10" and not kr_audit:
                self.broker_api_lib.debug("kr_audit should be checked")
                return False
            elif current_num == "11" and not instance_compute_time:
                self.broker_api_lib.debug("instance_compute_time should be checked")
                return False

        schedule_node = current_report.getElementsByTagName("Schedule")[0]
        frequency_node = schedule_node.getElementsByTagName("Frequency")[0]
        current_frequency = mapi_util.getText(frequency_node)

        duration_node = schedule_node.getElementsByTagName("DateTimeDuration")[0]
        current_startdatetime = duration_node.attributes["StartDateTime"].value.strip()
        current_enddatetime = duration_node.attributes["EndDateTime"].value.strip()

        starttime_node = schedule_node.getElementsByTagName("StartTime")[0]
        current_starttime = mapi_util.getText(starttime_node)

        startday_node = schedule_node.getElementsByTagName("StartDay")[0]
        current_startday = mapi_util.getText(startday_node)

        startdate_node = schedule_node.getElementsByTagName("StartDate")[0]
        current_startdate = mapi_util.getText(startdate_node)

        if frequency == current_frequency:
            if frequency == "OneTime":
                if current_startdatetime != start_datetime and current_enddatetime != start_datetime:
                    self.broker_api_lib.debug("startdatetime, endtdatetime not match")
                    return False

            if frequency == "Daily":
                if current_starttime != start_time:
                    self.broker_api_lib.debug("start_time not match")
                    return False

            if frequency == "Weekly":
                if current_startday != start_day:
                    self.broker_api_lib.debug("start_day not match")
                    return False

            if frequency == "Monthly":
                if current_startdate != start_date:
                    self.broker_api_lib.debug("start_date not match")
                    return False
        else:
            self.broker_api_lib.debug("frequency not match")
            return False

        recipient_node = current_report.getElementsByTagName("Recipients")[0]
        if recipient_list != recipient_node.attributes["EmailAddress"].value.strip():
            self.broker_api_lib.debug("EmailAddress not match")
            return False

        if enable_email != recipient_node.attributes["Enabled"].value.strip():
            self.broker_api_lib.debug("enable_email not match")
            return False

        return True

    def compare_account_setting(self, timezone, date_format, session_timeout, current_account_setting):
        if timezone:
            current_timezone = current_account_setting.attributes["timezoneID"].value.strip()
            if timezone != current_timezone:
                logging.error("timezone not match")
                return False

        if date_format:
            current_date_format = current_account_setting.attributes["dateFormat"].value.strip()
            if date_format != current_date_format:
                logging.error("date format not match")
                return False

        if session_timeout:
            current_session_timeout = current_account_setting.attributes["sessionTimeout"].value.strip()
            if session_timeout != current_session_timeout:
                logging.error("session timeout not match")
                return False

        return True

    # Validation functions
    def validate_SecurityGroupSetting(self, sg_setting):
        try:
            current_scheduleType = sg_setting.attributes["ScheduleType"].value.strip()
            if not current_scheduleType:
                logging.error("no ScheduleType")
                return False

            current_scheduleIntervalTime = sg_setting.attributes["ScheduleIntervalTime"].value.strip()
            if not current_scheduleIntervalTime:
                logging.error("no ScheduleIntervalTime")
                return False

            current_scheduleIntervalPeriod = sg_setting.attributes["ScheduleIntervalPeriod"].value.strip()
            if not current_scheduleIntervalPeriod:
                logging.error("no ScheduleIntervalPeriod")
                return False

            current_scheduleIntervalDay = sg_setting.attributes["ScheduleIntervalDay"].value.strip()
            if not current_scheduleIntervalDay:
                logging.error("no ScheduleIntervalDay")
                return False

            current_reAttemptInterval = sg_setting.attributes["ReAttemptInterval"].value.strip()
            if not current_reAttemptInterval:
                logging.error("no ReAttemptInterval")
                return False

            current_reAttemptIntervalType = sg_setting.attributes["ReAttemptIntervalType"].value.strip()
            if not current_reAttemptIntervalType:
                logging.error("no ReAttemptIntervalType")
                return False

            current_reAttemptICRepeat = sg_setting.attributes["ReAttemptICRepeat"].value.strip()
            if not current_reAttemptICRepeat:
                logging.error("no ReAttemptIntervalType")
                return False

            return True
        except Exception, err:
            sys.stderr.write("ERROR: %s is attribute or child element missing\n" % str(err))
            return False

    """
<imageList version="1" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
	<image
		encryptSwap="false"
		href="https://mapi_server.securecloud.com:8443/Broker/API.svc/image/8a5ae71c-b1f8-4894-89ee-0258357c84db/"
		id="exportDevice_image"
		lastModified="2012-08-16T10:22:39.747"
		msUID="8a5ae71c-b1f8-4894-89ee-0258357c84db"
		name="exportDevice_image">
		<description/>
		<provider href="https://mapi_server.securecloud.com:8443/Broker/API.svc/provider/exportdevice_csp/" name="exportDevice_csp"/>
	</image>
	"""

    def validate_image(self, image, full_validate=False):
        try:
            current_encryptSwap = image.attributes["encryptSwap"].value.strip()
            if not current_encryptSwap:
                logging.error("no encryptSwap")
                return False

            current_href = image.attributes["href"].value.strip()
            if not current_href:
                logging.error("no href")
                return False

            current_id = image.attributes["id"].value.strip()
            if not current_id:
                logging.error("no id")
                return False

            current_lastModified = image.attributes["lastModified"].value.strip()
            if not current_lastModified:
                logging.error("no lastModified")
                return False

            current_msUID = image.attributes["msUID"].value.strip()
            if not current_msUID:
                logging.error("no msUID")
                return False

            current_name = image.attributes["name"].value.strip()
            if not current_name:
                logging.error("no name")
                return False

            desc_node = image.getElementsByTagName("description")[0]

            if full_validate:
                platform_node = image.getElementsByTagName("platform")
                # platform_node = image.getElementsByTagName("platform")[0]
                """
				current_platform = mapi_util.getText(platform_node)
				if not current_platform:
					logging.error("no platform")
				"""

            provider_node = image.getElementsByTagName("provider")[0]
            result = self.validate_provider(provider_node)
            if not result:
                logging.error("validate provider failed")
                return False

            return True
        except Exception, err:
            sys.stderr.write("ERROR: %s is attribute or child element missing\n" % str(err))
            return False

    def validate_provider(self, provider):
        try:
            current_href = provider.attributes["href"].value.strip()
            if not current_href:
                logging.error("no href")
                return False

            current_name = provider.attributes["name"].value.strip()
            if not current_name:
                logging.error("no name")
                return False

            return True
        except Exception, err:
            sys.stderr.write("ERROR: %s is attribute or child element missing\n" % str(err))
            return False

    """
	<device
		detachable="false"
		deviceStatus="Configured"
		href="https://mapi_server.securecloud.com:8443/Broker/API.svc/device/df962b08-9d8e-4bb6-a3d1-86f94508ac7f/"
		id="updateRAID_device1"
		info=""
		lastModified="2012-08-08T07:34:34.723"
		msUID="df962b08-9d8e-4bb6-a3d1-86f94508ac7f"
		name="updateRAID_device1"
		parentId="updateRAID_id_new"
		partitionNumber="-1"
		providerLocation="updateRAID_zone"
		provisionState=""
		type="0"
		writeaccess="false">
		<description/>
		<volume size="1G">
			<mountPoint/>
		</volume>
		<provider href="https://mapi_server.securecloud.com:8443/Broker/API.svc/provider/updateraid_csp/" name="updateRAID_csp"/>
		<image
			encryptSwap="false"
			href="https://mapi_server.securecloud.com:8443/Broker/API.svc/image/e7be90cc-7377-44b9-8f65-3c5f73fbaaab/"
			id="updateRAID_image"
			lastModified="2012-08-08T07:34:34.723"
			msUID="e7be90cc-7377-44b9-8f65-3c5f73fbaaab"
			name="updateRAID_image">
			<description/>
			<provider href="https://mapi_server.securecloud.com:8443/Broker/API.svc/provider/updateraid_csp/" name="updateRAID_csp"/>
		</image>
		<imageCandidates>
			<imageList>
				<image
					encryptSwap="false"
					href="https://mapi_server.securecloud.com:8443/Broker/API.svc/image/424ce706-d750-45c2-83e6-d669142593d6/"
					id="getDevice_image"
					lastModified="2012-08-21T09:18:05.153" msUID="424ce706-d750-45c2-83e6-d669142593d6" name="getDevice_image">
					<description/>
					<provider href="https://mapi_server.securecloud.com:8443/Broker/API.svc/provider/getdevice_csp/" name="getDevice_csp"/>
				</image>
			</imageList>
		</imageCandidates>
		<keyGen cipher="aes" keySize="256" mode="cbc"/>
	</device>
	"""
    def validate_device(self, device, full_validate=False):
        try:
            current_detachable = device.attributes["detachable"].value.strip()
            if not current_detachable:
                logging.error("no detachable")
                return False

            current_deviceStatus = device.attributes["deviceStatus"].value.strip()
            if not current_deviceStatus:
                logging.error("no deviceStatus")
                return False

            current_href = device.attributes["href"].value.strip()
            if not current_href:
                logging.error("no href")
                return False

            current_id = device.attributes["id"].value.strip()
            if not current_id:
                logging.error("no id")
                return False

            current_info = device.attributes["info"].value.strip()

            current_lastModified = device.attributes["lastModified"].value.strip()
            if not current_lastModified:
                logging.error("no lastModified")
                return False

            current_msUID = device.attributes["msUID"].value.strip()
            if not current_msUID:
                logging.error("no msUID")
                return False

            current_name = device.attributes["name"].value.strip()
            if not current_name:
                logging.error("no name")
                return False

            current_partitionNumber = device.attributes["partitionNumber"].value.strip()
            if not current_partitionNumber:
                logging.error("no partitionNumber")
                return False

            current_providerLocation = device.attributes["providerLocation"].value.strip()
            if not current_providerLocation:
                logging.error("no providerLocation")
                return False

            current_provisionState = device.attributes["provisionState"].value.strip()

            current_type = device.attributes["type"].value.strip()
            if not current_type:
                logging.error("no type")
                return False

            current_writeaccess = device.attributes["writeaccess"].value.strip()
            if not current_writeaccess:
                logging.error("no writeaccess")
                return False

            desc_node = device.getElementsByTagName("description")[0]

            volume_node = device.getElementsByTagName("volume")[0]
            if volume_node:
                volume_size = volume_node.attributes["size"].value.strip()
                # To-Do: can be null volume size
                """
				if not volume_size:
					logging.error("no volume size")
					return False
				"""

                mount_nodes = device.getElementsByTagName("mountPoint")
                if mount_nodes:
                    mount_node = mount_nodes[0]

            provider_node = device.getElementsByTagName("provider")[0]
            result = self.validate_provider(provider_node)
            if not result:
                logging.error("validate provider failed")
                return False

            image_node = device.getElementsByTagName("image")[0]
            result = self.validate_image(image_node)
            if not result:
                logging.error("validate image failed")
                return False

            imageCandidates_node = device.getElementsByTagName("imageCandidates")
            if imageCandidates_node:
                imageCandidates_node = imageCandidates_node[0]
                imageList_node = imageCandidates_node.getElementsByTagName("imageList")

                if imageList_node:
                    imageList_node = imageList_node[0]
                    image_nodes = imageList_node.getElementsByTagName("image")
                    for image_node in image_nodes:
                        result = self.validate_image(image_node)
                        if not result:
                            logging.error("validate candidate image failed")
                            return False

            # validate instance later
            key_nodes = device.getElementsByTagName("keyGen")
            if key_nodes:
                key_node = key_nodes[0]
                key_cipher = key_node.attributes["cipher"].value.strip()
                if not key_cipher:
                    logging.error("no cipher")
                    return False

                key_cipher = key_node.attributes["keySize"].value.strip()
                if not key_cipher:
                    logging.error("no keySize")
                    return False

                key_mode = key_node.attributes["mode"].value.strip()
                if not key_mode:
                    logging.error("no mode")
                    return False

            return True
        except Exception, err:
            sys.stderr.write("ERROR: %s is attribute or child element missing\n" % str(err))
            return False


if __name__ == '__main__':

    # listAllDevices()

    # get single device and update
    # device_id = "32dd93f4-d539-4c9a-a9e5-fd2c0fb8aa62"
    # getDevice(device_id)

    # f = open(XML_LOG_PATH+"getDevice_update.xml","r")
    # device_data = f.read()
    # updateDevice(device_id, device_data)

    # device_id = "629fa79b-8fde-48fa-b8f9-14b315aaf412"
    # deleteDevice(device_id)
    # device_id = "aae492bc-1aa8-4281-a880-1d5d2fc5e437"
    # encryptDevice(device_id)
    # device_id = "6d7865ff-3602-49ec-8e5d-951088673c60"
    # exportDevice(device_id, "this-is-passphrase")
    # listAllImages()
    # image_id = "6b46e0af-2da0-414f-87d0-169084348aaf"
    # getImage(image_id)
    # image_id = "6b46e0af-2da0-414f-87d0-169084348aaf"
    # f = open(XML_LOG_PATH+"getImage_update.xml","r")
    # image_data = f.read()
    # updateImage(image_id, image_data)
    # image_id = "6b46e0af-2da0-414f-87d0-169084348aaf"
    # deleteImage(image_id)
    # listAllProviders()
    # getProvider("Amazon-EC2")
    # listAllSecurityGroups()
    # sg_id = "dd57b1c0-0a70-4201-9063-13a8da40ccae"
    # getSecurityGroup(sg_id)
    # listAllSecurityRules()
    # sr_id = "5d14057d-3277-4ab9-9d3e-e808acbb9c65"
    # getSecurityRule(sr_id)
    # getSecurityGroupSetting()
    # 7:50 on UI = 3:50
    # putSecurityGroupSetting(scheduleType="Daily",scheduleIntervalTime="7:50:00",scheduleIntervalPeriod="PM",scheduleIntervalDay="Sun",reAttemptInterval="30",reAttemptIntervalType="minutes",reAttemptICRepeat="100")
    security_rules = [{'id': "d6f008eb-a11b-4cb6-8cb0-63c056d27009",
                                       'matchType': "MatchAll",
                                       "condition_list": [{"evaluator": "equal", "expectedValue": "fd96:7568:9882:16:11c0:4d8b:c109:8000"}]
                                       }]
    # createSecurityGroup("MAPI_test", "test_csp5_image1", "test_csp5_device1", security_rules)

    # sg_id = "6123dce7-f7ef-4924-a9c8-d71d426fda58"
    # f = open(XML_LOG_PATH+"createSecurityGroup_update.xml","r")
    # sg_data = f.read()
    # updateSecurityGroup(sg_id, sg_data)
    # sg_id = "6123dce7-f7ef-4924-a9c8-d71d426fda58"
    # deleteSecurityGroup(sg_id)
    # listCurrentUserAccounts()
    # userRights()
    # listAllRoles()
    # listAllUsers()
    # getCurrentUser()
    # user_id = "d8dada6e-3ba6-4209-98a0-3340ff8ce0cb"
    # getUser(user_id)
    # getCurrentAccount()
    account_id = "1FB18C52-2D33-4983-9704-7915133759A7"
    account_name = "danny_shao@trend.com.tw"
    # new_user_id = createUser("auto_user@trend.com.tw", "localuser", "auto", "user", "auto_user@trend.com.tw", account_id, account_name, "Administrator")
    # print new_user_id

    # passphrase="P@ssw0rd"
    # updatePassphrase(account_id, new_passphrase=passphrase)

    # listTimezones()

    # new_timezone = "Taipei Standard Time"
    # new_dateFormat = "yyyy/MM/dd"
    # updateTimeInfo(account_id, new_timezone, new_dateFormat)

    # dsm_enable = "true"
    # dsm_server = "172.18.0.240"
    # dsm_port = "4119"
    # dsm_user = "masteradmin"
    # dsm_pass = "Trend@123"
    # updateDSMConnSettings(dsm_enable,dsm_server,dsm_port,dsm_user,dsm_pass)

    # readDSMConnSettings()

    # getKmipConnectionSetting()

    # listLicenses()

    # getLicense("372")

    # listLogGroups()

    # listLogArchives()

    # listAllNotifiers()

    # notify_id="1027"
    # getNotificationEvents(notify_id)

    # notify_name = "api test2"
    # result = createNotifier(notify_name)

    # notify_id = "1028"
    # notify_name = "api test4"
    # updateNotifier(notify_id, notify_name)

    # notify_id = "1028"
    # print deleteNotifier(notify_id)

    # getTemplateList("A")

    # getReportList("A")

    # archive_report_id = "12d9d267-e4ce-41f8-bbd8-84f067437a80"
    # deleteReport(archive_report_id)

    template_id   = "b755f15e-4b5b-429f-98e9-56b1019f84d0"
    # loadTemplate(template_id)

    template_name = "api create test2"
    template_desc = "this is api create test2"
    # createTemplate(template_name, template_desc)

    template_id   = "f6b2c235-0fe7-48b3-b1f4-6db5e99e4fde"
    template_name = "api create test update"
    template_desc = "this is api create test update"
    # updateTemplate(template_id, template_name, template_desc)

    template_id   = "8cc002d5-2b07-4ab2-b9aa-50a82e3c9dec"
    # deleteTemplate(template_id)

    template_name = "api create test2"
    template_desc = "this is api create test2"
    # generateReport(template_name, template_desc)

    # helper functions
    account_name  = "danny_shao@trend.com.tw"
    user_name     = "danny_shao@trend.com.tw"
    # print get_account_id_from_account_name(account_name)
    # print get_user_id_from_user_name(user_name)

    # listLanguages()


    x = mapi_lib(
        auth_type          = "api_auth",
        broker             = "bobby",
        broker_passphrase  = "v5RWh0Lj5j",
        realm              = "securecloud@trend.com",
        access_key_id      = "53bXWuLfc0BeyQCNqNMF",
        secret_access_key  = "babu4cqZfaECQt8TpuL5369ASIZJ7c15PTVt88xr",
        api_account_id     = "7FB9CDFC-1542-4AAF-AFC1-247F59819E28",
        api_passphrase     = "P@ssw0rd",
        )
    x.listVM()


    # RAT case
    # realm = "securecloud@trend.com"
    # digest_broker_name = "danny"
    # digest_broker_pass = "ClOuD9"
    # header_broker_name = "danny"

    # x = mapi_lib(no_init=True)
    # print x.digest_authentication_test(realm, digest_broker_name, digest_broker_pass, header_broker_name)

    # x = mapi_lib()
    # print x.get_certificate()

    # vm
    #x = mapi_lib(auth_type="api_auth")
    #x.listVM()

    #x = mapi_lib(auth_type="api_auth")
    #vm_guid = "6133b187-ab40-4a80-b1f1-3e794b272f9b"
    #x.readVM(vm_guid)
