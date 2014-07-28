import time
import mapi_lib
import logging
import mapi_util
import sys
import simulator_lib
import base64
import xml

#from xml.etree.ElementTree import ElementTree
import xml.etree.cElementTree as etree
from cStringIO import StringIO



"""
To-do
Not done:
exportDevice?
updateRAID - when comparing, cannot get the description and mount point
cloneDevice - proper way to unconfigure the device

revise for re-run:
exportDevice

"""


inventory_log = logging.getLogger('inventory_logger')
inventory_log.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(levelname)s][%(filename)s][%(funcName)s][%(lineno)d]-%(message)s ')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
inventory_log.addHandler(handler)


def listAllDevices():
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	config_name="listAllDevices"
	csp_provider="listAllDevices_csp"
	csp_zone="listAllDevices_zone"
	image_id="listAllDevices_image"
	device_id = "listAllDevices_device1"
	device_id_list=[device_id]
	simulator_lib.create_config(config_name, csp_provider, csp_zone, image_id, device_id_list)
	simulator_lib.upload_inventory(config_name, image_id)

	xml_result = broker_api_lib.listAllDevices()
	if not xml_result:
		inventory_log.error("call listAllDevices return False")
		return False
	
	device_list = xml_result.getElementsByTagName("deviceList")[0]
	devices = device_list.getElementsByTagName("device")
	for device in devices:
		if device_id == device.attributes["id"].value.strip():
			return True

	inventory_log.error("Pre-inserted device is not found")
	return False

def getDevice(device_id):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")

	config_name="getDevice"
	csp_provider="getDevice_csp"
	csp_zone="getDevice_zone"
	image_id="getDevice_image"
	device_id_list=[device_id]
	simulator_lib.create_config(config_name, csp_provider, csp_zone, image_id, device_id_list)
	simulator_lib.upload_inventory(config_name, image_id)

	broker_api_lib = broker_api_lib.broker_api_lib(auth_type="api_auth")

	device_msuid = broker_api_lib.get_device_msuid_from_device_id(device_id)
	if not device_msuid:
		inventory_log.error("call getDevice return False")
		return False

	xml_result = broker_api_lib.getDevice(device_msuid)
	if not xml_result:
		inventory_log.error("can't find the device msuid")
		return False
	
	device = xml_result.getElementsByTagName("device")[0]
	if device_id == device.attributes["id"].value.strip():
		return True
	else:
		inventory_log.error("can't find the device")
		return False



def updateDevice(device_id, device_name, device_os, device_fs, write_permission, device_desc, device_mount_point, device_key_size, image_id):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")

	config_name="updateDevice"
	csp_provider="updateDevice_csp"
	csp_zone="updateDevice_zone"
	device_id_list=[device_id]
	simulator_lib.create_config(config_name, csp_provider, csp_zone, image_id, device_id_list)
	simulator_lib.upload_inventory(config_name, image_id)

	device_msuid = broker_api_lib.get_device_msuid_from_device_id(device_id)
	if not device_msuid:
		inventory_log.error("Failed to get device msuid")
		return False


	xml_result = broker_api_lib.updateDevice(device_msuid, device_id, device_name, device_os, device_fs, write_permission, device_desc, device_mount_point, device_key_size, image_id)
	if not xml_result:
		inventory_log.error("call updateDevice return False")
		return False
	
	xml_result = broker_api_lib.getDevice(device_msuid)
	if not xml_result:
		inventory_log.error("call getDevice return False")
		return False

	current_device = xml_result.getElementsByTagName("device")[0]
	result = broker_api_lib.compare_device(device_name, device_os, device_fs, write_permission, device_desc, device_mount_point, device_key_size, image_id, current_device)
	if result:
		return True
	else:
		inventory_log.error("Device is not updated")
		return False


def deleteDevice(device_id):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")

	config_name="deleteDevice"
	csp_provider="deleteDevice_csp"
	csp_zone="deleteDevice_zone"
	image_id="deleteDevice_image"
	device_id_list=[device_id]
	simulator_lib.create_config(config_name, csp_provider, csp_zone, image_id, device_id_list)
	simulator_lib.upload_inventory(config_name, image_id)

	device_msuid = broker_api_lib.get_device_msuid_from_device_id(device_id)
	if not device_msuid:
		inventory_log.error("device msuid is not found")
		return False

	#upload new device so that the first one will become undetected
	device_id_list=["deleteDevice_device_new"]
	simulator_lib.create_config(config_name, csp_provider, csp_zone, image_id, device_id_list)
	simulator_lib.upload_inventory(config_name, image_id)

	result = broker_api_lib.deleteDevice(device_msuid)
	if not result:
		inventory_log.error("call deleteDevice return False")
		return False

	device_msuid = broker_api_lib.get_device_msuid_from_device_id(device_id)
	if not device_msuid:
		return True
	else:
		inventory_log.error("Device is found and which should already be deleted")
		return False


