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
device validation needs to validate instance



"""


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
		logging.error("call listAllImages return False")
		return False
	
	image_list = xml_result.getElementsByTagName("imageList")[0]
	images = image_list.getElementsByTagName("image")
	for image in images:
		result = broker_api_lib.validate_image(image)
		if not result:
			logging.error("validation failed")
			return False
		
	return True



def getImage(image_msuid):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")

	"""
	config_name="getImage"
	csp_provider="getImage_csp"
	csp_zone="getImage_zone"
	device_id_list=[image_id + "_device1"]
	simulator_lib.create_config(config_name, csp_provider, csp_zone, image_id, device_id_list)
	simulator_lib.upload_inventory(config_name, image_id)
	
	image_msuid = broker_api_lib.get_image_msuid_from_image_id(image_id)
	if not image_msuid:
		logging.error("can't find image msuid from image id")
		return False
	"""
	
	xml_result = broker_api_lib.getImage(image_msuid)
	if not xml_result:
		logging.error("call getImage return False")
		return False

		
	image = xml_result.getElementsByTagName("image")[0]
	result = broker_api_lib.validate_image(image, True)



	return result


# provider wont change
def updateImage(new_image_id, image_name, image_desc, image_encrypt_swap):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	config_name="updateImage"
	image_id = "updateImage_image"
	simulator_lib.create_config(config_name, "updateImage_csp", "updateImage_zone", image_id, ["updateImage_device1"])
	simulator_lib.upload_inventory(config_name, image_id)


	image_msuid = broker_api_lib.get_image_msuid_from_image_id(image_id)
	if not image_msuid:
		logging.error("can't find the image msuid")
		return False

	# Form update data
	xml_result = broker_api_lib.updateImage(image_msuid, new_image_id, image_name, image_desc, image_encrypt_swap)
	if not xml_result:
		logging.error("call updateImage return False")
		return False

	"""
	xml_result = broker_api_lib.getImage(image_msuid)
	if not xml_result:
		logging.error("call getImage return False")
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
		logging.error("can't find the image")
		return False
	"""

	return True


def deleteImage(image_msuid):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")

	"""	
	config_name="deleteImage"
	csp_provider="deleteImage_csp"
	csp_zone="deleteImage_zone"
	device_id_list=[image_id + "_device1"]
	simulator_lib.create_config(config_name, csp_provider, csp_zone, image_id, device_id_list)
	simulator_lib.upload_inventory(config_name, image_id)
	
	image_msuid = broker_api_lib.get_image_msuid_from_image_id(image_id)
	if not image_msuid:
		logging.error("can't find the image msuid")
		return False
	"""
	
	result = broker_api_lib.deleteImage(image_msuid)
	if not result:
		logging.error("call deleteImage return False")
		return False


	return True

	"""
	image_msuid = broker_api_lib.get_image_msuid_from_image_id(image_id)
	if not image_msuid:
		return True
	else:
		logging.error("image msuid is found and should be deleted")
		return False
	"""

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
		logging.error("call listAllProviders return False")
		return False
	
	provider_list = xml_result.getElementsByTagName("providerList")[0]
	providers = provider_list.getElementsByTagName("provider")
	for provider in providers:
		result = broker_api_lib.validate_provider(provider)
		if not result:
			logging.error("validate provider failed")
			return False

	return True


def getProvider(csp_provider, create_new=False):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")

	if create_new:
		config_name="getProvider"
		csp_zone="getProvider_zone"
		image_id="getProvider_image"
		device_id_list=["getProvider_device1"]
		simulator_lib.create_config(config_name, csp_provider, csp_zone, image_id, device_id_list)
		simulator_lib.upload_inventory(config_name, image_id)



	xml_result = broker_api_lib.getProvider(csp_provider)
	if not xml_result:
		logging.error("call getProvider return False")
		return False
	
	provider = xml_result.getElementsByTagName("provider")[0]
	result = broker_api_lib.validate_provider(provider)
	
	if result:
		return True
	else:
		logging.error("validate provider failed")
		return False


def getProvider_case_sensitive(csp_provider, query_provider_name, create_new=False):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")

	if create_new:
		config_name="getProvider"
		csp_zone="getProvider_zone"
		image_id="getProvider_image"
		device_id_list=["getProvider_device1"]
		simulator_lib.create_config(config_name, csp_provider, csp_zone, image_id, device_id_list)
		simulator_lib.upload_inventory(config_name, image_id)



	xml_result = broker_api_lib.getProvider(query_provider_name)
	if not xml_result:
		logging.error("call getProvider return False")
		return False
	
	provider = xml_result.getElementsByTagName("provider")[0]
	result = broker_api_lib.validate_provider(provider)
	
	if result:
		return True
	else:
		logging.error("validate provider failed")
		return False



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
		logging.error("call listAllDevices return False")
		return False
	
	device_list = xml_result.getElementsByTagName("deviceList")[0]
	devices = device_list.getElementsByTagName("device")
	for device in devices:
		result = broker_api_lib.validate_device(device)
		if not result:
			logging.error("validate device fail")
			return False

	return True

def getDevice(device_id, create_new=False):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")


	#if create_new:
	config_name="getDevice"
	csp_provider="getDevice_csp"
	csp_zone="getDevice_zone"
	image_id="getDevice_image"
	device_id_list=["getDevice_device1"]
	simulator_lib.create_config(config_name, csp_provider, csp_zone, image_id, device_id_list)
	simulator_lib.upload_inventory(config_name, image_id)

	device_msuid = broker_api_lib.get_device_msuid_from_device_id(device_id)
	if not device_msuid:
		logging.error("call getDevice return False")
		return False


	xml_result = broker_api_lib.getDevice(device_msuid)
	if not xml_result:
		logging.error("can't find the device msuid")
		return False
	
	device = xml_result.getElementsByTagName("device")[0]
	result = broker_api_lib.validate_device(device)
	if not result:
		logging.error("validate device failed")
		return False
	else:
		return True


def updateDevice(device_id, device_name, device_os, device_fs, write_permission, device_desc, device_mount_point, device_key_size, image_id, is_configure="true", key_mode="cbc"):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")

	config_name="updateDevice"
	csp_provider="updateDevice_csp"
	csp_zone="updateDevice_zone"
	device_id_list=[device_id]
	simulator_lib.create_config(config_name, csp_provider, csp_zone, image_id, device_id_list)
	simulator_lib.upload_inventory(config_name, image_id)

	device_msuid = broker_api_lib.get_device_msuid_from_device_id(device_id)
	if not device_msuid:
		logging.error("Failed to get device msuid")
		return False

	"""
	image_msuid = broker_api_lib.get_image_msuid_from_image_id(image_id)
	if not image_msuid:
		logging.error("Failed to get image msuid")
		return False
	"""
	
	xml_result = broker_api_lib.updateDevice(device_msuid, device_id, device_name, device_os, device_fs, write_permission, device_desc, device_mount_point, device_key_size, image_id, is_configure, key_mode)
	if not xml_result:
		logging.error("call updateDevice return False")
		return False
	
	xml_result = broker_api_lib.getDevice(device_msuid)
	if not xml_result:
		logging.error("call getDevice return False")
		return False

	"""
	current_device = xml_result.getElementsByTagName("device")[0]
	result = broker_api_lib.compare_device(device_name, device_os, device_fs, write_permission, device_desc, device_mount_point, device_key_size, image_id, current_device)
	if result:
		return True
	else:
		logging.error("Device is not updated")
		return False
	"""

	return True

def deleteDevice(device_msuid):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")

	"""
	config_name="deleteDevice"
	csp_provider="deleteDevice_csp"
	csp_zone="deleteDevice_zone"
	image_id="deleteDevice_image"
	device_id_list=[device_id]
	simulator_lib.create_config(config_name, csp_provider, csp_zone, image_id, device_id_list)
	simulator_lib.upload_inventory(config_name, image_id)

	device_msuid = broker_api_lib.get_device_msuid_from_device_id(device_id)
	if not device_msuid:
		logging.error("device msuid is not found")
		return False

	#upload new device so that the first one will become undetected
	device_id_list=["deleteDevice_device_new"]
	simulator_lib.create_config(config_name, csp_provider, csp_zone, image_id, device_id_list)
	simulator_lib.upload_inventory(config_name, image_id)
	"""
	
	result = broker_api_lib.deleteDevice(device_msuid)
	if not result:
		logging.error("call deleteDevice return False")
		return False

	"""
	device_msuid = broker_api_lib.get_device_msuid_from_device_id(device_id)
	if not device_msuid:
		return True
	else:
		logging.error("Device is found and which should already be deleted")
		return False
	"""

	return True





def createRAID(raid_id, raid_name, raid_level, raid_os, raid_fs, write_permission, provider_zone, device_id_list, raid_desc, provider, image_id, mount_point, key_size, is_configure="true", key_mode="cbc", is_detachable="false", test_non_existing_devices=False):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	# check if the RAID existing or not
	# if existing, delete it
	raid_msuid = broker_api_lib.get_device_msuid_from_device_id(raid_id)
	if raid_msuid:
		result = broker_api_lib.deleteRAID(raid_msuid)
		if not result:
			logging.error("Fall to delete existing RAID")
			return False

	config_name="createRAID"
	simulator_lib.create_config(config_name, "createRAID_csp", "createRAID_zone", "createRAID_image", ["createRAID_device1","createRAID_device2"])
	simulator_lib.upload_inventory(config_name, image_id)


	if test_non_existing_devices:
		device_msuid_list = device_id_list
	else:
		if device_id_list == None:
			device_msuid_list = None
		else:
			device_msuid_list = []
			for device_id in device_id_list:
				device_msuid = broker_api_lib.get_device_msuid_from_device_id(device_id)
				if not device_msuid:
					logging.error("Failed to find device msuid with device id:%s" % (device_id))
					return False
				else:
					device_msuid_list.append(device_msuid)


	xml_result = broker_api_lib.createRAID(raid_msuid, raid_id, raid_name, raid_level, raid_os, raid_fs, write_permission, provider_zone, device_msuid_list, raid_desc, provider, image_id, mount_point, key_size, is_configure, key_mode, is_detachable)
	if not xml_result:
		logging.error("call createRAID return False")
		return False

	device_msuid = broker_api_lib.get_device_msuid_from_device_id(raid_id)

	# Get RAID
	xml_result = broker_api_lib.readRAID(device_msuid)
	if not xml_result:
		logging.error("call readRAID return False")
		return False


	# delete RAID
	#result = broker_api_lib.deleteRAID(device_msuid)
	#if not result:
	#	logging.error("call broker_api_lib.deleteRAID failed")
	#	#return False

	if device_msuid:
		return True
	else:
		logging.error("Failed to find raid")
		return False




def readRAID(user_device_msuid):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	# check if the RAID existing or not
	# if existing, delete it
	raid_msuid = broker_api_lib.get_device_msuid_from_device_id("readRAID_raid")
	if raid_msuid:
		result = broker_api_lib.deleteRAID(raid_msuid)
		if not result:
			logging.error("Fall to delete existing RAID")
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
			logging.error("Failed to find device msuid with device id:%s" % (device_id))
			return False
		else:
			device_msuid_list.append(device_msuid)

	# create RAID
	raid_msuid=""
	raid_id="readRAID_raid"
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
		logging.error("call createRAID return False")
		return False

	"""
	device_msuid = broker_api_lib.get_device_msuid_from_device_id(raid_id)
	if not device_msuid:
		logging.error("Fail to find raid device msuid")
		return False
	"""

	# Get RAID
	#print user_device_msuid
	xml_result = broker_api_lib.readRAID(user_device_msuid)
	if not xml_result:
		logging.error("call readRAID return False")
		return False

	"""
	device = xml_result.getElementsByTagName("device")[0]
	if raid_id == device.attributes["id"].value.strip():
		return True
	else:
		logging.error("raid is not found")
		return False
	"""

	return True





#revice compare code
def updateRAID(raid_id, raid_name, raid_level, raid_os, raid_fs, write_permission, provider_zone, device_id_list, raid_desc, provider, image_id, mount_point, key_size, test_non_existing_devices=False):
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
			logging.error("Fall to delete existing RAID")
			return False

	# check if the RAID existing or not
	# if existing, delete it
	raid_msuid = broker_api_lib.get_device_msuid_from_device_id(raid_id)
	if raid_msuid:
		result = broker_api_lib.deleteRAID(raid_msuid)
		if not result:
			logging.error("Fall to delete existing RAID")
			return False


	# create 2 devices
	old_config_name="updateRAID"
	old_csp_provider="updateRAID_csp"
	old_csp_zone="updateRAID_zone"
	old_image_id="updateRAID_image"
	old_device_id_list=["updateRAID_device1","updateRAID_device2"]
	simulator_lib.create_config(old_config_name, old_csp_provider, old_csp_zone, old_image_id, old_device_id_list)
	simulator_lib.upload_inventory(old_config_name, old_image_id)


	old_device_msuid_list = []
	for device_id in old_device_id_list:
		device_msuid = broker_api_lib.get_device_msuid_from_device_id(device_id)
		if not device_msuid:
			logging.error("Failed to find device msuid with device id:%s" % (device_id))
			return False
		else:
			old_device_msuid_list.append(device_msuid)


	# create RAID
	raid_msuid=""
	xml_result = broker_api_lib.createRAID(raid_msuid, old_raid_id, old_raid_name, old_raid_level, old_raid_os, old_raid_fs, old_write_permission, old_csp_zone, old_device_msuid_list, old_raid_desc, old_csp_provider, old_image_id, old_mount_point, old_key_size)
	if not xml_result:
		logging.error("call createRAID return False")
		return False


	raid_msuid = broker_api_lib.get_device_msuid_from_device_id(old_raid_id)
	if not raid_msuid:
		logging.error("no raid msuid")
		return False


	# publish new image and devices
	new_config_name="updateRAID"
	new_csp_provider=provider
	new_csp_zone=provider_zone
	new_image_id=image_id
	new_device_id_list=device_id_list
	simulator_lib.create_config(new_config_name, new_csp_provider, new_csp_zone, new_image_id, new_device_id_list)
	simulator_lib.upload_inventory(new_config_name, new_image_id)


	if test_non_existing_devices:
		device_msuid_list = device_id_list
	else:
		device_msuid_list = []
		if device_id_list == None:
			device_msuid_list = None
		else:
			for device_id in device_id_list:
				device_msuid = broker_api_lib.get_device_msuid_from_device_id(device_id)
				if not device_msuid:
					logging.error("Failed to find device msuid with device id:%s" % (device_id))
					return False
				else:
					device_msuid_list.append(device_msuid)


	# update RAID
	xml_result = broker_api_lib.updateRAID(raid_msuid, raid_id, raid_name, raid_level, raid_os, raid_fs, write_permission, new_csp_zone, device_msuid_list, raid_desc, new_csp_provider, new_image_id, mount_point, key_size)
	if not xml_result:
		logging.error("call broker_api_lib.updateRAID failed")
		return False


	# get RAID info
	xml_result = broker_api_lib.readRAID(raid_msuid)
	if not xml_result:
		logging.error("call broker_api_lib.readRAID failed")
		return False


	# check if RAID info is updated
	#current_device = xml_result.getElementsByTagName("device")[0]
	#is_same = broker_api_lib.compare_raid(raid_id, raid_name, raid_level, raid_os, raid_fs, write_permission, provider_zone, device_msuid_list, raid_desc, provider, image_id, mount_point, key_size, current_device)


	# delete RAID
	#result = broker_api_lib.deleteRAID(raid_msuid)
	#if not result:
	#	logging.error("call broker_api_lib.deleteRAID failed")
	#	#return False

	"""
	if is_same:
		return True
	else:
		logging.error("after update, some values are not updated")
		return False
	"""

	return True



def encryptDevice(device_id, upload_inventory=False, provision_state="pending"):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")

	if upload_inventory:
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
			logging.error("device msuid is not found")
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
			logging.error("call updateDevice return False")
			return False
	else:
		device_msuid = device_id

	xml_result = broker_api_lib.encryptDevice(device_msuid, provision_state)
	if not xml_result:
		logging.error("call encryptDevice return False")
		return False

	xml_result = broker_api_lib.getDevice(device_msuid)
	if not xml_result:
		logging.error("call getDevice return False")
		return False

	device = xml_result.getElementsByTagName("device")[0]
	if device.attributes["provisionState"].value.strip() == "pending" and device.attributes["deviceStatus"].value.strip() == "EncryptionPending":
		return True
	else:
		logging.error("Device is not in the encrypt pending state")
		return False


def deleteRAID(raid_id, create_raid=False):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")

	if create_raid:
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
				logging.error("Failed to find device msuid with device id:%s" % (device_id))
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
			logging.error("call createRAID return False")
			return False


		raid_msuid = broker_api_lib.get_device_msuid_from_device_id(raid_id)
		if not raid_msuid:
			logging.error("Fail to find raid device msuid")
			return False
	else:
		raid_msuid = raid_id


	result = broker_api_lib.deleteRAID(raid_msuid)
	if not result:
		logging.error("call broker_api_lib.deleteRAID failed")
		return False

	raid_msuid = broker_api_lib.get_device_msuid_from_device_id(raid_id)
	if raid_msuid:
		logging.error("raid is not deleted, still existing")
		return False
	
	return True


def encryptRAID(raid_id, create_raid=False, provision_state="pending"):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")


	if create_raid:
		# check if the RAID existing or not
		# if existing, delete it
		raid_msuid = broker_api_lib.get_device_msuid_from_device_id(raid_id)
		if raid_msuid:
			result = broker_api_lib.deleteRAID(raid_msuid)
			if not result:
				logging.error("Fall to delete existing RAID")
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
				logging.error("Failed to find device msuid with device id:%s" % (device_id))
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
			logging.error("call createRAID return False")
			return False


		raid_msuid = broker_api_lib.get_device_msuid_from_device_id(raid_id)
		if not raid_msuid:
			logging.error("Fail to find raid device msuid")
			return False
	else:
		raid_msuid = raid_id


	#encrypt RAID
	xml_result = broker_api_lib.encryptRAID(raid_msuid, provision_state)
	if not xml_result:
		logging.error("call encryptRAID return False")
		return False

	# get RAID info
	xml_result = broker_api_lib.readRAID(raid_msuid)
	if not xml_result:
		logging.error("call broker_api_lib.readRAID failed")
		return False

	device = xml_result.getElementsByTagName("device")[0]
	if device.attributes["provisionState"].value.strip() == "pending" and device.attributes["deviceStatus"].value.strip() == "EncryptionPending":
		return True
	else:
		logging.error("RAID is not in the encrypt pending state")
		return False



def cloneDevice(from_device_id, to_device_id, existing_from_device=False, existing_to_device=False):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")

	from_device_msuid = broker_api_lib.get_device_msuid_from_device_id(from_device_id)
	to_device_msuid = broker_api_lib.get_device_msuid_from_device_id(to_device_id)

	if from_device_msuid:
		image_id="cloneDevice_image"

		# unconfigure encrypted devices
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
			logging.error("call updateDevice return False")
			return False

		result = broker_api_lib.deleteDevice(from_device_msuid)
		if not result:
			logging.error("call deleteDevice return False")
			return False
		
	if to_device_msuid:
		image_id="cloneDevice_image"

		# unconfigure encrypted devices
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
			logging.error("call updateDevice return False")
			return False

		result = broker_api_lib.deleteDevice(to_device_msuid)
		if not result:
			logging.error("call deleteDevice return False")
			return False


	config_name="cloneDevice"
	csp_provider="cloneDevice_csp"
	csp_zone="cloneDevice_zone"
	image_id="cloneDevice_image"

	if existing_from_device and existing_to_device:
		device_id_list=[from_device_id, to_device_id]
	elif existing_from_device:
		device_id_list=[from_device_id]
	elif existing_to_device:
		device_id_list=[to_device_id]
		
	simulator_lib.create_config(config_name, csp_provider, csp_zone, image_id, device_id_list)
	simulator_lib.upload_inventory(config_name, image_id)

	if existing_from_device:
		from_device_msuid = broker_api_lib.get_device_msuid_from_device_id(from_device_id)
		if not from_device_msuid:
			logging.error("Failed to get source device msuid")
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
			logging.error("call updateDevice return False")
			return False

		xml_result = broker_api_lib.encryptDevice(from_device_msuid)
		if not xml_result:
			logging.error("call encryptDevice return False")
			return False

		simulator_lib.encrypt_device(config_name, image_id, [from_device_id])
	else:
		from_device_msuid = from_device_id

	if existing_to_device:
		to_device_msuid = broker_api_lib.get_device_msuid_from_device_id(to_device_id)
		if not to_device_msuid:
			logging.error("Failed to get target device msuid")
			return False
	else:
		to_device_msuid = to_device_id


	xml_result = broker_api_lib.cloneDevice(from_device_msuid, to_device_msuid)
	if not xml_result:
		logging.error("call cloneDevice return False")
		return False

	
	from_xml_result = broker_api_lib.getDevice(from_device_msuid)
	if not from_xml_result:
		logging.error("call getDevice for source device return False")
		return False

	to_xml_result = broker_api_lib.getDevice(to_device_msuid)
	if not to_xml_result:
		logging.error("call getDevice for target device return False")
		return False
	
	from_device = from_xml_result.getElementsByTagName("device")[0]
	to_device = to_xml_result.getElementsByTagName("device")[0]


	#Todo : just checking device status now, can check more later
	if from_device.attributes["deviceStatus"].value.strip() == to_device.attributes["deviceStatus"].value.strip():
		return True
	else:
		return False



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


	#get user ID
	user_id = broker_api_lib.get_user_id_from_user_name(login_name)
	if user_id:
		#delete user
		broker_api_lib.deleteUser(user_id)

	#create user
	xml_result = broker_api_lib.createUser(login_name, base64.b64encode(login_pass), user_type, auth_type, is_license, first_name, last_name, email, user_role, mfa_status)
	if not xml_result:
		logging.error("call createUser return False")
		return False


	config_name="exportDevice"
	csp_provider="exportDevice_csp"
	csp_zone="exportDevice_zone"
	image_id="exportDevice_image"
	device_id = "exportDevice_device1"
	device_id_list=[device_id]

	device_msuid = broker_api_lib.get_device_msuid_from_device_id(device_id)

	if device_msuid:
		# unconfigure encrypted devices
		device_name=device_id
		device_os="windows"
		device_fs="ntfs"
		write_permission="true"
		device_desc="this is exportDevice"
		device_mount_point="H"
		device_key_size="128"
		is_configure="false"
		xml_result = broker_api_lib.updateDevice(device_msuid, device_id, device_name, device_os, device_fs, write_permission, device_desc, device_mount_point, device_key_size, image_id, is_configure)
		if not xml_result:
			logging.error("call updateDevice return False")
			return False

		result = broker_api_lib.deleteDevice(device_msuid)
		if not result:
			logging.error("call deleteDevice return False")
			return False


	simulator_lib.create_config(config_name, csp_provider, csp_zone, image_id, device_id_list)
	simulator_lib.upload_inventory(config_name, image_id)

	device_msuid = broker_api_lib.get_device_msuid_from_device_id(device_id)
	if not device_msuid:
		logging.error("Failed to get target device msuid")
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
		logging.error("call updateDevice return False")
		return False

	xml_result = broker_api_lib.encryptDevice(device_msuid)
	if not xml_result:
		logging.error("call encryptDevice return False")
		return False

	simulator_lib.encrypt_device(config_name, image_id, [device_id])

	broker_api_lib2 = mapi_lib.mapi_lib(auth_type="basic_auth", user_name=login_name, user_pass=login_pass)

	#temp already encrypted device
	#device_id = "7853142e-a4e5-42a7-8af3-5f50f1408319"

	raw_result = broker_api_lib2.exportDevice(device_msuid, passphrase)
	if not raw_result:
		logging.error("call exportDevice return False")
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
		return True
	else:
		return False



def cross_accounts_view_test():


	broker_api_lib_user1 = mapi_lib.mapi_lib(auth_type="basic_auth", user_name="shaodanny@gmail.com", user_pass="P@ssw0rd@123")

	config_name="cross_accounts_view"
	csp_provider="cross_accounts_view_csp"
	csp_zone="cross_accounts_view_zone"
	image_id="cross_accounts_view_image"
	device_id = "cross_accounts_view_device1"
	device_id_list=[device_id]

	"""
	device_msuid = broker_api_lib_user1.get_device_msuid_from_device_id(device_id)

	if device_msuid:
		result = broker_api_lib_user1.deleteDevice(device_msuid)
		if not result:
			logging.error("call deleteDevice return False")
			return False


	simulator_lib.create_config(config_name, csp_provider, csp_zone, image_id, device_id_list)
	simulator_lib.upload_inventory(config_name, image_id)

	device_msuid = broker_api_lib_user1.get_device_msuid_from_device_id(device_id)
	if not device_msuid:
		logging.error("Failed to get target device msuid")
		return False
	"""

	broker_api_lib_user2 = mapi_lib.mapi_lib(auth_type="basic_auth", user_name="shaodanny%2B2@gmail.com", user_pass="P@ssw0rd", api_account_id="DE71A0B9-5F38-4915-B650-C1B4A4FBC0D1", api_passphrase="QU+ppeMIW3YR")

	"""
	xml_result = broker_api_lib_user2.getDevice(device_msuid)
	if xml_result:
		logging.error("Error: should not see the device from other user")
		return False
	"""

	xml_result = broker_api_lib_user2.listCurrentUserAccounts()
	if not xml_result:
		logging.error("call listCurrentUserAccounts return False")
		return False



	return True


if __name__ == '__main__':

	# old RAT cases

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


	passphrase = "P@ssw0rd"
	#print exportDevice(passphrase)

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






	# DETAIL TEST START FROM HERE----------------------------------------------------

	#print listAllImages()

	# ------------------------------------------------------


	# getImage

	#image_id = ""
	# empty image id returns image list
	
	#image_id = "00000000-0000-0000-0000-000000000000"
	#returns http 400 bad request
	# server error, TMEG.Cloud9.Exceptions.DatabaseException: Data Error: -402

	#image_id = "asdfasdfsdtfgdfg87d89fyaeao8sdfg79ay"
	# 500 internal server error
	# System.FormatException: Guid should contain 32 digits with 4 dashes (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx).

	#image_id = "asdfasdfsdtfgd"
	# 500 internal server error
	# System.FormatException: Guid should contain 32 digits with 4 dashes (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx).

	#image_id = mapi_util.SPECIAL_CHARS
	# HTTP Error 401: Unauthorized
	
	#print getImage(image_id)

	# ------------------------------------------------------

	# original
	"""
	image_id = "updateImage_image"
	image_name = "updateImage_name"
	image_desc = "updateImage desc"
	image_encrypt_swap = "true"
	"""

	# image_name = ""
	# result: ok "" empty is not updated
	"""
	image_id = "updateImage_image"
	image_name = ""
	image_desc = "updateImage desc update"
	image_encrypt_swap = "true"
	"""

	# image_name = UI max 32, try 33
	# result: ok 
	"""
	image_id = "updateImage_image"
	image_name = mapi_util.random_str(33)
	image_desc = "updateImage desc update"
	image_encrypt_swap = "true"
	"""


	# image_name = max 1024 chars
	# result : ok
	"""
	image_id = "updateImage_image"
	image_name = mapi_util.random_str(1024)
	image_desc = "updateImage desc update"
	image_encrypt_swap = "true"
	"""

	# image_name = max 1024 + 1
	# result : ok but extra chars is truncated
	"""
	image_id = "updateImage_image"
	image_name = mapi_util.random_str(1025)
	image_desc = "updateImage desc update"
	image_encrypt_swap = "true"
	"""

	# image_name = special chars
	# result : HTTP Error 500: Whitespace must appear between attributes. Line 1, position 263.
	"""
	image_id = "updateImage_image"
	image_name = mapi_util.SPECIAL_CHARS
	image_desc = "updateImage desc update"
	image_encrypt_swap = "true"
	"""

	# image_id = "updateImage_image_update"
	# result : ok but image_id is not updated
	"""
	image_id = "updateImage_image_update"
	image_name = "updateImage_name"
	image_desc = "updateImage desc update"
	image_encrypt_swap = "true"
	"""


	# image_desc = ""
	# result : ok 
	"""
	image_id = "updateImage_image"
	image_name = "updateImage_name"
	image_desc = ""
	image_encrypt_swap = "true"
	"""

	# image_desc = UI max 360
	# result : ok 
	"""
	image_id = "updateImage_image"
	image_name = "updateImage_name"
	image_desc = mapi_util.random_str(360)
	image_encrypt_swap = "true"
	"""

	# image_desc = UI max 360+1
	# result : ok 
	"""
	image_id = "updateImage_image"
	image_name = "updateImage_name"
	image_desc = mapi_util.random_str(361)
	image_encrypt_swap = "true"
	"""
	
	# image_desc = DB max nvarchar(max)
	# result : ? too big to test with
	"""
	image_id = "updateImage_image"
	image_name = "updateImage_name"
	image_desc = mapi_util.random_str(361)
	image_encrypt_swap = "true"
	"""

	# image_desc = special chars
	# result : ok
	"""
	image_id = "updateImage_image"
	image_name = "updateImage_name"
	image_desc = mapi_util.SPECIAL_CHARS
	image_encrypt_swap = "true"
	"""

	# image_encrypt_swap = "true"
	# result : ok
	"""
	image_id = "updateImage_image"
	image_name = "updateImage_name"
	image_desc = "image description"
	image_encrypt_swap = "true"
	"""

	# image_encrypt_swap = "false"
	# result : ok
	"""
	image_id = "updateImage_image"
	image_name = "updateImage_name"
	image_desc = "image description"
	image_encrypt_swap = "false"
	"""

	# image_encrypt_swap = ""
	# result : HTTP Error 500: There is an error in XML document (1, 252).
	"""
	image_id = "updateImage_image"
	image_name = "updateImage_name"
	image_desc = "image description"
	image_encrypt_swap = ""
	"""

	# image_encrypt_swap = random 30 chars
	# result : HTTP Error 500: There is an error in XML document (1, 282).
	"""
	image_id = "updateImage_image"
	image_name = "updateImage_name"
	image_desc = "image description"
	image_encrypt_swap = mapi_util.random_str(30)
	"""

	# image_encrypt_swap = special chars
	# result : HTTP Error 500: Whitespace must appear between attributes. Line 1, position 226.
	"""
	image_id = "updateImage_image"
	image_name = "updateImage_name"
	image_desc = "image description"
	image_encrypt_swap = mapi_util.SPECIAL_CHARS
	"""

	# image_encrypt_swap = case sensitive
	# result : HTTP Error 500: There is an error in XML document (1, 256).
	"""
	image_id = "updateImage_image"
	image_name = "updateImage_name"
	image_desc = "image description"
	image_encrypt_swap = "TRUE"
	"""

	#print updateImage(image_id, image_name, image_desc, image_encrypt_swap)


	# ------------------------------------------------------
	
	# deleteImage

	#image_id = ""
	# HTTP Error 405: Method Not Allowed
	
	#image_id = "00000000-0000-0000-0000-000000000000"
	#result: ok ? non-existing should return error?


	# image_id = "asdfasdfsdtfgdfg87d89fyaeao8sdfg79ay"
	# HTTP Error 500: Internal Server Error

	# image_id = "asdfasdfsdtfgd"
	# HTTP Error 500 internal server error

	# image_id = mapi_util.SPECIAL_CHARS
	# HTTP Error 307: Temporary Redirect
	
	#print deleteImage(image_id)

	# ------------------------------------------------------


	#print listAllProviders()

	# ------------------------------------------------------

	# original
	"""
	provider_name = "getProvider_csp"
	print getProvider(provider_name, True)
	"""

	# provider_name = ""
	# result: return all providers
	"""
	provider_name = ""
	print getProvider(provider_name, True)
	"""

	# provider_name = db max 1024, however db insertion is ok but when get the max name in the URL as tryout is 234
	# result: HTTP Error 400: Bad Request
	"""	
	provider_name = mapi_util.random_str(235)
	print getProvider(provider_name, True)
	"""

	# provider_name = mapi_util.random_str(10), query non-existing provider
	# result: HTTP Error 400: Bad Request
	"""
	provider_name = mapi_util.random_str(10)
	print getProvider(provider_name)
	"""


	# provider_name = mapi_util.SPECAIL_CHARS
	# result: HTTP Error 401: Unauthorized, db insertion ok, failed when in the URL
	"""
	provider_name = mapi_util.SPECIAL_CHARS
	print getProvider(provider_name, True)
	"""

	# provider_name = sensitive test
	# result: ok, query csp provider is case insensitive, it that right?
	"""
	csp_provider = "AaBbCc"
	query_provider_name = "aabbcc"
	print getProvider_case_sensitive(csp_provider, query_provider_name, True)
	"""
	
	# ------------------------------------------------------


	#print listAllDevices()

	# ------------------------------------------------------

	# getDevice

	# original
	#device_id = "getDevice_device1"

	# empty device list, return all devices
	# device_id = ""
	
	
	#returns http 400 bad request
	# server error, TMEG.Cloud9.Exceptions.DatabaseException: Data Error: -402	
	#device_id = "00000000-0000-0000-0000-000000000000"

	# 500 internal server error
	# System.FormatException: Guid should contain 32 digits with 4 dashes (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx).
	#device_id = "asdfasdfsdtfgdfg87d89fyaeao8sdfg79ay"

	# 500 internal server error
	# System.FormatException: Guid should contain 32 digits with 4 dashes (xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx).
	#device_id = "asdfasdfsdtfgd"

	# HTTP Error 401: Unauthorized
	#device_id = mapi_util.SPECIAL_CHARS

	
	#print getDevice(device_id)



	# ------------------------------------------------------

	# original
	"""
	device_id = "updateDevice_device1"
	device_name="updateDevice_device1_updated"
	device_os="windows"
	device_fs="ntfs"
	write_permission="true"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point="H"
	device_key_size="128"
	image_id="updateDevice_image"
	"""

	# device_name=""
	# result: is empty, name is not updated
	"""
	device_id = "updateDevice_device1"
	device_name=""
	device_os="windows"
	device_fs="ntfs"
	write_permission="true"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point="H"
	device_key_size="128"
	image_id="updateDevice_image"
	print updateDevice(device_id, device_name, device_os, device_fs, write_permission, device_desc, device_mount_point, device_key_size, image_id)
	"""
	

	# device_name= max 1024
	# result: ok
	"""
	device_id = "updateDevice_device1"
	device_name= mapi_util.random_str(1024)
	print device_name
	device_os="windows"
	device_fs="ntfs"
	write_permission="true"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point="H"
	device_key_size="128"
	image_id="updateDevice_image"
	print updateDevice(device_id, device_name, device_os, device_fs, write_permission, device_desc, device_mount_point, device_key_size, image_id)
	"""

	# device_name= max 1024+1 
	# result: ok but extra chars is truncated
	"""
	device_id = "updateDevice_device1"
	device_name= mapi_util.random_str(1025)
	print device_name
	device_os="windows"
	device_fs="ntfs"
	write_permission="true"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point="H"
	device_key_size="128"
	image_id="updateDevice_image"
	"""

	# device_name= mapi_util.SPECIAL_CHARS
	# result: HTTP Error 500: Whitespace must appear between attributes. Line 1, position 264
	"""
	device_id = "updateDevice_device1"
	device_name= mapi_util.SPECIAL_CHARS
	device_os="windows"
	device_fs="ntfs"
	write_permission="true"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point="H"
	device_key_size="128"
	image_id="updateDevice_image"
	"""

	# available choise = windows/linux
	# device_os="windows"
	# result: ok
	"""
	device_id = "updateDevice_device1"
	device_name= "updateDevice_device1"
	device_os="windows"
	device_fs="ntfs"
	write_permission="true"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point="H"
	device_key_size="128"
	image_id="updateDevice_image"
	"""

	# device_os="linux"
	# result: ok
	"""
	device_id = "updateDevice_device1"
	device_name= "updateDevice_device1"
	device_os="linux"
	device_fs="ntfs"
	write_permission="true"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point="H"
	device_key_size="128"
	image_id="updateDevice_image"
	"""

	# device_os=""
	# result: HTTP Error 500: There is an error in XML document (1, 318).
	"""
	device_id = "updateDevice_device1"
	device_name= "updateDevice_device1"
	device_os=""
	device_fs="ntfs"
	write_permission="true"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point="H"
	device_key_size="128"
	image_id="updateDevice_image"
	"""

	# device_os= random 20 chars
	# result: HTTP Error 500: There is an error in XML document (1, 318).
	"""
	device_id = "updateDevice_device1"
	device_name= "updateDevice_device1"
	device_os= mapi_util.random_str(20)
	device_fs="ntfs"
	write_permission="true"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point="H"
	device_key_size="128"
	image_id="updateDevice_image"
	"""

	# device_os= special chars
	# result: HTTP Error 500: Whitespace must appear between attributes. Line 1, position 291.
	"""
	device_id = "updateDevice_device1"
	device_name= "updateDevice_device1"
	device_os= mapi_util.SPECIAL_CHARS
	device_fs="ntfs"
	write_permission="true"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point="H"
	device_key_size="128"
	image_id="updateDevice_image"
	"""

	# device_os= case sensitive
	# result: HTTP Error 500: There is an error in XML document (1, 323).
	"""
	device_id = "updateDevice_device1"
	device_name= "updateDevice_device1"
	device_os= "LINUX"
	device_fs="ntfs"
	write_permission="true"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point="H"
	device_key_size="128"
	image_id="updateDevice_image"
	"""

	# available choices = fat32/ntfs/xfs/ext3
	# device_fs="ntfs"
	# result: ok
	"""
	device_id = "updateDevice_device1"
	device_name= "updateDevice_device1"
	device_os= "windows"
	device_fs="ntfs"
	write_permission="true"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point="H"
	device_key_size="128"
	image_id="updateDevice_image"
	"""

	# available choices = fat32/ntfs/xfs/ext3
	# device_fs="fat32"
	# result: ok
	"""
	device_id = "updateDevice_device1"
	device_name= "updateDevice_device1"
	device_os= "windows"
	device_fs="fat32"
	write_permission="true"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point="H"
	device_key_size="128"
	image_id="updateDevice_image"
	"""

	# available choices = fat32/ntfs/xfs/ext3
	# device_fs="xfs"
	# result: ok
	"""
	device_id = "updateDevice_device1"
	device_name= "updateDevice_device1"
	device_os= "windows"
	device_fs="xfs"
	write_permission="true"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point="H"
	device_key_size="128"
	image_id="updateDevice_image"
	"""

	# available choices = fat32/ntfs/xfs/ext3
	# device_fs="ext3"
	# result: ok
	"""
	device_id = "updateDevice_device1"
	device_name= "updateDevice_device1"
	device_os= "windows"
	device_fs="ext3"
	write_permission="true"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point="H"
	device_key_size="128"
	image_id="updateDevice_image"
	"""

	# available choices = fat32/ntfs/xfs/ext3
	# device_fs=""
	# result: HTTP Error 500: There is an error in XML document (1, 321).
	"""
	device_id = "updateDevice_device1"
	device_name= "updateDevice_device1"
	device_os= "windows"
	device_fs=""
	write_permission="true"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point="H"
	device_key_size="128"
	image_id="updateDevice_image"
	"""


	# available choices = fat32/ntfs/xfs/ext3
	# device_fs= random 20 chars
	# result: HTTP Error 500: There is an error in XML document (1, 341).
	"""
	device_id = "updateDevice_device1"
	device_name= "updateDevice_device1"
	device_os= "windows"
	device_fs= mapi_util.random_str(20)
	write_permission="true"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point="H"
	device_key_size="128"
	image_id="updateDevice_image"
	"""

	# available choices = fat32/ntfs/xfs/ext3
	# device_fs= case sensitive 
	# result: HTTP Error 500: There is an error in XML document (1, 326).
	"""
	device_id = "updateDevice_device1"
	device_name= "updateDevice_device1"
	device_os= "windows"
	device_fs= "FAT32"
	write_permission="true"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point="H"
	device_key_size="128"
	image_id="updateDevice_image"
	"""

	# write_permission="true"
	# result: ok
	"""
	device_id = "updateDevice_device1"
	device_name= "updateDevice_device1"
	device_os= "windows"
	device_fs= "fat32"
	write_permission="true"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point="H"
	device_key_size="128"
	image_id="updateDevice_image"
	"""

	# write_permission="false"
	# result: ok
	"""
	device_id = "updateDevice_device1"
	device_name= "updateDevice_device1"
	device_os= "windows"
	device_fs= "fat32"
	write_permission="false"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point="H"
	device_key_size="128"
	image_id="updateDevice_image"
	"""

	# write_permission=""
	# result: HTTP Error 500: There is an error in XML document (1, 322).
	"""
	device_id = "updateDevice_device1"
	device_name= "updateDevice_device1"
	device_os= "windows"
	device_fs= "fat32"
	write_permission=""
	device_desc="this is updateDevice_device1 updated"
	device_mount_point="H"
	device_key_size="128"
	image_id="updateDevice_image"
	"""
	

	# write_permission= random 20 char
	# result: HTTP Error 500: There is an error in XML document (1, 332).
	"""	
	device_id = "updateDevice_device1"
	device_name= "updateDevice_device1"
	device_os= "windows"
	device_fs= "fat32"
	write_permission=mapi_util.random_str(10)
	device_desc="this is updateDevice_device1 updated"
	device_mount_point="H"
	device_key_size="128"
	image_id="updateDevice_image"
	"""


	# write_permission= special chars
	# result: HTTP Error 500: Whitespace must appear between attributes. Line 1, position 345.
	"""
	device_id = "updateDevice_device1"
	device_name= "updateDevice_device1"
	device_os= "windows"
	device_fs= "fat32"
	write_permission=mapi_util.SPECIAL_CHARS
	device_desc="this is updateDevice_device1 updated"
	device_mount_point="H"
	device_key_size="128"
	image_id="updateDevice_image"
	"""


	# write_permission= case sensitive
	# result: HTTP Error 500: There is an error in XML document (1, 326).
	"""
	device_id = "updateDevice_device1"
	device_name= "updateDevice_device1"
	device_os= "windows"
	device_fs= "fat32"
	write_permission="TRUE"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point="H"
	device_key_size="128"
	image_id="updateDevice_image"
	"""


	# write_permission= case sensitive
	# result: HTTP Error 500: There is an error in XML document (1, 326).

	device_id = "updateDevice_device1"
	device_name= "updateDevice_device1"
	device_os= "windows"
	device_fs= "fat32"
	write_permission="true"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point="H"
	device_key_size="128"
	image_id="updateDevice_image"



	# device_desc=""
	# result: ok
	"""
	device_id = "updateDevice_device1"
	device_name= "updateDevice_device1"
	device_os= "windows"
	device_fs= "fat32"
	write_permission="true"
	device_desc=""
	device_mount_point="H"
	device_key_size="128"
	image_id="updateDevice_image"
	"""

	# device_desc=random 2000 chars
	# result: ok
	"""
	device_id = "updateDevice_device1"
	device_name= "updateDevice_device1"
	device_os= "windows"
	device_fs= "fat32"
	write_permission="true"
	device_desc=mapi_util.random_str(2000)
	print device_desc
	device_mount_point="H"
	device_key_size="128"
	image_id="updateDevice_image"
	"""

	# device_desc=random 2000 chars +1
	# result: ok
	"""
	device_id = "updateDevice_device1"
	device_name= "updateDevice_device1"
	device_os= "windows"
	device_fs= "fat32"
	write_permission="true"
	device_desc=mapi_util.random_str(2001)
	print device_desc
	device_mount_point="H"
	device_key_size="128"
	image_id="updateDevice_image"
	"""

	# device_desc= nvarchar(max), not doable
	# result: ok
	"""
	device_id = "updateDevice_device1"
	device_name= "updateDevice_device1"
	device_os= "windows"
	device_fs= "fat32"
	write_permission="true"
	device_desc=mapi_util.random_str(2001)
	print device_desc
	device_mount_point="H"
	device_key_size="128"
	image_id="updateDevice_image"
	"""


	# device_desc= special chars 
	# result: ok
	"""
	device_id = "updateDevice_device1"
	device_name= "updateDevice_device1"
	device_os= "windows"
	device_fs= "fat32"
	write_permission="true"
	device_desc=mapi_util.SPECIAL_CHARS
	device_mount_point="H"
	device_key_size="128"
	image_id="updateDevice_image"
	"""


	# device_mount_point="H"
	# result: ok
	"""
	device_id = "updateDevice_device1"
	device_name="updateDevice_device1"
	device_os="windows"
	device_fs="ntfs"
	write_permission="true"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point="H"
	device_key_size="128"
	image_id="updateDevice_image"
	"""

	# device_mount_point="\mnt\test"
	# result: ok
	"""
	device_id = "updateDevice_device1"
	device_name="updateDevice_device1"
	device_os="windows"
	device_fs="ntfs"
	write_permission="true"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point="\\mnt\\test"
	device_key_size="128"
	image_id="updateDevice_image"
	"""

	# device_mount_point=""
	# result: ok, empty mount point wont be updated
	"""
	device_id = "updateDevice_device1"
	device_name="updateDevice_device1"
	device_os="windows"
	device_fs="ntfs"
	write_permission="true"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point=""
	device_key_size="128"
	image_id="updateDevice_image"
	"""

	# device_mount_point=UI max 255
	# result: ok
	"""
	device_id = "updateDevice_device1"
	device_name="updateDevice_device1"
	device_os="windows"
	device_fs="ntfs"
	write_permission="true"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point=mapi_util.random_str(255)
	device_key_size="128"
	image_id="updateDevice_image"
	"""

	# device_mount_point=UI max 255+1
	# result: ok
	"""
	device_id = "updateDevice_device1"
	device_name="updateDevice_device1"
	device_os="windows"
	device_fs="ntfs"
	write_permission="true"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point=mapi_util.random_str(256)
	device_key_size="128"
	image_id="updateDevice_image"
	"""

	# device_mount_point=nvarchar(max)
	# result: not doable, memory bound
	"""
	device_id = "updateDevice_device1"
	device_name="updateDevice_device1"
	device_os="windows"
	device_fs="ntfs"
	write_permission="true"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point=mapi_util.random_str(256)
	device_key_size="128"
	image_id="updateDevice_image"
	"""


	# device_mount_point=special chars
	# result: ok, but UI not allowed
	"""
	device_id = "updateDevice_device1"
	device_name="updateDevice_device1"
	device_os="windows"
	device_fs="ntfs"
	write_permission="true"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point=mapi_util.SPECIAL_CHARS
	device_key_size="128"
	image_id="updateDevice_image"
	"""


	# device_mount_point=special chars
	# result: ok, but UI not allowed
	"""
	device_id = "updateDevice_device1"
	device_name="updateDevice_device1"
	device_os="windows"
	device_fs="ntfs"
	write_permission="true"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point=mapi_util.SPECIAL_CHARS
	device_key_size="128"
	image_id="updateDevice_image"
	"""

	# device_key_size=""
	# result: HTTP Error 500: There is an error in XML document (1, 564).
	"""
	device_id = "updateDevice_device1"
	device_name="updateDevice_device1"
	device_os="windows"
	device_fs="ntfs"
	write_permission="true"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point="H"
	device_key_size=""
	image_id="updateDevice_image"
	"""

	# device_key_size="0"
	# result: ok, but ok?
	"""
	device_id = "updateDevice_device1"
	device_name="updateDevice_device1"
	device_os="windows"
	device_fs="ntfs"
	write_permission="true"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point="H"
	device_key_size="0"
	image_id="updateDevice_image"
	"""

	# device_key_size="-1"
	# result: ok, but ok?
	"""
	device_id = "updateDevice_device1"
	device_name="updateDevice_device1"
	device_os="windows"
	device_fs="ntfs"
	write_permission="true"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point="H"
	device_key_size="-1"
	image_id="updateDevice_image"
	"""


	# device_key_size= max int 2147483647
	# result: ok
	"""
	device_id = "updateDevice_device1"
	device_name="updateDevice_device1"
	device_os="windows"
	device_fs="ntfs"
	write_permission="true"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point="H"
	device_key_size="2147483647"
	image_id="updateDevice_image"
	"""


	# device_key_size= max int 2147483647+1
	# result: HTTP Error 500: There is an error in XML document (1, 574).
	"""
	device_id = "updateDevice_device1"
	device_name="updateDevice_device1"
	device_os="windows"
	device_fs="ntfs"
	write_permission="true"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point="H"
	device_key_size="2147483648"
	image_id="updateDevice_image"
	"""


	# device_key_size= non-integer
	# result: HTTP Error 500: There is an error in XML document (1, 574).
	"""
	device_id = "updateDevice_device1"
	device_name="updateDevice_device1"
	device_os="windows"
	device_fs="ntfs"
	write_permission="true"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point="H"
	device_key_size=mapi_util.random_str(10)
	image_id="updateDevice_image"
	"""

	# ok case
	# image_id="updateDevice_image"
	# result: HTTP Error 500: There is an error in XML document (1, 574).
	"""
	device_id = "updateDevice_device1"
	device_name="updateDevice_device1"
	device_os="windows"
	device_fs="ntfs"
	write_permission="true"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point="H"
	device_key_size="128"
	image_id="updateDevice_image"
	"""


	# image_id=non-existing image
	# result: ok, bug? the image should be check before updated
	"""
	device_id = "updateDevice_device1"
	device_name="updateDevice_device1"
	device_os="windows"
	device_fs="ntfs"
	write_permission="true"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point="H"
	device_key_size="128"
	image_id=mapi_util.random_str(20)
	"""


	# image_id=""
	# result: ok, image information wont be updated
	"""
	device_id = "updateDevice_device1"
	device_name="updateDevice_device1"
	device_os="windows"
	device_fs="ntfs"
	write_permission="true"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point="H"
	device_key_size="128"
	image_id=""
	"""


	print updateDevice(device_id, device_name, device_os, device_fs, write_permission, device_desc, device_mount_point, device_key_size, image_id)

	# key_mode="cbc"
	# result: ok
	"""
	device_id = "updateDevice_device1"
	device_name="updateDevice_device1"
	device_os="windows"
	device_fs="ntfs"
	write_permission="true"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point="H"
	device_key_size="128"
	image_id="updateDevice_image"
	key_mode="cbc"
	"""

	# key_mode="cfb"
	# result: ok
	"""
	device_id = "updateDevice_device1"
	device_name="updateDevice_device1"
	device_os="windows"
	device_fs="ntfs"
	write_permission="true"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point="H"
	device_key_size="128"
	image_id="updateDevice_image"
	key_mode="cfb"
	"""

	# key_mode="xts"
	# result: ok
	"""
	device_id = "updateDevice_device1"
	device_name="updateDevice_device1"
	device_os="windows"
	device_fs="ntfs"
	write_permission="true"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point="H"
	device_key_size="128"
	image_id="updateDevice_image"
	key_mode="xts"
	"""


	# key_mode=""
	# result: HTTP Error 500: There is an error in XML document (1, 551).
	"""
	device_id = "updateDevice_device1"
	device_name="updateDevice_device1"
	device_os="windows"
	device_fs="ntfs"
	write_permission="true"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point="H"
	device_key_size="128"
	image_id="updateDevice_image"
	key_mode=""
	"""

	# key_mode= random 20 chars
	# result: HTTP Error 500: There is an error in XML document (1, 571).
	"""
	device_id = "updateDevice_device1"
	device_name="updateDevice_device1"
	device_os="windows"
	device_fs="ntfs"
	write_permission="true"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point="H"
	device_key_size="128"
	image_id="updateDevice_image"
	key_mode= mapi_util.random_str(20)
	"""

	# key_mode= SPECIAL CHARS
	# result: HTTP Error 500: There is an error in XML document (1, 573).
	"""
	device_id = "updateDevice_device1"
	device_name="updateDevice_device1"
	device_os="windows"
	device_fs="ntfs"
	write_permission="true"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point="H"
	device_key_size="128"
	image_id="updateDevice_image"
	key_mode= mapi_util.SPECIAL_CHARS
	"""

	# key_mode= case sensitive
	# result: HTTP Error 500: There is an error in XML document (1, 554).
	"""
	device_id = "updateDevice_device1"
	device_name="updateDevice_device1"
	device_os="windows"
	device_fs="ntfs"
	write_permission="true"
	device_desc="this is updateDevice_device1 updated"
	device_mount_point="H"
	device_key_size="128"
	image_id="updateDevice_image"
	key_mode= "CBC"
	"""


	#print updateDevice(device_id, device_name, device_os, device_fs, write_permission, device_desc, device_mount_point, device_key_size, image_id, key_mode=key_mode)


	# ------------------------------------------------------


	# deleteDevice


	# empty device list
	# device_id = ""
	# HTTP Error 405: Method Not Allowed
	
	#returns http 400 bad request
	#device_id = "00000000-0000-0000-0000-000000000000"

	# 500 internal server error
	#device_id = "asdfasdfsdtfgdfg87d89fyaeao8sdfg79ay"

	# 500 internal server error
	#device_id = "asdfasdfsdtfgd"

	# HTTP Error 307: Temporary Redirect
	#device_id = mapi_util.SPECIAL_CHARS
	
	#print deleteDevice(device_id)


	# ------------------------------------------------------

	# original
	"""
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
	mount_point="/mnt/test_raid"
	key_size="128"
	"""


	# raid_name=""
	# result: HTTP Error 400: Bad Request
	"""
	raid_id="createRAID_raid"
	raid_name=""
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ext3"
	write_permission="true"
	raid_desc="this is test raid"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""

	# raid_name=random 1024
	# result: ok
	"""
	raid_id="createRAID_raid"
	raid_name=mapi_util.random_str(1024)
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ext3"
	write_permission="true"
	raid_desc="this is test raid"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""

	# raid_name=random 1024+1
	# result: ok, extra chars are truncated
	"""
	raid_id="createRAID_raid"
	raid_name=mapi_util.random_str(1025)
	print raid_name
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ext3"
	write_permission="true"
	raid_desc="this is test raid"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""


	# raid_name=special chars
	# result: HTTP Error 500: Whitespace must appear between attributes. Line 1, position 221.
	"""
	raid_id="createRAID_raid"
	raid_name=mapi_util.SPECIAL_CHARS
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ext3"
	write_permission="true"
	raid_desc="this is test raid"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""

	# raid_desc=""
	# result: ok
	"""
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
	raid_desc=""
	mount_point="/mnt/test_raid"
	key_size="128"
	"""

	# raid_desc=UI max 2000, try 2000
	# result: ok
	"""
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
	raid_desc=mapi_util.random_str(2000)
	mount_point="/mnt/test_raid"
	key_size="128"
	"""


	# raid_desc=UI max 2000, try 2001
	# result: ok
	"""
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
	raid_desc=mapi_util.random_str(2000)
	mount_point="/mnt/test_raid"
	key_size="128"
	"""


	# raid_desc=nvarchar(max), not-testable now
	# result: ??
	"""
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
	raid_desc=mapi_util.random_str(2000)
	mount_point="/mnt/test_raid"
	key_size="128"
	"""


	# raid_desc=special chars
	# result: ok
	"""
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
	raid_desc=mapi_util.SPECIAL_CHARS
	mount_point="/mnt/test_raid"
	key_size="128"
	"""

	# raid_level="RAID0"
	# result: ok
	"""
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
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""


	# raid_level="RAID1"
	# result: ok
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID1"
	raid_os="linux"
	raid_fs="ext3"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""

	# raid_level=""
	# result: HTTP Error 500: There is an error in XML document (1, 355).
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level=""
	raid_os="linux"
	raid_fs="ext3"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""

	# raid_level=""
	# result: HTTP Error 500: There is an error in XML document (1, 355).
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level=""
	raid_os="linux"
	raid_fs="ext3"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""

	# raid_level=random 20 chars
	# result: HTTP Error 500: There is an error in XML document (1, 375).
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level=mapi_util.random_str(20)
	raid_os="linux"
	raid_fs="ext3"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""

	# raid_level=special chars
	# result: HTTP Error 500: Whitespace must appear between attributes. Line 1, position 260.
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level=mapi_util.SPECIAL_CHARS
	raid_os="linux"
	raid_fs="ext3"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""


	# raid_level=raid0, case sensitive
	# result: HTTP Error 500: There is an error in XML document (1, 360).
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="raid0"
	raid_os="linux"
	raid_fs="ext3"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""
	


	# raid_os="linux"
	# result: ok
	"""
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
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""

	# raid_os="windows"
	# result: ok
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID0"
	raid_os="windows"
	raid_fs="ext3"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""
	
	# raid_os=""
	# result: HTTP Error 500: There is an error in XML document (1, 355).
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID0"
	raid_os=""
	raid_fs="ext3"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""

	# raid_os=random 20 chars
	# result: HTTP Error 500: There is an error in XML document (1, 375).
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID0"
	raid_os=mapi_util.random_str(20)
	raid_fs="ext3"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""

	# raid_os=special chars
	# result: HTTP Error 500: Whitespace must appear between attributes. Line 1, position 272.
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID0"
	raid_os=mapi_util.SPECIAL_CHARS
	raid_fs="ext3"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""


	# raid_os=LINUX, case sensitive
	# result: HTTP Error 500: There is an error in XML document (1, 360).
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID0"
	raid_os="LINUX"
	raid_fs="ext3"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""

	# raid_fs="ext3"
	# result: ok
	"""
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
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""

	# raid_fs="ntfs"
	# result: ok
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""

	# raid_fs="xfs"
	# result: ok
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="xfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""

	# raid_fs="fat32"
	# result: ok
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="fat32"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""


	# raid_fs=""
	# result: HTTP Error 500: There is an error in XML document (1, 356).
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs=""
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""
	

	# raid_fs=random 20 chars
	# result: HTTP Error 500: There is an error in XML document (1, 376).
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs=mapi_util.random_str(20)
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""


	# raid_fs=special chars
	# result: HTTP Error 500: Whitespace must appear between attributes. Line 1, position 284.
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs=mapi_util.SPECIAL_CHARS
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""

	# raid_fs=NTFS, case sensitive
	# result: HTTP Error 500: There is an error in XML document (1, 360).
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="NTFS"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""


	# write_permission="true"
	# result: ok
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""


	# write_permission="false"
	# result: ok
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="false"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""


	# write_permission=""
	# result: HTTP Error 500: There is an error in XML document (1, 356).
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission=""
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""

	# write_permission="1"
	# result: ok
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="1"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""

	# write_permission="0"
	# result: ok
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="0"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""

	# write_permission=non-integer test
	# result: HTTP Error 500: There is an error in XML document (1, 357).
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="a"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""
	
	# write_permission=TRUE, case sensitive test
	# result: HTTP Error 500: There is an error in XML document (1, 360).
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="TRUE"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""


	# orginal mount
	# mount_point="/mnt/test_raid"
	# result: ok
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""

	# mount_point=""
	# result: HTTP Error 400: Bad Request
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point=""
	key_size="128"
	"""

	# mount_point=UI max 255, try 255
	# result: ok
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point=mapi_util.random_str(255)
	key_size="128"
	"""

	# mount_point=UI max 255, try 256
	# result: ok
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point=mapi_util.random_str(256)
	key_size="128"
	"""


	# mount_point=nvarchar(max), un-testable
	# result: ??
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point=mapi_util.random_str(256)
	key_size="128"
	"""


	# mount_point=special chars
	# result: ok but bug, UI not allowed
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point=mapi_util.SPECIAL_CHARS
	key_size="128"
	"""


	# key_size="128"
	# result: ok
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test"
	key_size="128"
	"""


	# key_size=""
	# result: HTTP Error 500: There is an error in XML document (1, 696).
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test"
	key_size=""
	"""

	# key_size="0"
	# result: HTTP Error 400: Bad Request
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test"
	key_size="0"
	"""


	# key_size="-1"
	# result: HTTP Error 400: Bad Request
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test"
	key_size="-1"
	"""

	# key_size=max int
	# result: HTTP Error 400: Bad Request
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test"
	key_size=mapi_util.MAX_INT
	"""
	

	# key_size=allowed int = 128/192/384/256/512
	# result: ok
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test"
	key_size="128"
	"""
	

	# provider=""
	# result: HTTP Error 400: Bad Request
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider=""
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test"
	key_size="512"
	"""

	# provider=non-existing provider
	# result: will create a new csp but the dropdown won't show the csp
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider=mapi_util.random_str(10)
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test"
	key_size="512"
	"""

	# provider=special chars
	# result: HTTP Error 500: There is an error in XML document (1, 587).
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider=mapi_util.SPECIAL_CHARS
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test"
	key_size="512"
	"""
	

	# provider_zone=""
	# result: HTTP Error 400: Bad Request
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone=""
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test"
	key_size="512"
	"""


	# provider_zone=non-existing zone
	# result: ok, zone is created and show on the all-device page but in the edit page, it won't be shown in the dropdown
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone=mapi_util.random_str(20)
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test"
	key_size="512"
	"""

	# provider_zone=max zone in db=1024
	# result: ok
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone=mapi_util.random_str(1024)
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test"
	key_size="512"
	"""

	# provider_zone=max zone in db=1024+1
	# result: ok, extra chars are truncated
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone=mapi_util.random_str(1025)
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test"
	key_size="512"
	"""


	# image_id=""
	# result: ok, bug, UI cannot be empty
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider="createRAID_csp"
	image_id=""
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test"
	key_size="512"
	"""

	# image_id=non-existing image
	# result: HTTP Error 400: Bad Request
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider="createRAID_csp"
	image_id=mapi_util.random_str(10)
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test"
	key_size="512"
	"""


	# device_id_list = 0 device
	# result: HTTP Error 400: Bad Request
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = None
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test"
	key_size="512"
	"""

	#print createRAID(raid_id, raid_name, raid_level, raid_os, raid_fs, write_permission, provider_zone, device_id_list, raid_desc, provider, image_id, mount_point, key_size)

	# device_id_list = 2 non-existing devices
	# result: HTTP Error 400: Bad Request
	"""
	raid_id="createRAID_raid"
	raid_name="createRAID_raid"
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["00000000-0000-0000-0000-000000000001", "00000000-0000-0000-0000-000000000002"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test"
	key_size="512"
	"""
	#print createRAID(raid_id, raid_name, raid_level, raid_os, raid_fs, write_permission, provider_zone, device_id_list, raid_desc, provider, image_id, mount_point, key_size, test_non_existing_devices=True)



	# ------------------------------------------------------

	#raid_id = ""
	# HTTP Error 500: Internal Server Error
	
	#raid_id = "00000000-0000-0000-0000-000000000000"
	#returns http 400 bad request

	#raid_id = "asdfasdfsdtfgdfg87d89fyaeao8sdfg79ay"
	# 500 internal server error

	#raid_id = "asdfasdfsdtfgd"
	# 500 internal server error
	
	#raid_id = mapi_util.SPECIAL_CHARS
	# HTTP Error 401: Unauthorized
	
	#print readRAID(raid_id)

	# ------------------------------------------------------

	#original
	"""
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
	"""

	# raid_name=""
	# result: "" empty name is not updated
	"""
	raid_id="updateRAID_raid"
	raid_name=""
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ext3"
	write_permission="true"
	raid_desc="this is test raid"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""


	# raid_name=random 1024
	# result: ok
	"""
	raid_id="updateRAID_raid"
	raid_name=mapi_util.random_str(1024)
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ext3"
	write_permission="true"
	raid_desc="this is test raid"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""



	# raid_name=random 1024+1
	# result: ok, extra chars are truncated
	"""
	raid_id="updateRAID_raid"
	raid_name=mapi_util.random_str(1025)
	print raid_name
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ext3"
	write_permission="true"
	raid_desc="this is test raid"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""


	# raid_name=special chars
	# result: HTTP Error 500: Whitespace must appear between attributes. Line 1, position 221.
	"""
	raid_id="updateRAID_raid"
	raid_name=mapi_util.SPECIAL_CHARS
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ext3"
	write_permission="true"
	raid_desc="this is test raid"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""



	# raid_desc=""
	# result: ok
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ext3"
	write_permission="true"
	raid_desc=""
	mount_point="/mnt/test_raid"
	key_size="128"
	"""


	# raid_desc=UI max 2000, try 2000
	# result: ok
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ext3"
	write_permission="true"
	raid_desc=mapi_util.random_str(2000)
	mount_point="/mnt/test_raid"
	key_size="128"
	"""


	# raid_desc=UI max 2000, try 2001
	# result: ok
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ext3"
	write_permission="true"
	raid_desc=mapi_util.random_str(2000)
	mount_point="/mnt/test_raid"
	key_size="128"
	"""



	# raid_desc=nvarchar(max), not-testable now
	# result: ??
	"""
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
	raid_desc=mapi_util.random_str(2000)
	mount_point="/mnt/test_raid"
	key_size="128"
	"""


	# raid_desc=special chars
	# result: ok
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ext3"
	write_permission="true"
	raid_desc=mapi_util.SPECIAL_CHARS
	mount_point="/mnt/test_raid"
	key_size="128"
	"""



	# raid_level="RAID0"
	# result: ok
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ext3"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""



	# raid_level="RAID1"
	# result: ok
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID1"
	raid_os="linux"
	raid_fs="ext3"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""



	# raid_level=""
	# result: HTTP Error 500: There is an error in XML document (1, 355).
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level=""
	raid_os="linux"
	raid_fs="ext3"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""



	# raid_level=""
	# result: HTTP Error 500: There is an error in XML document (1, 355).
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level=""
	raid_os="linux"
	raid_fs="ext3"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""



	# raid_level=random 20 chars
	# result: HTTP Error 500: There is an error in XML document (1, 375).
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level=mapi_util.random_str(20)
	raid_os="linux"
	raid_fs="ext3"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""



	# raid_level=special chars
	# result: HTTP Error 500: Whitespace must appear between attributes. Line 1, position 260.
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level=mapi_util.SPECIAL_CHARS
	raid_os="linux"
	raid_fs="ext3"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""



	# raid_level=raid0, case sensitive
	# result: HTTP Error 500: There is an error in XML document (1, 360).
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="raid0"
	raid_os="linux"
	raid_fs="ext3"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""
	

	# raid_os="linux"
	# result: ok
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ext3"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""


	# raid_os="windows"
	# result: ok
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="windows"
	raid_fs="ext3"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""




	# raid_os=""
	# result: HTTP Error 500: There is an error in XML document (1, 355).
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os=""
	raid_fs="ext3"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""


	# raid_os=random 20 chars
	# result: HTTP Error 500: There is an error in XML document (1, 375).
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os=mapi_util.random_str(20)
	raid_fs="ext3"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""



	# raid_os=special chars
	# result: HTTP Error 500: Whitespace must appear between attributes. Line 1, position 272.
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os=mapi_util.SPECIAL_CHARS
	raid_fs="ext3"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""


	# raid_os=LINUX, case sensitive
	# result: HTTP Error 500: There is an error in XML document (1, 360).
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="LINUX"
	raid_fs="ext3"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""


	# raid_fs="ext3"
	# result: ok
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ext3"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""



	# raid_fs="ntfs"
	# result: ok
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""



	# raid_fs="xfs"
	# result: ok
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="xfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""



	# raid_fs="fat32"
	# result: ok
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="fat32"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""



	# raid_fs=""
	# result: HTTP Error 500: There is an error in XML document (1, 356).
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs=""
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""




	# raid_fs=random 20 chars
	# result: HTTP Error 500: There is an error in XML document (1, 376).
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs=mapi_util.random_str(20)
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""

	

	# raid_fs=special chars
	# result: HTTP Error 500: Whitespace must appear between attributes. Line 1, position 284.
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs=mapi_util.SPECIAL_CHARS
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""




	# raid_fs=NTFS, case sensitive
	# result: HTTP Error 500: There is an error in XML document (1, 360).
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="NTFS"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""



	# write_permission="true"
	# result: ok
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""


	# write_permission="false"
	# result: ok
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="false"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""


	# write_permission=""
	# result: HTTP Error 500: There is an error in XML document (1, 356).
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission=""
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""


	# write_permission="1"
	# result: ok
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="1"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""

	
	# write_permission="0"
	# result: ok
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="0"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""


	# write_permission=non-integer test
	# result: HTTP Error 500: There is an error in XML document (1, 357).
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="createRAID_csp"
	image_id="createRAID_image"
	provider_zone="createRAID_zone"
	device_id_list = ["createRAID_device1","createRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="a"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""

	
	# write_permission=TRUE, case sensitive test
	# result: HTTP Error 500: There is an error in XML document (1, 360).
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="TRUE"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""



	# orginal mount
	# mount_point="/mnt/test_raid"
	# result: ok
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test_raid"
	key_size="128"
	"""


	# mount_point=""
	# result: ok, empty mount is not updated
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point=""
	key_size="128"
	"""


	# mount_point=UI max 255, try 255
	# result: ok
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point=mapi_util.random_str(255)
	key_size="128"
	"""


	# mount_point=UI max 255, try 256
	# result: ok
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point=mapi_util.random_str(256)
	key_size="128"
	"""

	

	# mount_point=nvarchar(max), un-testable
	# result: ??
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point=mapi_util.random_str(256)
	key_size="128"
	"""


	# mount_point=special chars
	# result: ok but bug, UI not allowed
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point=mapi_util.SPECIAL_CHARS
	key_size="128"
	"""


	# key_size="128"
	# result: ok
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test"
	key_size="128"
	"""


	# key_size=""
	# result: HTTP Error 500: There is an error in XML document (1, 696).
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test"
	key_size=""
	"""

	
	# key_size="0"
	# result: ok, bug
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test"
	key_size="0"
	"""


	# key_size="-1"
	# result: ok, but whole keygen tag is gone
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test"
	key_size="-1"
	"""

	
	# key_size=max int
	# result: ok, bug?
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test"
	key_size=mapi_util.MAX_INT
	"""


	# key_size=max int+1
	# result: HTTP Error 500: There is an error in XML document (1, 706).
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test"
	key_size=mapi_util.MAX_INT_PLUS_1
	"""
	

	# key_size=can be any int
	# result: ok, ?
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test"
	key_size="7788"
	"""



	# provider=""
	# result: ok, empty provider is not updated
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider=""
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test"
	key_size="512"
	"""



	# provider=non-existing provider
	# result: ok, bug? should check existing first?
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider=mapi_util.random_str(10)
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test"
	key_size="512"
	"""



	# provider=special chars
	# result: HTTP Error 500: There is an error in XML document (1, 587).
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider=mapi_util.SPECIAL_CHARS
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test"
	key_size="512"
	"""
	


	# provider_zone=""
	# result: ok, empty provider zone is not updated
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone=""
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test"
	key_size="512"
	"""


	# provider_zone=non-existing zone
	# result: ok, bug should check existing or not?
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone=mapi_util.random_str(20)
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test"
	key_size="512"
	"""


	# provider_zone=max zone in db=1024
	# result: ok
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone=mapi_util.random_str(1024)
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test"
	key_size="512"
	"""



	# provider_zone=max zone in db=1024+1
	# result: ok, extra chars are truncated
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone=mapi_util.random_str(1025)
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test"
	key_size="512"
	"""



	# image_id=""
	# result: ok, empty image id is not updated
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id=""
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test"
	key_size="512"
	"""



	# image_id=non-existing image
	# result: ok, bug, should check first?
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id=mapi_util.random_str(10)
	provider_zone="updateRAID_zone"
	device_id_list = ["updateRAID_device1","updateRAID_device2"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test"
	key_size="512"
	"""



	# device_id_list = 0 device
	# result: ok, empty device list is not updated
	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = None
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test"
	key_size="512"
	"""


	# device_id_list = 2 non-existing devices
	# result: HTTP Error 400: Bad Request

	"""
	raid_id="updateRAID_raid"
	raid_name="updateRAID_raid"
	provider="updateRAID_csp"
	image_id="updateRAID_image"
	provider_zone="updateRAID_zone"
	device_id_list = ["00000000-0000-0000-0000-000000000001", "00000000-0000-0000-0000-000000000002"]
	raid_level="RAID0"
	raid_os="linux"
	raid_fs="ntfs"
	write_permission="true"
	raid_desc="create RAID description"
	mount_point="/mnt/test"
	key_size="512"
	"""
	
	#print updateRAID(raid_id, raid_name, raid_level, raid_os, raid_fs, write_permission, provider_zone, device_id_list, raid_desc, provider, image_id, mount_point, key_size, test_non_existing_devices=True)


	# ------------------------------------------------------

	# RAT case
	device_id = "encryptDevice_device1"
	#print encryptDevice(device_id, True)

	# device_id = ""
	# result: fail,HTTP Error 400: Bad Request
	device_id = ""
	#print encryptDevice(device_id)

	# device_id = "00000000-0000-0000-0000-000000000000"
	# result: fail,HTTP Error 400: Bad Request
	device_id = "00000000-0000-0000-0000-000000000000"
	#print encryptDevice(device_id)

	# device_id = "asdfasdfsdtfgdfg87d89fyaeao8sdfg79ay"
	# result: fail,HTTP Error 500: Internal Server Error
	device_id = "asdfasdfsdtfgdfg87d89fyaeao8sdfg79ay"
	#print encryptDevice(device_id)
	
	# device_id = mapi_util.SPECIAL_CHARS
	# result: fail,HTTP Error 307: Temporary Redirect
	device_id = mapi_util.SPECIAL_CHARS
	#print encryptDevice(device_id)

	# provision_state = ""
	# result:pass, device is not provisioned
	device_id = "encryptDevice_device1"
	provision_state = ""
	#print encryptDevice(device_id, True, provision_state)

	# provision_state = random 10 chars
	# result:pass, bug should only allow "pending"
	device_id = "encryptDevice_device1"
	provision_state = mapi_util.random_str(10)
	#print encryptDevice(device_id, True, provision_state)

	# provision_state = special chars
	# result:fail,HTTP Error 500: Whitespace must appear between attributes. Line 1, position 207.
	device_id = "encryptDevice_device1"
	provision_state = mapi_util.SPECIAL_CHARS
	#print encryptDevice(device_id, True, provision_state)



	# ------------------------------------------------------

	# RAT case
	raid_id = "deleteRAID_id"
	#print deleteRAID(raid_id, True)

	# raid_id = ""
	# result: fail,HTTP Error 500: Internal Server Error
	raid_id = ""
	#print deleteRAID(raid_id)

	# raid_id = "00000000-0000-0000-0000-000000000000"
	# result: fail,HTTP Error 400: Bad Request
	raid_id = "00000000-0000-0000-0000-000000000000"
	#print deleteRAID(raid_id)

	# raid_id = "asdfasdfsdtfgdfg87d89fyaeao8sdfg79ay"
	# result: fail,HTTP Error 500: Internal Server Error
	raid_id = "asdfasdfsdtfgdfg87d89fyaeao8sdfg79ay"
	#print deleteRAID(raid_id)
	
	# raid_id = mapi_util.SPECIAL_CHARS
	# result: fail,HTTP Error 307: Temporary Redirect
	raid_id = mapi_util.SPECIAL_CHARS
	#print deleteRAID(raid_id)


	# ------------------------------------------------------

	# RAT
	raid_id = "encryptRAID_id"
	#print encryptRAID(raid_id, True)

	# raid_id = ""
	# result: fail,HTTP Error 400: Bad Request
	raid_id = ""
	#print encryptRAID(raid_id)

	# raid_id = "00000000-0000-0000-0000-000000000000"
	# result: fail,HTTP Error 400: Bad Request
	raid_id = "00000000-0000-0000-0000-000000000000"
	# print encryptRAID(raid_id)

	# raid_id = "asdfasdfsdtfgdfg87d89fyaeao8sdfg79ay"
	# result: fail,HTTP Error 500: Internal Server Error
	raid_id = "asdfasdfsdtfgdfg87d89fyaeao8sdfg79ay"
	#print encryptRAID(raid_id)
	
	# raid_id = mapi_util.SPECIAL_CHARS
	# result: fail,HTTP Error 307: Temporary Redirect
	raid_id = mapi_util.SPECIAL_CHARS
	#print encryptRAID(raid_id)

	# provision_state = ""
	# result:pass, device is not provisioned
	raid_id = "encryptRAID_id"
	provision_state = ""
	#print encryptRAID(raid_id, True, provision_state)

	# provision_state = random 10 chars
	# result:pass, bug should only allow "pending"
	raid_id = "encryptRAID_id"
	provision_state = mapi_util.random_str(10)
	#print encryptRAID(raid_id, True, provision_state)

	# provision_state = special chars
	# result:fail,HTTP Error 500: Whitespace must appear between attributes. Line 1, position 207.
	raid_id = "encryptRAID_id"
	provision_state = mapi_util.SPECIAL_CHARS
	#print encryptRAID(raid_id, True, provision_state)


	# ------------------------------------------------------

	# RAT
	"""
	from_device_id = "cloneDevice_device_2_1"
	to_device_id = "cloneDevice_device_2_2"
	existing_from_device = True
	existing_to_device = True
	print cloneDevice(from_device_id, to_device_id, existing_from_device, existing_to_device)
	"""

	# from_device_id = ""
	# result:fail,HTTP Error 400: Bad Request
	"""
	from_device_id = ""
	to_device_id = "cloneDevice_device_2_2"
	existing_from_device = False
	existing_to_device = True
	print cloneDevice(from_device_id, to_device_id, existing_from_device, existing_to_device)
	"""

	# from_device_id = "00000000-0000-0000-0000-000000000000"
	# result:fail,HTTP Error 400: Bad Request
	"""
	from_device_id = "00000000-0000-0000-0000-000000000000"
	to_device_id = "cloneDevice_device_2_2"
	existing_from_device = False
	existing_to_device = True
	print cloneDevice(from_device_id, to_device_id, existing_from_device, existing_to_device)
	"""

	# from_device_id = "asdfasdfsdtfgdfg87d89fyaeao8sdfg79ay"
	# result:fail,HTTP Error 500: Internal Server Error
	"""
	from_device_id = "asdfasdfsdtfgdfg87d89fyaeao8sdfg79ay"
	to_device_id = "cloneDevice_device_2_2"
	existing_from_device = False
	existing_to_device = True
	print cloneDevice(from_device_id, to_device_id, existing_from_device, existing_to_device)
	"""

	# from_device_id = mapi_util.SPECIAL_CHARS
	# result:fail,HTTP Error 307: Temporary Redirect
	"""
	from_device_id = mapi_util.SPECIAL_CHARS
	to_device_id = "cloneDevice_device_2_2"
	existing_from_device = False
	existing_to_device = True
	print cloneDevice(from_device_id, to_device_id, existing_from_device, existing_to_device)
	"""

	# to_device_id = ""
	# result:fail,HTTP Error 500: Internal Server Error
	"""
	from_device_id = "cloneDevice_device_2_1"
	to_device_id = ""
	existing_from_device = True
	existing_to_device = False
	print cloneDevice(from_device_id, to_device_id, existing_from_device, existing_to_device)
	"""

	# to_device_id = "00000000-0000-0000-0000-000000000000"
	# result:fail,HTTP Error 400: Bad Request
	"""
	from_device_id = "cloneDevice_device_2_1"
	to_device_id = "00000000-0000-0000-0000-000000000000"
	existing_from_device = True
	existing_to_device = False
	print cloneDevice(from_device_id, to_device_id, existing_from_device, existing_to_device)
	"""

	# to_device_id = "asdfasdfsdtfgdfg87d89fyaeao8sdfg79ay"
	# result:fail,HTTP Error 500: Internal Server Error
	"""
	from_device_id = "cloneDevice_device_2_1"
	to_device_id = "asdfasdfsdtfgdfg87d89fyaeao8sdfg79ay"
	existing_from_device = True
	existing_to_device = False
	print cloneDevice(from_device_id, to_device_id, existing_from_device, existing_to_device)
	"""

	# to_device_id = mapi_util.SPECIAL_CHARS
	# result:fail,HTTP Error 500: Whitespace must appear between attributes. Line 1, position 153.
	"""
	from_device_id = "cloneDevice_device_2_1"
	to_device_id = mapi_util.SPECIAL_CHARS
	existing_from_device = True
	existing_to_device = False
	print cloneDevice(from_device_id, to_device_id, existing_from_device, existing_to_device)
	"""


	# ------------------------------------------------------

	# RAT
	#passphrase = "P@ssw0rd"
	#print exportDevice(passphrase)

	# passphrase = ""
	# result:pass, bug, passphrase should not be empty
	passphrase = ""
	#print exportDevice(passphrase)

	"""
	[The passphrase should be 8 to 32 characters, containing at least one of the following:
	upper case, lower case, numeral, and special character (~!@#$%^&*()_+).]
	"""

	# passphrase = "aA1@"
	# result:pass, bug, should be at least 8 chars
	passphrase = "aA1@"
	#print exportDevice(passphrase)

	# passphrase = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaA1@"
	# result:pass, bug, should not exceed 32 chars
	passphrase = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaA1@"
	#print exportDevice(passphrase)

	# passphrase = "1A@@@@@@"
	# result:pass, bug, should contain lower case
	passphrase = "1A@@@@@@"
	#print exportDevice(passphrase)

	# passphrase = "1a@@@@@@"
	# result:pass, bug, shoudd contain upper case
	passphrase = "1a@@@@@@"
	#print exportDevice(passphrase)

	# passphrase = "aA@@@@@@"
	# result:pass, bug, should contain number
	passphrase = "aA@@@@@@"
	#print exportDevice(passphrase)

	# passphrase = "123456aA"
	# result:pass, bug, should contain special char
	passphrase = "123456aA"
	#print exportDevice(passphrase)



	# ------------------------------------------------------
	print cross_accounts_view_test()
