def encryptDevice(device_id):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")

	#create a device
	config_name="encryptDevice"
	csp_provider="encryptDevice_csp"
	csp_zone="encryptDevice_zone"
	image_id="encryptDevice_image"
	device_id_list=[device_id]
	simulator_lib.create_config(config_name, csp_provider, csp_zone, image_id, device_id_list)
	simulator_lib.upload_inventory(config_name, image_id)

	device_msuid = broker_api_lib.get_device_msuid_from_device_id(device_id)
	if not device_msuid:
		inventory_log.error("device msuid is not found")
		return False


	#configure device
	device_name="encryptDevice"
	device_os="windows"
	device_fs="ntfs"
	write_permission="true"
	device_desc="this is encryptDevice"
	device_mount_point="H"
	device_key_size="128"
	xml_result = broker_api_lib.updateDevice(device_msuid, device_id, device_name, device_os, device_fs, write_permission, device_desc, device_mount_point, device_key_size, image_id)
	if not xml_result:
		inventory_log.error("call updateDevice return False")
		return False


	xml_result = broker_api_lib.encryptDevice(device_msuid)
	if not xml_result:
		inventory_log.error("call encryptDevice return False")
		return False

	xml_result = broker_api_lib.getDevice(device_msuid)
	if not xml_result:
		inventory_log.error("call getDevice return False")
		return False

	device = xml_result.getElementsByTagName("device")[0]
	if device.attributes["provisionState"].value.strip() == "pending" and device.attributes["deviceStatus"].value.strip() == "EncryptionPending":
		return True
	else:
		inventory_log.error("Device is not in the encrypt pending state")
		return False


def cloneDevice(from_device_id, to_device_id):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")

	from_device_msuid = broker_api_lib.get_device_msuid_from_device_id(from_device_id)

	to_device_msuid = broker_api_lib.get_device_msuid_from_device_id(to_device_id)


	if from_device_msuid and to_device_msuid:
		image_id="cloneDevice_image"

		# unconfigure the 2 encrypted devices
		device_name=from_device_id
		device_os="windows"
		device_fs="ntfs"
		write_permission="true"
		device_desc="unconfigure the clone source device"
		device_mount_point="H"
		device_key_size="128"
		is_configure="false"
		xml_result = broker_api_lib.updateDevice(from_device_msuid, from_device_id, device_name, device_os, device_fs, write_permission, device_desc, device_mount_point, device_key_size, image_id, is_configure)
		if not xml_result:
			inventory_log.error("call updateDevice return False")
			return False


		device_name=to_device_msuid
		device_os="windows"
		device_fs="ntfs"
		write_permission="true"
		device_desc="unconfigure the clone target device"
		device_mount_point="H"
		device_key_size="128"
		is_configure="false"
		xml_result = broker_api_lib.updateDevice(to_device_msuid, to_device_id, device_name, device_os, device_fs, write_permission, device_desc, device_mount_point, device_key_size, image_id, is_configure)
		if not xml_result:
			inventory_log.error("call updateDevice return False")
			return False


		result = broker_api_lib.deleteDevice(from_device_msuid)
		if not result:
			inventory_log.error("call deleteDevice return False")
			return False

		result = broker_api_lib.deleteDevice(to_device_msuid)
		if not result:
			inventory_log.error("call deleteDevice return False")
			return False




	config_name="cloneDevice"
	csp_provider="cloneDevice_csp"
	csp_zone="cloneDevice_zone"
	image_id="cloneDevice_image"
	device_id_list=[from_device_id, to_device_id]
	simulator_lib.create_config(config_name, csp_provider, csp_zone, image_id, device_id_list)
	simulator_lib.upload_inventory(config_name, image_id)

	from_device_msuid = broker_api_lib.get_device_msuid_from_device_id(from_device_id)
	if not from_device_msuid:
		inventory_log.error("Failed to get source device msuid")
		return False

	to_device_msuid = broker_api_lib.get_device_msuid_from_device_id(to_device_id)
	if not to_device_msuid:
		inventory_log.error("Failed to get target device msuid")
		return False


	#configure device
	device_name=from_device_id
	device_os="windows"
	device_fs="ntfs"
	write_permission="true"
	device_desc="this is cloneDevice"
	device_mount_point="H"
	device_key_size="128"
	xml_result = broker_api_lib.updateDevice(from_device_msuid, from_device_id, device_name, device_os, device_fs, write_permission, device_desc, device_mount_point, device_key_size, image_id)
	if not xml_result:
		inventory_log.error("call updateDevice return False")
		return False


	xml_result = broker_api_lib.encryptDevice(from_device_msuid)
	if not xml_result:
		inventory_log.error("call encryptDevice return False")
		return False

	simulator_lib.encrypt_device(config_name, image_id, [from_device_id])


	xml_result = broker_api_lib.cloneDevice(from_device_msuid, to_device_msuid)
	if not xml_result:
		inventory_log.error("call cloneDevice return False")
		return False

	
	from_xml_result = broker_api_lib.getDevice(from_device_msuid)
	if not from_xml_result:
		inventory_log.error("call getDevice for source device return False")
		return False

	to_xml_result = broker_api_lib.getDevice(to_device_msuid)
	if not to_xml_result:
		inventory_log.error("call getDevice for target device return False")
		return False
	
	from_device = from_xml_result.getElementsByTagName("device")[0]
	to_device = to_xml_result.getElementsByTagName("device")[0]


	#Todo : just checking device status now, can check more later
	if from_device.attributes["deviceStatus"].value.strip() == to_device.attributes["deviceStatus"].value.strip():
		return True
	else:
		return False



# tobe test
def exportDevice(passphrase):

	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	login_name = "export_key_user@trend.com.tw"
	login_pass = "P@ssw0rd"
	user_type = "localuser"
	auth_type = "localuser"
	is_license = "false"
	first_name = "export_key"
	last_name = "user"
	email = "auto_user@trend.com.tw"
	user_role = "Security Administrator"
	mfa_status = "false"


	#create user
	xml_result = broker_api_lib.createUser(login_name, base64.b64encode(login_pass), user_type, auth_type, is_license, first_name, last_name, email, user_role, mfa_status)
	if not xml_result:
		inventory_log.error("call createUser return False")
		return False


	"""
	config_name="exportDevice"
	csp_provider="exportDevice_csp"
	csp_zone="exportDevice_zone"
	image_id="exportDevice_image"
	device_id = "exportDevice_device1"
	device_id_list=[device_id]
	simulator_lib.create_config(config_name, csp_provider, csp_zone, image_id, device_id_list)
	simulator_lib.upload_inventory(config_name, image_id)

	device_msuid = broker_api_lib.get_device_msuid_from_device_id(device_id)
	if not device_msuid:
		inventory_log.error("Failed to get target device msuid")
		return False

	#configure device
	device_name=device_id
	device_os="windows"
	device_fs="ntfs"
	write_permission="true"
	device_desc="this is exportDevice"
	device_mount_point="H"
	device_key_size="128"
	xml_result = broker_api_lib.updateDevice(device_msuid, device_id, device_name, device_os, device_fs, write_permission, device_desc, device_mount_point, device_key_size, image_id)
	if not xml_result:
		inventory_log.error("call updateDevice return False")
		return False


	xml_result = broker_api_lib.encryptDevice(device_msuid)
	if not xml_result:
		inventory_log.error("call encryptDevice return False")
		return False

	simulator_lib.encrypt_device(config_name, image_id, [device_id])
	"""

	broker_api_lib2 = mapi_lib.mapi_lib(auth_type="basic_auth", user_name=login_name, user_pass=login_pass)

	#temp already encrypted device
	device_id = "7853142e-a4e5-42a7-8af3-5f50f1408319"

	raw_result = broker_api_lib2.exportDevice(device_id, passphrase)
	if not raw_result:
		inventory_log.error("call exportDevice return False")
		return False

	export_key_raw = ""
	doc = StringIO(raw_result)
	for event, elem in etree.iterparse(doc, ("start", "end")):
		if elem.tag == "keyGen":
			export_key_raw = elem.text

	#print "export raw:" + export_key_raw
	export_key_xml = xml.dom.minidom.parseString(export_key_raw)
	export_node = export_key_xml.getElementsByTagName("ExportInformation")[0]
	keybackup_node = export_node.getElementsByTagName("KeyBackup")[0]
	salt_node = keybackup_node.getElementsByTagName("Salt")[0]
	salt = mapi_util.getText(salt_node)
	key_node = keybackup_node.getElementsByTagName("Key")[0]
	key = mapi_util.getText(key_node)

	if salt and key:
		result = True
	else:
		result = False

	# clean up, delete user and device
		#get user ID
	user_id = broker_api_lib.get_user_id_from_user_name(login_name)
	if not user_id:
		inventory_log.debug("This user is not found")
		return False

	#delete user
	broker_api_lib.deleteUser(user_id)
	if not user_id:
		inventory_log.debug("Delete user failed")
		return False

	return result

	#verify how

def listAllImages():
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	config_name="listAllImages"
	csp_provider="listAllImages_csp"
	csp_zone="listAllImages_zone"
	image_id="listAllImages_image"
	device_id_list=["listAllImages_device1"]
	simulator_lib.create_config(config_name, csp_provider, csp_zone, image_id, device_id_list)
	simulator_lib.upload_inventory(config_name, image_id)


	xml_result = broker_api_lib.listAllImages()
	if not xml_result:
		inventory_log.error("call listAllImages return False")
		return False
	
	image_list = xml_result.getElementsByTagName("imageList")[0]
	images = image_list.getElementsByTagName("image")
	for image in images:
		if image_id == image.attributes["id"].value.strip():
			return True

	inventory_log.error("pre-inserted image is not found")
	return False


def getImage(image_id):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	config_name="getImage"
	csp_provider="getImage_csp"
	csp_zone="getImage_zone"
	device_id_list=[image_id + "_device1"]
	simulator_lib.create_config(config_name, csp_provider, csp_zone, image_id, device_id_list)
	simulator_lib.upload_inventory(config_name, image_id)
	
	image_msuid = broker_api_lib.get_image_msuid_from_image_id(image_id)
	if not image_msuid:
		inventory_log.error("can't find image msuid from image id")
		return False

	xml_result = broker_api_lib.getImage(image_msuid)
	if not xml_result:
		inventory_log.error("call getImage return False")
		return False
	
	image = xml_result.getElementsByTagName("image")[0]
	if image_id == image.attributes["id"].value.strip():
		return True
	else:
		inventory_log.error("can't find the image")
		return False


# provider wont change
def updateImage(image_id, image_name, image_desc, image_encrypt_swap, csp_provider):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	config_name="getImage"
	csp_zone="getImage_zone"
	device_id_list=[image_id + "_device1"]
	simulator_lib.create_config(config_name, csp_provider, csp_zone, image_id, device_id_list)
	simulator_lib.upload_inventory(config_name, image_id)


	image_msuid = broker_api_lib.get_image_msuid_from_image_id(image_id)
	if not image_msuid:
		inventory_log.error("can't find the image msuid")
		return False

	# Form update data
	xml_result = broker_api_lib.updateImage(image_msuid, image_id, image_name, image_desc, image_encrypt_swap, csp_provider)
	if not xml_result:
		inventory_log.error("call updateImage return False")
		return False

	xml_result = broker_api_lib.getImage(image_msuid)
	if not xml_result:
		inventory_log.error("call getImage return False")
		return False
	
	image = xml_result.getElementsByTagName("image")[0]
	current_image_name = image.attributes["name"].value.strip()
	current_encrypt_swap = image.attributes["encryptSwap"].value.strip()

	desc_node = image.getElementsByTagName("description")[0]
	current_desc = mapi_util.getText(desc_node)

	provider_node = image.getElementsByTagName("provider")[0]
	current_provider = mapi_util.getText(provider_node)


	if image_name == current_image_name and \
	image_desc == current_desc and \
	image_encrypt_swap == current_encrypt_swap:
		return True
	else:
		inventory_log.error("can't find the image")
		return False


def deleteImage(image_id):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	config_name="deleteImage"
	csp_provider="deleteImage_csp"
	csp_zone="deleteImage_zone"
	device_id_list=[image_id + "_device1"]
	simulator_lib.create_config(config_name, csp_provider, csp_zone, image_id, device_id_list)
	simulator_lib.upload_inventory(config_name, image_id)
	
	image_msuid = broker_api_lib.get_image_msuid_from_image_id(image_id)
	if not image_msuid:
		inventory_log.error("can't find the image msuid")
		return False

	result = broker_api_lib.deleteImage(image_msuid)
	if not result:
		inventory_log.error("call deleteImage return False")
		return False


	image_msuid = broker_api_lib.get_image_msuid_from_image_id(image_id)
	if not image_msuid:
		return True
	else:
		inventory_log.error("image msuid is found and should be deleted")
		return False


def listAllProviders():
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	config_name="listAllProviders"
	csp_provider="listAllProviders_csp"
	csp_zone="listAllProviders_zone"
	image_id="listAllProviders_image"
	device_id_list=["listAllProviders_device1"]
	simulator_lib.create_config(config_name, csp_provider, csp_zone, image_id, device_id_list)
	simulator_lib.upload_inventory(config_name, image_id)

	xml_result = broker_api_lib.listAllProviders()
	if not xml_result:
		inventory_log.error("call listAllProviders return False")
		return False
	
	provider_list = xml_result.getElementsByTagName("providerList")[0]
	providers = provider_list.getElementsByTagName("provider")
	for provider in providers:
		if csp_provider == provider.attributes["name"].value.strip():
			return True

	inventory_log.error("cannot find the pre-inserted provider")
	return False


def getProvider(csp_provider):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	config_name="getProvider"
	csp_zone="getProvider_zone"
	image_id="getProvider_image"
	device_id_list=["getProvider_device1"]
	simulator_lib.create_config(config_name, csp_provider, csp_zone, image_id, device_id_list)
	simulator_lib.upload_inventory(config_name, image_id)

	xml_result = broker_api_lib.getProvider(csp_provider)
	if not xml_result:
		inventory_log.error("call getProvider return False")
		return False
	
	provider = xml_result.getElementsByTagName("provider")[0]
	if csp_provider == provider.attributes["name"].value.strip():
		return True
	else:
		inventory_log.error("Provider is not found")
		return False


def createRAID(raid_id, raid_name, raid_level, raid_os, raid_fs, write_permission, provider_zone, device_id_list, raid_desc, provider, image_id, mount_point, key_size):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	# check if the RAID existing or not
	# if existing, delete it
	raid_msuid = broker_api_lib.get_device_msuid_from_device_id(raid_id)
	if raid_msuid:
		result = broker_api_lib.deleteRAID(raid_msuid)
		if not result:
			inventory_log.error("Fall to delete existing RAID")
			return False

	config_name="createRAID"
	simulator_lib.create_config(config_name, provider, provider_zone, image_id, device_id_list)
	simulator_lib.upload_inventory(config_name, image_id)

	device_msuid_list = []
	for device_id in device_id_list:
		device_msuid = broker_api_lib.get_device_msuid_from_device_id(device_id)
		if not device_msuid:
			inventory_log.error("Failed to find device msuid with device id:%s" % (device_id))
			return False
		else:
			device_msuid_list.append(device_msuid)


	xml_result = broker_api_lib.createRAID(raid_msuid, raid_id, raid_name, raid_level, raid_os, raid_fs, write_permission, provider_zone, device_msuid_list, raid_desc, provider, image_id, mount_point, key_size)
	if not xml_result:
		inventory_log.error("call createRAID return False")
		return False

	device_msuid = broker_api_lib.get_device_msuid_from_device_id(raid_id)

	# delete RAID
	#result = broker_api_lib.deleteRAID(device_msuid)
	#if not result:
	#	inventory_log.error("call broker_api_lib.deleteRAID failed")
	#	#return False

	if device_msuid:
		return True
	else:
		inventory_log.error("Failed to find raid")
		return False



def readRAID(raid_id):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	# check if the RAID existing or not
	# if existing, delete it
	raid_msuid = broker_api_lib.get_device_msuid_from_device_id(raid_id)
	if raid_msuid:
		result = broker_api_lib.deleteRAID(raid_msuid)
		if not result:
			inventory_log.error("Fall to delete existing RAID")
			return False


	# create 2 devices
	config_name="readRAID"
	csp_provider="readRAID_csp"
	csp_zone="readRAID_zone"
	image_id="readRAID_image"
	device_id_list=["readRAID_device1","readRAID_device2"]
	simulator_lib.create_config(config_name, csp_provider, csp_zone, image_id, device_id_list)
	simulator_lib.upload_inventory(config_name, image_id)


	device_msuid_list = []
	for device_id in device_id_list:
		device_msuid = broker_api_lib.get_device_msuid_from_device_id(device_id)
		if not device_msuid:
			inventory_log.error("Failed to find device msuid with device id:%s" % (device_id))
			return False
		else:
			device_msuid_list.append(device_msuid)

	# create RAID
	raid_msuid=""
	raid_name="readRAID_raid"
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ext3"
	write_permission="true"
	raid_desc="this is test raid"
	mount_point="/test_raid"
	key_size="128"

	xml_result = broker_api_lib.createRAID(raid_msuid, raid_id, raid_name, raid_level, raid_os, raid_fs, write_permission, csp_zone, device_msuid_list, raid_desc, csp_provider, image_id, mount_point, key_size)
	if not xml_result:
		inventory_log.error("call createRAID return False")
		return False


	device_msuid = broker_api_lib.get_device_msuid_from_device_id(raid_id)
	if not device_msuid:
		inventory_log.error("Fail to find raid device msuid")
		return False

	# Get RAID
	xml_result = broker_api_lib.readRAID(device_msuid)
	if not xml_result:
		inventory_log.error("call readRAID return False")
		return False
	
	device = xml_result.getElementsByTagName("device")[0]
	if raid_id == device.attributes["id"].value.strip():
		return True
	else:
		inventory_log.error("raid is not found")
		return False


#revice compare code
def updateRAID(raid_id, raid_name, raid_level, raid_os, raid_fs, write_permission, provider_zone, device_id_list, raid_desc, provider, image_id, mount_point, key_size):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	# old RAID
	old_raid_id="updateRAID_id"
	old_raid_name="updateRAID_name"
	old_raid_level="RAID0"
	old_raid_os="windows"
	old_raid_fs="ntfs"
	old_write_permission="true"
	old_raid_desc="before update"
	old_mount_point="/mnt/before_update"
	old_key_size="128"

	# check if the RAID existing or not
	# if existing, delete it
	raid_msuid = broker_api_lib.get_device_msuid_from_device_id(old_raid_id)
	if raid_msuid:
		result = broker_api_lib.deleteRAID(raid_msuid)
		if not result:
			inventory_log.error("Fall to delete existing RAID")
			return False

	# check if the RAID existing or not
	# if existing, delete it
	raid_msuid = broker_api_lib.get_device_msuid_from_device_id(raid_id)
	if raid_msuid:
		result = broker_api_lib.deleteRAID(raid_msuid)
		if not result:
			inventory_log.error("Fall to delete existing RAID")
			return False


	# create 2 devices
	old_config_name="updateRAID"
	old_csp_provider=provider
	old_csp_zone=provider_zone
	old_image_id=image_id
	old_device_id_list=["updateRAID_device1","updateRAID_device2"]
	simulator_lib.create_config(old_config_name, old_csp_provider, old_csp_zone, old_image_id, old_device_id_list)
	simulator_lib.upload_inventory(old_config_name, old_image_id)


	old_device_msuid_list = []
	for device_id in old_device_id_list:
		device_msuid = broker_api_lib.get_device_msuid_from_device_id(device_id)
		if not device_msuid:
			inventory_log.error("Failed to find device msuid with device id:%s" % (device_id))
			return False
		else:
			old_device_msuid_list.append(device_msuid)


	# create RAID
	raid_msuid=""
	"""
	old_raid_id="updateRAID_id"
	old_raid_name="updateRAID_name"
	old_raid_level="RAID0"
	old_raid_os="windows"
	old_raid_fs="ntfs"
	old_write_permission="true"
	old_raid_desc="before update"
	old_mount_point="/mnt/before_update"
	old_key_size="128"
	"""

	xml_result = broker_api_lib.createRAID(raid_msuid, old_raid_id, old_raid_name, old_raid_level, old_raid_os, old_raid_fs, old_write_permission, old_csp_zone, old_device_msuid_list, old_raid_desc, old_csp_provider, old_image_id, old_mount_point, old_key_size)
	if not xml_result:
		inventory_log.error("call createRAID return False")
		return False


	raid_msuid = broker_api_lib.get_device_msuid_from_device_id(old_raid_id)
	if not raid_msuid:
		inventory_log.error("no raid msuid")
		return False


	# create new image 
	new_config_name="updateRAID"
	new_csp_provider=provider
	new_csp_zone=provider_zone
	new_image_id=image_id
	new_device_id_list=device_id_list
	simulator_lib.create_config(new_config_name, new_csp_provider, new_csp_zone, new_image_id, new_device_id_list)
	simulator_lib.upload_inventory(new_config_name, new_image_id)

	device_msuid_list = []
	for device_id in device_id_list:
		device_msuid = broker_api_lib.get_device_msuid_from_device_id(device_id)
		if not device_msuid:
			inventory_log.error("Failed to find device msuid with device id:%s" % (device_id))
			return False
		else:
			device_msuid_list.append(device_msuid)


	# update RAID
	xml_result = broker_api_lib.updateRAID(raid_msuid, raid_id, raid_name, raid_level, raid_os, raid_fs, write_permission, new_csp_zone, device_msuid_list, raid_desc, new_csp_provider, new_image_id, mount_point, key_size)
	if not xml_result:
		inventory_log.error("call broker_api_lib.updateRAID failed")
		return False


	# get RAID info
	xml_result = broker_api_lib.readRAID(raid_msuid)
	if not xml_result:
		inventory_log.error("call broker_api_lib.readRAID failed")
		return False


	# check if RAID info is updated
	current_device = xml_result.getElementsByTagName("device")[0]
	is_same = broker_api_lib.compare_raid(raid_id, raid_name, raid_level, raid_os, raid_fs, write_permission, provider_zone, device_msuid_list, raid_desc, provider, image_id, mount_point, key_size, current_device)


	# delete RAID
	#result = broker_api_lib.deleteRAID(raid_msuid)
	#if not result:
	#	inventory_log.error("call broker_api_lib.deleteRAID failed")
	#	#return False

	if is_same:
		return True
	else:
		inventory_log.error("after update, some values are not updated")
		return False



def deleteRAID(raid_id):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	# create 2 devices
	config_name="deleteRAID"
	csp_provider="deleteRAID_csp"
	csp_zone="deleteRAID_zone"
	image_id="deleteRAID_image"
	device_id_list=["deleteRAID_device1","deleteRAID_device2"]
	simulator_lib.create_config(config_name, csp_provider, csp_zone, image_id, device_id_list)
	simulator_lib.upload_inventory(config_name, image_id)


	device_msuid_list = []
	for device_id in device_id_list:
		device_msuid = broker_api_lib.get_device_msuid_from_device_id(device_id)
		if not device_msuid:
			inventory_log.error("Failed to find device msuid with device id:%s" % (device_id))
			return False
		else:
			device_msuid_list.append(device_msuid)

	# create RAID
	raid_msuid=""
	raid_name="deleteRAID_raid"
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ext3"
	write_permission="true"
	raid_desc="this is to delete raid"
	mount_point="/delete_raid"
	key_size="128"

	xml_result = broker_api_lib.createRAID(raid_msuid, raid_id, raid_name, raid_level, raid_os, raid_fs, write_permission, csp_zone, device_msuid_list, raid_desc, csp_provider, image_id, mount_point, key_size)
	if not xml_result:
		inventory_log.error("call createRAID return False")
		return False


	raid_msuid = broker_api_lib.get_device_msuid_from_device_id(raid_id)
	if not raid_msuid:
		inventory_log.error("Fail to find raid device msuid")
		return False


	result = broker_api_lib.deleteRAID(raid_msuid)
	if not result:
		inventory_log.error("call broker_api_lib.deleteRAID failed")
		return False

	raid_msuid = broker_api_lib.get_device_msuid_from_device_id(raid_id)
	if raid_msuid:
		inventory_log.error("raid is not deleted, still existing")
		return False
	
	return True


def encryptRAID(raid_id):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	# check if the RAID existing or not
	# if existing, delete it
	raid_msuid = broker_api_lib.get_device_msuid_from_device_id(raid_id)
	if raid_msuid:
		result = broker_api_lib.deleteRAID(raid_msuid)
		if not result:
			inventory_log.error("Fall to delete existing RAID")
			return False


	# create 2 devices
	config_name="encryptRAID"
	csp_provider="encryptRAID_csp"
	csp_zone="encryptRAID_zone"
	image_id="encryptRAID_image"
	device_id_list=["encryptRAID_device1","encryptRAID_device2"]
	simulator_lib.create_config(config_name, csp_provider, csp_zone, image_id, device_id_list)
	simulator_lib.upload_inventory(config_name, image_id)


	device_msuid_list = []
	for device_id in device_id_list:
		device_msuid = broker_api_lib.get_device_msuid_from_device_id(device_id)
		if not device_msuid:
			inventory_log.error("Failed to find device msuid with device id:%s" % (device_id))
			return False
		else:
			device_msuid_list.append(device_msuid)

	# create RAID
	raid_msuid=""
	raid_name="encryptRAID_raid"
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ext3"
	write_permission="true"
	raid_desc="this is to encrypt raid"
	mount_point="/encryptRAID_raid"
	key_size="128"

	xml_result = broker_api_lib.createRAID(raid_msuid, raid_id, raid_name, raid_level, raid_os, raid_fs, write_permission, csp_zone, device_msuid_list, raid_desc, csp_provider, image_id, mount_point, key_size)
	if not xml_result:
		inventory_log.error("call createRAID return False")
		return False


	raid_msuid = broker_api_lib.get_device_msuid_from_device_id(raid_id)
	if not raid_msuid:
		inventory_log.error("Fail to find raid device msuid")
		return False

	#encrypt RAID
	xml_result = broker_api_lib.encryptDevice(raid_msuid)
	if not xml_result:
		inventory_log.error("call encryptRAID return False")
		return False

	# get RAID info
	xml_result = broker_api_lib.readRAID(raid_msuid)
	if not xml_result:
		inventory_log.error("call broker_api_lib.readRAID failed")
		return False

	device = xml_result.getElementsByTagName("device")[0]
	if device.attributes["provisionState"].value.strip() == "pending" and device.attributes["deviceStatus"].value.strip() == "EncryptionPending":
		return True
	else:
		inventory_log.error("RAID is not in the encrypt pending state")
		return False



if __name__ == '__main__':

	#print listAllImages()
	image_id = "getImage_image"
	#print getImage(image_id)

	#print listAllProviders()
	#provider_name = "getProvider_csp"
	#print getProvider(provider_name)

	#print listAllDevices()
	device_name = "getDevice_device2"
	#print getDevice(device_name)


	image_id = "updateImage_image"
	image_name = "updateImage_name_update"
	image_desc = "updateImage desc update"
	imgae_encrypt_swap = "true"
	provider_name = "updateImage_csp"
	#print updateImage(image_id, image_name, image_desc, imgae_encrypt_swap, provider_name)

	image_id = "deleteImage_image"
	#print deleteImage(image_id)

	image_id="updateDevice_image"
	device_id = "updateDevice_device1"
	device_name="updateDevice_device1_updated"
	device_os="windows"
	device_fs="ntfs"
	write_permission="true"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point="H"
	device_key_size="128"
	#print updateDevice(device_id, device_name, device_os, device_fs, write_permission, device_desc, device_mount_point, device_key_size, image_id)

	device_id = "deleteDevice_device1"
	#print deleteDevice(device_id)

	device_id = "encryptDevice_device1"
	#print encryptDevice(device_id)


	passphrase = "P@ssw0rd"
	print exportDevice(passphrase)

	from_device_id = "cloneDevice_device_2_1"
	to_device_id = "cloneDevice_device_2_2"
	#print cloneDevice(from_device_id, to_device_id)


	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ext3"
	write_permission="true"
	raid_desc="this is test raid"
	mount_point="/test_raid"
	key_size="128"
	#print createRAID(raid_id, raid_name, raid_level, raid_os, raid_fs, write_permission, provider_zone, device_id_list, raid_desc, provider, image_id, mount_point, key_size)

	raid_id = "readRAID_raid"
	#print readRAID(raid_id)


	raid_id="updateRAID_id_new"
	raid_name="updateRAID_name_new"
	provider="updateRAID_csp"
	provider_zone="updateRAID_zone"
	image_id="updateRAID_image"
	device_id_list = ["updateRAID_device1","updateRAID_device2", "updateRAID_device3","updateRAID_device4"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ext3"
	write_permission="true"
	raid_desc="after update"
	mount_point="/mnt/after_update"
	key_size="256"

	#print updateRAID(raid_id, raid_name, raid_level, raid_os, raid_fs, write_permission, provider_zone, device_id_list, raid_desc, provider, image_id, mount_point, key_size)

	raid_id = "deleteRAID_id"
	#print deleteRAID(raid_id)

	raid_id = "encryptRAID_id"
	#print encryptRAID(raid_id)

