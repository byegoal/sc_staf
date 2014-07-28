import os
import re
import time
import logging
import platform
import ConfigParser
import shutil
import subprocess
import xml
import re
import socket
import sys
from subprocess import Popen, PIPE
from urllib2 import urlopen, HTTPError, URLError
from xml.dom import minidom
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import Element

import secureCloud.agentBVT.util

try:
    from win32con import NULL
except ImportError, e:
    logging.debug("import win32con fail: %s" % e)
try:
    import secureCloud.managementAPI.mapi_lib
except ImportError, e:
    logging.debug("import mapi_lib fail: %s" % e)

import secureCloud.config.result_config
import secureCloud.scAgent.file
log_path = secureCloud.config.result_config.result_path
chefLogger = secureCloud.config.result_config.chefLogger
stafLogger = secureCloud.config.result_config.stafLogger
errorLogger = secureCloud.config.result_config.errorLogger
    
#TODO: pass credential to mapi, and credential should read from product.ini
def write_report(path,msg):
        f = file(path+'result.log', 'r') # open for 'w'riting
        line = f.readline()
        f.close()
        if line== "":
            poem = ''' ------Test Result------ \n'''
            f = file(path+'result.log', 'w') # open for 'w'riting
            f.write(poem) # write text to file
            f.close() # close the file
        f = file(path+'result.log', 'a') # open for 'w'riting
        f.write(msg)
        f.write('\n')
         # write text to file
        f.close() # close the file
    
def get_vm_guid(vm_name, retry=30):
    x = secureCloud.managementAPI.mapi_lib.mapi_lib(auth_type="api_auth")
    xml_result = x.listVM()


    count = 0
    while (not xml_result) and count < retry:
        time.sleep(90)
        count += 1
        xml_result = x.listVM()


    vm_list = xml_result.getElementsByTagName("vmList")[0]
    vms = vm_list.getElementsByTagName("vms")[0]
    all_vm = vms.getElementsByTagName("vm")
    current = None
    for vm in all_vm:
        current_vm_name = vm.attributes["imageName"].value.strip()
        last_modified = vm.attributes["lastModified"].value.strip()
        vm_guid = vm.attributes["imageGUID"].value.strip()

        logging.debug("current %s, %s, %s" % (current_vm_name, last_modified, vm_guid))

        if current_vm_name == vm_name:
            if current == None:
                current = {"guid": vm_guid, "last_modified": last_modified}
                print current
            else:
                if(last_modified > current["last_modified"]):
                    current["guid"] = vm_guid
                    current["last_modified"] = last_modified
                    print current

    if current == None:
        return False
    else:
        return current["guid"]


def get_device_guid(vm_name, device_name, retry = 60):
    x = secureCloud.managementAPI.mapi_lib.mapi_lib(auth_type="api_auth")
    vm_guid = get_vm_guid(vm_name)
    if vm_guid == False:
        logging.debug("cannot find vm GUID")
        return 1
    logging.debug("vm guid:" + vm_guid)

    count = 0
    while(count < retry):
        xml_result = x.readVM(vm_guid)

        vm_node = xml_result.getElementsByTagName("vm")[0]
        devices_node = vm_node.getElementsByTagName("devices")[0]
        devices = devices_node.getElementsByTagName("device")
        for device in devices:
            current_device = device.attributes["name"].value.strip()
            current_msuid = device.attributes["msUID"].value.strip()
            logging.debug("current device:%s" % (current_device))
            if device_name == current_device:
                return current_msuid

        time.sleep(10)
        count += 1

    return False
def get_device_guid_from_server(server_vm_guid, device_name, retry = 60):
    x = secureCloud.managementAPI.mapi_lib.mapi_lib(auth_type="api_auth")
    count = 0
    while(count < retry):
        xml_result = x.readVM(server_vm_guid)

        vm_node = xml_result.getElementsByTagName("vm")[0]
        devices_node = vm_node.getElementsByTagName("devices")[0]
        devices = devices_node.getElementsByTagName("device")
        for device in devices:
            current_device = device.attributes["name"].value.strip()
            current_msuid = device.attributes["msUID"].value.strip()
            logging.debug("current device:%s" % (current_device))
            if device_name == current_device:
                stafLogger.debug("server_vm_guid:%s, device_msuid:%s\n"%(server_vm_guid,current_msuid))
                return current_msuid

        time.sleep(10)
        count += 1

    return False
def check_device_existing(vm_name, device_name, check_mount=True, retry=60):
    x = secureCloud.managementAPI.mapi_lib.mapi_lib(auth_type="api_auth")
    vm_guid = get_vm_guid(vm_name)
    if vm_guid == False:
        logging.debug("cannot find vm GUID")
        return 1
    logging.debug("vm guid:" + vm_guid)

    count = 0
    while(count < retry):
        xml_result = x.readVM(vm_guid)

        vm_node = xml_result.getElementsByTagName("vm")[0]
        devices_node = vm_node.getElementsByTagName("devices")[0]
        devices = devices_node.getElementsByTagName("device")
        for device in devices:
            current_device = device.attributes["name"].value.strip()
            logging.debug("current device:%s" % (current_device))

            if check_mount:
                #partitionlist_node = device.getElementsByTagName("partitionList")[0]
                #partition_node = partitionlist_node.getElementsByTagName("partition")[0]
                volume_node = device.getElementsByTagName("volume")[0]
                mountPoint_node = volume_node.getElementsByTagName("mountPoint")[0]
                current_mount_point = secureCloud.managementAPI.mapi_util.getText(mountPoint_node)
                logging.debug("current mount point:%s" % (current_mount_point))
                if device_name == current_device and current_mount_point:
                    logging.debug("current device:%s is found" % (current_device))
                    return 0
            else:
                if device_name == current_device:
                    logging.debug("current device:%s is found" % (current_device))
                    return 0

        time.sleep(10)
        count += 1

    logging.debug("current device:%s is not found" % (current_device))
    return 1


def check_device_encrypted(vm_name, device_name, retry=60):
    x = secureCloud.managementAPI.mapi_lib.mapi_lib(auth_type="api_auth")
    vm_guid = get_vm_guid(vm_name)
    if vm_guid == False:
        logging.debug("cannot find vm GUID")
        return 1
    logging.debug("vm guid:" + vm_guid)

    count = 0
    while (count < retry):
        xml_result = x.readVM(vm_guid)

        vm_node = xml_result.getElementsByTagName("vm")[0]
        devices_node = vm_node.getElementsByTagName("devices")[0]
        devices = devices_node.getElementsByTagName("device")
        for device in devices:
            current_device = device.attributes["name"].value.strip()
            current_msuid = device.attributes["msUID"].value.strip()
            logging.debug("current device:%s" % (current_device))
            logging.debug("current device msuid :%s" % (current_msuid))
            if device_name == current_device:
                current_status = device.attributes["deviceStatus"].value.strip()
                if  current_status == "Encrypted":
                    return 0
                # else:
                #	return 1

        time.sleep(10)
        count += 1
    return 1
def check_list_vm(access_key_id,secret_access_key):
    x = secureCloud.managementAPI.mapi_lib.mapi_lib(auth_type="api_auth")
    xml_result = x.listVM()

    return xml_result
def check_device_encrypted_by_device_guid(server_vm_guid, device_guid, sc_path,retry=60):
    count = 0
    x = secureCloud.managementAPI.mapi_lib.mapi_lib(auth_type="api_auth")
    while (count < retry):
        xml_result = x.readVM(server_vm_guid)
        stafLogger.debug("check_device_encrypted_by_device_guid xml_result=%s"%str(xml_result))
        vm_node = xml_result.getElementsByTagName("vm")[0]
        devices_node = vm_node.getElementsByTagName("devices")[0]
        devices = devices_node.getElementsByTagName("device")
        for device in devices:
            current_device = device.attributes["name"].value.strip()
            current_msuid = device.attributes["msUID"].value.strip()
            logging.debug("current device:%s" % (current_device))
            logging.debug("current device msuid :%s" % (current_msuid))
            if device_guid == current_msuid:
                current_status = device.attributes["deviceStatus"].value.strip()
                stafLogger.debug("device_name:%s, device_msUID:%s, deviceStatus:%s\n"%(current_device,current_msuid,current_status))
                if  current_status == "Encrypted":
                    return 0
                # else:
                #    return 1

        time.sleep(10)
        count += 1
    return 1


def check_device_not_encrypted_server(access_key_id,secret_access_key,server_vm_guid, device_msuid, retry=5):
    x = secureCloud.managementAPI.mapi_lib.mapi_lib(auth_type="api_auth")
    count = 0
    while (count < retry):
        xml_result = x.readVM(server_vm_guid)
        vm_node = xml_result.getElementsByTagName("vm")[0]
        devices_node = vm_node.getElementsByTagName("devices")[0]
        devices = devices_node.getElementsByTagName("device")
        for device in devices:
            current_device = device.attributes["name"].value.strip()
            current_msuid = device.attributes["msUID"].value.strip()
            if current_msuid == device_msuid:
                current_status = device.attributes["deviceStatus"].value.strip()
                if  current_status == "Configured":
                    return 0
                else:
                    errorLogger.error("current device:%s, deviceStatus:%s\n" % (current_device,current_status)) 
                
                # else:
                #    return 1
        time.sleep(10)
        count += 1
    return 1
def check_device_encrypted_by_device_guid(access_key_id,secret_access_key,sc_path, device_guid, retry=60):

    if device_guid == False:
        logging.debug("cannot find boot_device_guid")
        return 1
    agent_vmGuid = get_agent_vmGuid(sc_path)
    logging.debug("agent_vm_guid: %s \n"%agent_vmGuid)
    if agent_vmGuid == False:
        logging.debug("cannot find agent_vmGuid")
        return 1
    x = secureCloud.managementAPI.mapi_lib.mapi_lib(auth_type="api_auth")
    server_vmGuid = get_server_vmGuid_by_agent_vmGuid(agent_vmGuid)
    logging.debug("server_vm_guid: %s \n"%server_vmGuid)
    if server_vmGuid == False:
        logging.debug("cannot find server_vmGuid")
        return 1
    count = 0
    while (count < retry):
        xml_result = x.readVM(server_vmGuid)

        vm_node = xml_result.getElementsByTagName("vm")[0]
        devices_node = vm_node.getElementsByTagName("devices")[0]
        devices = devices_node.getElementsByTagName("device")
        for device in devices:
            current_device = device.attributes["name"].value.strip()
            current_msuid = device.attributes["msUID"].value.strip()
            logging.debug("current device:%s" % (current_device))
            logging.debug("current device msuid :%s" % (current_msuid))
            if device_guid == current_msuid:
                current_status = device.attributes["deviceStatus"].value.strip()
                if  current_status == "Encrypted":
                    return 0
                # else:
                #    return 1

        time.sleep(10)
        count += 1
    return 1


def agent_config_xml_data(sc_path):
        xmldata = minidom.parse('%sconfig.xml'% (sc_path))
        return xmldata
    
def update_agent_config_for_userScript(sc_path,type,sh_file):
    tree=ET.parse('%s/config.xml'% (sc_path))
    root = tree.getroot()
    agent = root.find('agent')
    userScripts=agent.find('userScripts')
    if type=='teardown':
        userScripts.set('teardown',sh_file)
    else:
        userScripts.set('mountComplete', sh_file)
    tree = ET.ElementTree(root)
    tree.write('%s/config.xml'% (sc_path))
    return 0
   
def get_csp_id(sc_path):
    config_xml_data= agent_config_xml_data(sc_path)
    root_node = config_xml_data.getElementsByTagName("secureCloud")[0]
    csp_node = root_node.getElementsByTagName("csp")[0]
    csp_id = csp_node.attributes['id'].value.strip()
    return csp_id

def get_boot_device_guid(sc_path):
    boot_device_guid=None
    config_xml_data= agent_config_xml_data(sc_path)
    root_node = config_xml_data.getElementsByTagName("secureCloud")[0]
    agent_node = root_node.getElementsByTagName("agent")[0]
    devices = agent_node.getElementsByTagName("devices")[0]
    devices_node = devices.getElementsByTagName("device")
    for device in devices_node:
        
        if device.attributes["diskType"].value.strip()=='root':
           boot_device_guid = device.attributes["guid"].value.strip()         
    
    return boot_device_guid

def get_agent_vmGuid(sc_path):
    agent_vmGuid = None
    config_xml_data= agent_config_xml_data(sc_path)
    root_node = config_xml_data.getElementsByTagName("secureCloud")[0]
    agent_node = root_node.getElementsByTagName("agent")[0]
    key_node = agent_node.getElementsByTagName("key")[0]
    agent_vmGuid=key_node.attributes["id"].value.strip()
    if agent_vmGuid==None:
        return False
    else:
        return agent_vmGuid

def get_device_guid_by_agent_config(sc_path,device_name):
    device_guid=None
    config_xml_data= agent_config_xml_data(sc_path)
    root_node = config_xml_data.getElementsByTagName("secureCloud")[0]
    agent_node = root_node.getElementsByTagName("agent")[0]
    devices = agent_node.getElementsByTagName("devices")[0]
    devices_node = devices.getElementsByTagName("device")
    for device in devices_node:        
        if device.attributes["deviceName"].value.strip()==device_name.strip():
           device_guid = device.attributes["guid"].value.strip()             
    return device_guid

def get_server_vmGuid_by_agent_vmGuid(agent_vmGuid):
    server_vmGuid = None
    while agent_vmGuid != False:
        x = secureCloud.managementAPI.mapi_lib.mapi_lib(auth_type="api_auth")
        xml_result = x.listVM()
        if xml_result:
            vm_node = xml_result.getElementsByTagName("vmList")[0]
            devices_node = vm_node.getElementsByTagName("vms")[0]
            devices = devices_node.getElementsByTagName("vm")
            for device in devices:
             if agent_vmGuid == device.attributes["provisionedImageGUID"].value.strip():
                    server_vmGuid = device.attributes["imageGUID"].value.strip()
                    logging.debug("server_vmGuid:" + server_vmGuid)
                    return server_vmGuid

    if server_vmGuid == None:
        return False
    else:
        return server_vmGuid
def get_encrypted_single_device():
    sc_path = secureCloud.scAgent.Agent.get_sc_root()
    config_xml_data= agent_config_xml_data(sc_path)
    root_node = config_xml_data.getElementsByTagName("secureCloud")[0]
    agent_node = root_node.getElementsByTagName("agent")[0]
    devices = agent_node.getElementsByTagName("devices")[0]
    devices_node = devices.getElementsByTagName("device")
    for device in devices_node:        
        if device.attributes["diskType"].value.strip()=="general" and device.attributes["provisioningState"].value.strip()=="encrypted":
           device_guid = device.attributes["guid"].value.strip()   
           return device_guid 
def get_encrypted_raid():
    device_guid =None
    sc_path = secureCloud.scAgent.Agent.get_sc_root()
    config_xml_data= agent_config_xml_data(sc_path)
    root_node = config_xml_data.getElementsByTagName("secureCloud")[0]
    agent_node = root_node.getElementsByTagName("agent")[0]
    devices = agent_node.getElementsByTagName("devices")[0]
    devices_node = devices.getElementsByTagName("device")
    for device in devices_node:        
        if device.attributes["diskType"].value.strip()=="raid" and device.attributes["provisioningState"].value.strip()=="encrypted":
           device_guid = device.attributes["guid"].value.strip()   
           return device_guid          
    
    
def do_server_provision(vm_guid,device_msuid,preserve_data,file_system,mount_point):
    x = secureCloud.managementAPI.mapi_lib.mapi_lib(auth_type="api_auth")
    encrypt_data = x.create_ecnrypt_data(vm_guid,device_msuid,preserve_data,file_system,mount_point)
    logging.debug(encrypt_data)
    stafLogger.debug(encrypt_data)
    result = x.encryptVM(vm_guid,encrypt_data)
    stafLogger.debug(result)
    if result==1:
        case_result = 0
    else:
        case_result = 1
    return case_result
def destroy_device_key(server_vm_guid,device_msuid):
    x = secureCloud.managementAPI.mapi_lib.mapi_lib(auth_type="api_auth")
    result = x.deleteDeviceKey(server_vm_guid, device_msuid)
    stafLogger.debug("delete device key=%s result:"%device_msuid + str(result))
    if result==1:
        return 0
    else:
        return 1
    
def delete_vm(vm_name):
    x = secureCloud.managementAPI.mapi_lib.mapi_lib(auth_type="api_auth")
    vm_guid = get_vm_guid(vm_name)
    while vm_guid != False:
        logging.debug("vm guid:" + vm_guid)
        print("vm guid:" + vm_guid)
        xml_result = x.readVM(vm_guid)

        if xml_result:
            vm_node = xml_result.getElementsByTagName("vm")[0]
            devices_node = vm_node.getElementsByTagName("devices")[0]
            devices = devices_node.getElementsByTagName("device")
            for device in devices:
                current_device = device.attributes["name"].value.strip()
                current_msuid = device.attributes["msUID"].value.strip()
                logging.debug("current device:%s" % (current_device))
                logging.debug("current device msuid :%s" % (current_msuid))
                result = x.deleteDeviceKey(vm_guid, current_msuid)
                logging.debug("delete device key result:" + str(result))

                result = x.cancelPending(vm_guid, current_msuid)
                logging.debug("delete device key result:" + str(result))
                #if not result:

                #	return 1

            result = x.deleteVM(vm_guid)
            logging.debug("delete VM result:" + str(result))

        vm_guid = get_vm_guid(vm_name)

    return 0


def delete_vm_devices(vm_name):
    x = secureCloud.managementAPI.mapi_lib.mapi_lib(auth_type="api_auth")
    vm_guid = get_vm_guid(vm_name)
    if vm_guid != False:
        logging.debug("vm guid:" + vm_guid)
        print("vm guid:" + vm_guid)
        xml_result = x.readVM(vm_guid)

        if xml_result:
            vm_node = xml_result.getElementsByTagName("vm")[0]
            devices_node = vm_node.getElementsByTagName("devices")[0]
            devices = devices_node.getElementsByTagName("device")
            for device in devices:
                current_device = device.attributes["name"].value.strip()
                current_msuid = device.attributes["msUID"].value.strip()
                logging.debug("current device:%s" % (current_device))
                logging.debug("current device msuid :%s" % (current_msuid))
                
                if current_device == "/dev/sda" or current_device == "harddisk0":
                    continue
                else:
                    result = x.deleteDeviceKey(vm_guid, current_msuid)
                    logging.debug("delete device key result:" + str(result))

                    result = x.cancelPending(vm_guid, current_msuid)
                    logging.debug("delete device key result:" + str(result))

                    result = x.deleteDevice(vm_guid, current_msuid)
                    logging.debug("delete device key result:" + str(result))

                #if not result:
                #	return 1

    return 0

def delete_vm_scmc(agent_vm_guid):
    retval=0
    server_vm_guid = get_server_vmGuid_by_agent_vmGuid(agent_vm_guid)
    x = secureCloud.managementAPI.mapi_lib.mapi_lib(auth_type="api_auth")
    if server_vm_guid != False:
        stafLogger.debug("agent_vm_guid:" + agent_vm_guid)
        xml_result = x.readVM(server_vm_guid)
        if xml_result:
            vm_node = xml_result.getElementsByTagName("vm")[0]
            devices_node = vm_node.getElementsByTagName("devices")[0]
            devices = devices_node.getElementsByTagName("device")
            for device in devices:
                current_device = device.attributes["name"].value.strip()
                current_msuid = device.attributes["msUID"].value.strip()
                current_status = device.attributes["deviceStatus"].value.strip()
                stafLogger.debug("device name=%s, device msuid=%s, device status=%s," % (current_device,current_msuid,current_status))
                if  current_status == "Encrypted":
                  result=destroy_device_key(server_vm_guid,current_msuid)  
                  if result==1:
                      continue
                  else:
                       retval= 1
        time.sleep(30)
    delete_vm_result = x.deleteVM(server_vm_guid)
    stafLogger.debug("delete server_vm_guid=%s, result=%s"%(server_vm_guid,str(delete_vm_result)))
    if not delete_vm_result:
           errorLogger.error("delete server_vm_guid=%s fail")
           retval= 1
    return retval

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
def create_RAID(vm_name, raid_name, raid_level, raid_fs, device_id_list, raid_desc, mount_point):
    vm_guid = get_vm_guid(vm_name)
    if vm_guid == False:
        logging.debug("cannot find vm GUID")
        return 1   
    logging.debug("vm guid:" + vm_guid)
    
    device_msuid_list = []
    for device_id in device_id_list:
        device_msuid = get_device_guid(vm_name, device_id)
        if not device_msuid:
            logging.debug("Failed to find device msuid with device id:%s" % (device_id))
            return 1
        else:
            device_msuid_list.append(device_msuid)

    x = secureCloud.managementAPI.mapi_lib.mapi_lib(auth_type="api_auth")
    xml_result = x.createRAID(vm_guid, None, raid_name, raid_level, raid_fs, device_msuid_list, raid_desc, mount_point)

    return check_device_existing(vm_name, raid_name, False)

def create_RAID_server(raid_name, raid_level, raid_fs, device_name_list, raid_desc, mount_point,sc_path):
    agent_vm_guid = get_agent_vmGuid(sc_path)
    if agent_vm_guid == False:
        errorLogger.error("cannot find agent_vmGuid")
        return 1
    x = secureCloud.managementAPI.mapi_lib.mapi_lib(auth_type="api_auth")
    server_vm_guid = get_server_vmGuid_by_agent_vmGuid(agent_vm_guid)
    if server_vm_guid == False:
        logging.debug("cannot find server_vm_guid")
        return 1
    stafLogger.debug("agent_vm_guid:" + agent_vm_guid)
    stafLogger.debug("server_vm_guid:" + agent_vm_guid)
    
    device_msuid_list = []
    for device_name in device_name_list:
        device_msuid = get_device_guid_by_agent_config(sc_path, device_name)
        if not device_msuid:
            errorLogger.error("Failed to find device msuid with device_name:%s\n" % (device_name))
            return 1
        else:
            device_msuid_list.append(device_msuid)

    x = secureCloud.managementAPI.mapi_lib.mapi_lib(auth_type="api_auth")
    xml_result = x.createRAID(server_vm_guid, None, raid_name, raid_level, raid_fs, device_msuid_list, raid_desc, mount_point)
    stafLogger.debug('create_RAID_server:\n %s\n'%xml_result)
    if xml_result:
        return 0
    else:
        return 1

def encrypt_RAID(vm_name, raid_name, file_system, mount_point):
    vm_guid = get_vm_guid(vm_name)
    if vm_guid == False:
        logging.debug("cannot find vm GUID")
        return 1   
    logging.debug("vm guid:" + vm_guid)
    
    device_guid = get_device_guid(vm_name, raid_name)
    if not device_guid:
        logging.debug("Failed to find device msuid with device name:%s" % (raid_name))
        return 1


    x = secureCloud.managementAPI.mapi_lib.mapi_lib(auth_type="api_auth")
    xml_result = x.encryptRAID(vm_guid, device_guid, file_system, mount_point)
    if xml_result:
        return 0
    else:
        return 1

def encrypt_RAID_server(server_vm_guid, raid_name, file_system, mount_point,sc_path):
    if server_vm_guid == False:
        logging.debug("server_vm_guid is null. \n")
        return 1   
    
    device_guid = get_device_guid_from_server(server_vm_guid,raid_name)
    if not device_guid:
        logging.debug("Failed to find device msuid with device name:%s" % (raid_name))
        return 1


    x = secureCloud.managementAPI.mapi_lib.mapi_lib(auth_type="api_auth")
    xml_result = x.encryptRAID(server_vm_guid, device_guid, file_system, mount_point)
    if xml_result:
        return 0
    else:
        return 1

def update_auto_prov(server_vm_guid, auto_prov):
    if server_vm_guid == False:
        errorLogger.error("server_vm_guid is null. \n")
        return 1   
    x = secureCloud.managementAPI.mapi_lib.mapi_lib(auth_type="api_auth")
    xml_readVM= x.readVM(server_vm_guid)
    vm_node = xml_readVM.getElementsByTagName("vm")[0]
    vm_name = vm_node.attributes["imageName"].value.strip()
    stafLogger.debug('vm_name: %s\n'%vm_name)
    securityGroupID=vm_node.attributes["SecurityGroupGUID"].value.strip()
    stafLogger.debug('securityGroupID: %s\n'%securityGroupID)
    xml_result = x.updateVM(server_vm_guid,vm_name,auto_prov,securityGroupID)
    stafLogger.debug(xml_result)
    if not xml_result:
        errorLogger.error('Invoke UpdateVM got error')
        return 1
    vm_node = xml_result.getElementsByTagName("vm")[0]
    current_autoProv = vm_node.attributes["autoProvision"].value.strip()
    if current_autoProv==auto_prov:
        return 0
    else:
        errorLogger.error('Invoke with no error but new auto-provision value not be updated\n')
        stafLogger.debug('New autoProvision=%s\n'%current_autoProv)
        return 1
    
def print_vm(vm_name):
    x = secureCloud.managementAPI.mapi_lib.mapi_lib(auth_type="api_auth")
    vm_guid = get_vm_guid(vm_name)
    if vm_guid == False:
        logging.debug("cannot find vm GUID")
        return 1
    logging.debug("vm guid:" + vm_guid)

    xml_result = x.readVM(vm_guid)

    vm_node = xml_result.getElementsByTagName("vm")[0]
    devices_node = vm_node.getElementsByTagName("devices")[0]
    devices = devices_node.getElementsByTagName("device")
    for device in devices:
        current_device = device.attributes["name"].value.strip()
        current_msuid = device.attributes["msUID"].value.strip()
        logging.debug("current device:%s" % (current_device))
        logging.debug("current device msuid :%s" % (current_msuid))



def create_policy(vm_name, EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
                    RevokeIntervalType, policy_name, isResourcePool, description, \
                    successAction, successActionDelay, failAction, failActionDelay, security_rule_list):

    x = secureCloud.managementAPI.mapi_lib.mapi_lib(auth_type="api_auth")

    if len(policy_name) > 32:
        policy_name = policy_name[:32]

    policy_guid = x.get_policy_id_from_policy_name(policy_name)

    if policy_guid:
        x.deleteSecurityGroup(policy_guid)

    vm_guid = get_vm_guid(vm_name)
    if vm_guid == False:
        logging.debug("cannot find vm GUID")
        return 1   
    logging.debug("vm guid:" + vm_guid)

    device_id_list=[]
    image_id_list = [vm_guid]



    xml_result = x.createSecurityGroup(EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
                    RevokeIntervalType, policy_name, isResourcePool, description, \
                    successAction, successActionDelay, failAction, failActionDelay, \
                    device_id_list,image_id_list, security_rule_list)

    if not xml_result:
        return 1

    policy_guid = x.get_policy_id_from_policy_name(policy_name)

    if policy_guid:
        return 0
    else:
        return 1


def update_policy(vm_name, EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
                    RevokeIntervalType, policy_name, isResourcePool, description, \
                    successAction, successActionDelay, failAction, failActionDelay, security_rule_list):

    if len(policy_name) > 32:
        policy_name = policy_name[:32]

    x = secureCloud.managementAPI.mapi_lib.mapi_lib(auth_type="api_auth")
    policy_guid = x.get_policy_id_from_policy_name(policy_name)

    if not policy_guid:
        return 1
    
    vm_guid = get_vm_guid(vm_name)
    if vm_guid == False:
        logging.debug("cannot find vm GUID")
        return 1   
    logging.debug("vm guid:" + vm_guid)

    device_id_list=[]
    image_id_list = [vm_guid]

    xml_result = x.updateSecurityGroup(policy_guid, EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
                    RevokeIntervalType, policy_name, isResourcePool, description, \
                    successAction, successActionDelay, failAction, failActionDelay, \
                    device_id_list,image_id_list, security_rule_list)

    if not xml_result:
        return 1
    else:
        return 0




def delete_policy(policy_name):

    x = secureCloud.managementAPI.mapi_lib.mapi_lib(auth_type="api_auth")

    if len(policy_name) > 32:
        policy_name = policy_name[:32]

    policy_guid = x.get_policy_id_from_policy_name(policy_name)

    if policy_guid:
        result = x.deleteSecurityGroup(policy_guid)
        if not result:
            return 1

    return 0


def print_runningVM():
    x = secureCloud.managementAPI.mapi_lib.mapi_lib(auth_type="api_auth")
    xml_result = x.runningVM()

    """
    vm_node = xml_result.getElementsByTagName("vm")[0]
    devices_node = vm_node.getElementsByTagName("devices")[0]
    devices = devices_node.getElementsByTagName("device")
    for device in devices:
        current_device = device.attributes["name"].value.strip()
        current_msuid = device.attributes["msUID"].value.strip()
        logging.debug("current device:%s" % (current_device))
        logging.debug("current device msuid :%s" % (current_msuid))
    """


def get_runningVM_id_status(vm_name, retry=30):
    import secureCloud.managementAPI.mapi_util
    
    x = secureCloud.managementAPI.mapi_lib.mapi_lib(auth_type="api_auth")
    xml_result = x.runningVM()
    count = 0
    while (not xml_result) and count < retry:
        time.sleep(90)
        count += 1
        xml_result = x.runningVM()

    running_vm_list = xml_result.getElementsByTagName("runningVMList")[0]
    running_vms = running_vm_list.getElementsByTagName("runningVM")
    for running_vm in running_vms:
        current_image_name = running_vm.attributes["imageName"].value.strip()
        if current_image_name == vm_name:
            runningVMKeyRequest_node = running_vm.getElementsByTagName("runningVMKeyRequest")[0]
            key_request_guid = runningVMKeyRequest_node.attributes["requestID"].value.strip()
            deviceKeyRequestState_node = runningVMKeyRequest_node.getElementsByTagName("deviceKeyRequestState")[0]
            key_status = secureCloud.managementAPI.mapi_util.getText(deviceKeyRequestState_node)
            logging.debug("current image name:%s" % (current_image_name))
            logging.debug("current key status:%s" % (key_status))
            logging.debug("current key request guid:%s" % (key_request_guid))

            return key_request_guid, key_status

    return "", ""


def handle_key_request(vm_name, action):
    key_request_guid, key_status = get_runningVM_id_status(vm_name)


    x = secureCloud.managementAPI.mapi_lib.mapi_lib(auth_type="api_auth")
    xml_result = x.runningVMKeyRequest(key_request_guid, action)

    if xml_result:
        return True
    else:
        return False


def deny_key(vm_name):
    retry = 60
    key_request_guid, key_status = get_runningVM_id_status(vm_name)

    count = 0
    while (key_request_guid == "" or key_status <> "pending") and count < retry:
        key_request_guid, key_status = get_runningVM_id_status(vm_name)
        count = count + 1
        time.sleep(10)

    if key_status <> "pending":
        return 1

    x = secureCloud.managementAPI.mapi_lib.mapi_lib(auth_type="api_auth")
    xml_result = x.runningVMKeyRequest(key_request_guid, "deny")

    #verify 
    key_request_guid, key_status = get_runningVM_id_status(vm_name)
    count = 0
    while key_status <> "denied" and count < retry:
        key_request_guid, key_status = get_runningVM_id_status(vm_name)
        count = count + 1
        time.sleep(10)
        
    if key_status == "denied":
        return 0
    else:
        return 1


def manual_approve(vm_name):
    retry = 60
    key_request_guid, key_status = get_runningVM_id_status(vm_name)

    count = 0
    while (key_request_guid == "" or key_status <> "pending") and count < retry :
        key_request_guid, key_status = get_runningVM_id_status(vm_name)
        count = count + 1
        time.sleep(10)

    if key_status <> "pending":
        return 1

    x = secureCloud.managementAPI.mapi_lib.mapi_lib(auth_type="api_auth")
    xml_result = x.runningVMKeyRequest(key_request_guid, "approve")

    #verify 
    key_request_guid, key_status = get_runningVM_id_status(vm_name)
    count = 0
    while key_status <> "delivered" and count < retry:
        key_request_guid, key_status = get_runningVM_id_status(vm_name)
        count = count + 1
        time.sleep(10)

    if key_status == "delivered":
        return 0
    else:
        return 1



def run_manual_icm(vm_name):
    retry = 60
    key_request_guid, key_status = get_runningVM_id_status(vm_name)

    count = 0
    while key_request_guid == "" and count < retry:
        key_request_guid, key_status = get_runningVM_id_status(vm_name)
        count = count + 1
        time.sleep(10)


    x = secureCloud.managementAPI.mapi_lib.mapi_lib(auth_type="api_auth")
    xml_result = x.runningVMKeyRequest(key_request_guid, "runicm")

    #verify 
    if xml_result:
        return 0
    else:
        return 1



def check_revoked(vm_name):
    retry = 120
    key_request_guid, key_status = get_runningVM_id_status(vm_name)

    count = 0
    while key_status <> "revoked" and count < retry:
        key_request_guid, key_status = get_runningVM_id_status(vm_name)
        if key_status == "revoked":
            return 0
        
        count = count + 1
        time.sleep(10)

    return 1


# called
def download_build(os, url, download_file):
    if os == "WINDOWS":
        return_code = secureCloud.agentBVT.util.get(url, download_file)
    elif os == "LINUX":
        command = "wget -O %s %s --retry-connrefused" % (download_file, url)
        return_code = subprocess.call(command, shell=True)


    return return_code
        


def ini_update(config_path, section, option, value):
    try:
        config = ConfigParser.ConfigParser()
        # confog.optionxform = str
        config.read(config_path)
        config.set(section, option, value)
        config.write(open(config_path, 'w+'))

    except Exception, e:
        logging.error(e)

# called


def check_sc_install_dir(sc_install_dir):
    logging.debug("check sc install path: %s" % sc_install_dir)
    ret = os.path.exists(sc_install_dir)

    if ret == True:
        return 0
    else:
        return 1


# called
def check_sc_service():
    os_type = platform.system()
    if os_type == "Windows":
        ret = subprocess.call("sc query c9agentsvc", shell=True)
        logging.debug("return code:%s" % str(ret))
        if ret == 0:
            return 0
        else:
            return 1
    else:
        ret = os.path.exists(r'/etc/init.d/scagentd')
        logging.debug("return code:%s" % str(ret))
        if ret == True:
            return 0
        else:
            return 1


def start_sc_service():
    os_type = platform.system()
    if os_type == "Windows":
        ret = subprocess.call("net start c9agentsvc", shell=True)
        if ret == 0:
            return 0
        else:
            return 1
    else:
        ret = Popen("service scagentd stop", shell=True, stdout=PIPE)
        output = ret.communicate()

        #print output
        # ('Stop: Service is not running\n', None)

        m = re.search(r"Stop: Service is not running", output[0])
        while not m:
            time.sleep(300)
            logging.debug("service is not stopped, wait 300s then retry")
            print("service is not stopped, wait 300s then retry")
            ret = Popen("service scagentd stop", shell=True, stdout=PIPE)
            output = ret.communicate()
            m = re.search(r"Stop: Service is not running", output[0])


        ret = subprocess.call(r'service scagentd start', shell=True)
        time.sleep(15)

    return ret


def stop_sc_service(unmount=True, retry=3):
    os_type = platform.system()

    if os_type == "Windows":
        scagent_is_stopped = False
        cmd = os.popen("sc query c9agentsvc")
        x = cmd.readlines()
        current_status = ""
        for y in x:
            print y
            print "------------------------------"
            m = re.search( r"(\s+)STATE(\s+)\:(\s+)(\d+)(\s+)(\w+)", y )
            if m:
                current_status = m.group(6)
                logging.debug("current scagent service status:%s" % current_status)
                # STATE = STOPPED or RUNNING

        if current_status == "RUNNING":
            logging.debug("c9agentsvc is running, stop the service")
            ret = subprocess.call("net stop c9agentsvc", shell=True)
            logging.debug("service stop result:%s" % (str(ret)))
        elif current_status == "STOPPED":
            logging.debug("service is already stopped")
            
        some_drive_still_existing = False
        if os.path.exists("G:\\test_file.txt"):
            some_drive_still_existing = True
        if os.path.exists("H:\\test_file.txt"):
            some_drive_still_existing = True
        if os.path.exists("I:\\test_file.txt"):
            some_drive_still_existing = True
        if os.path.exists("J:\\test_file.txt"):
            some_drive_still_existing = True
        if os.path.exists("L:\\test_file.txt"):
            some_drive_still_existing = True
        if os.path.exists("M:\\test_file.txt"):
            some_drive_still_existing = True
        if os.path.exists("N:\\test_file.txt"):
            some_drive_still_existing = True
        if os.path.exists("O:\\test_file.txt"):
            some_drive_still_existing = True
        if os.path.exists("P:\\test_file.txt"):
            some_drive_still_existing = True
        if os.path.exists("Q:\\test_file.txt"):
            some_drive_still_existing = True

        if some_drive_still_existing:
            logging.debug("some devices failed to unmount during service stop")

        # To-Do: return 0 let test process, fix later
        return 0
    else:
        ret = Popen(["ps", "-A"], shell=True, stdout=subprocess.PIPE)
        out, err = ret.communicate()
        if not ('scagent' in out):
            logging.debug("scagent is not running")
            return 0

        ret = Popen("service scagentd stop", shell=True, stdout=PIPE)
        output = ret.communicate()

        logging.debug("service stop output:%s", output[0])
        # ('Stop: Service is not running\n', None)

        count = 0
        m = re.search(r"Stop: Service is not running", output[0])
        while (not m) and count < retry:
            time.sleep(300)
            ret = Popen("service scagentd stop", shell=True, stdout=PIPE)
            output = ret.communicate()
            logging.debug("service stop output:%s", output[0])
            m = re.search(r"Stop: Service is not running", output[0])
            count += 1

        if unmount:
            is_mount_point = os.path.ismount("/mnt/sdb1")
            if is_mount_point:
                command = "umount /mnt/sdb1"
                return_code = subprocess.call(command, shell=True)
                logging.debug("/mnt/sdb1 is not unmounted, unmount manually, ret:%s", str(return_code))

            is_mount_point = os.path.ismount("/mnt/sdc1")
            if is_mount_point:
                command = "umount /mnt/sdc1"
                return_code = subprocess.call(command, shell=True)
                logging.debug("/mnt/sdc1 is not unmounted, unmount manually, ret:%s", str(return_code))

            is_mount_point = os.path.ismount("/mnt/sdd1")
            if is_mount_point:
                command = "umount /mnt/sdd1"
                return_code = subprocess.call(command, shell=True)
                logging.debug("/mnt/sdd1 is not unmounted, unmount manually, ret:%s", str(return_code))

            is_mount_point = os.path.ismount("/mnt/sde1")
            if is_mount_point:
                command = "umount /mnt/sde1"
                return_code = subprocess.call(command, shell=True)
                logging.debug("/mnt/sde1 is not unmounted, unmount manually, ret:%s", str(return_code))

            is_mount_point = os.path.ismount("/mnt/sdf1")
            if is_mount_point:
                command = "umount /mnt/sdf1"
                return_code = subprocess.call(command, shell=True)
                logging.debug("/mnt/sdf1 is not unmounted, unmount manually, ret:%s", str(return_code))

            is_mount_point = os.path.ismount("/mnt/sdg1")
            if is_mount_point:
                command = "umount /mnt/sdg1"
                return_code = subprocess.call(command, shell=True)
                logging.debug("/mnt/sdg1 is not unmounted, unmount manually, ret:%s", str(return_code))

            is_mount_point = os.path.ismount("/mnt/test_raid")
            if is_mount_point:
                command = "umount /mnt/test_raid"
                return_code = subprocess.call(command, shell=True)
                logging.debug("/mnt/test_raid is not unmounted, unmount manually, ret:%s", str(return_code))

            is_mount_point = os.path.ismount("/mnt/sdj1")
            if is_mount_point:
                command = "umount /mnt/sdj1"
                return_code = subprocess.call(command, shell=True)
                logging.debug("/mnt/sdj1 is not unmounted, unmount manually, ret:%s", str(return_code))


    return 0
def is_sc_stop():
    ret = Popen("service scagentd status", shell=True, stdout=PIPE)
    output = ret.communicate()
    logging.debug("service status output:%s", output[0])
        # ('Stop: Service is not running\n', None)
    m = re.search(r"Service is not running.", output[0])
    if m: 
        return 0
    else:
        return 1
def is_sc_start():
    ret = Popen("service scagentd status", shell=True, stdout=PIPE)
    output = ret.communicate()
    logging.debug("service status output:%s", output[0])
        # ('Stop: Service is not running\n', None)
    m = re.search(r"Service is running.", output[0])
    if m: 
        return 0
    else:
        return 1

def is_mount_point(mount_point):
    is_mount_point = os.path.ismount("%s"%mount_point)
    if is_mount_point:
        command = "umount %s"% mount_point
        return_code = subprocess.call(command, shell=True)
        logging.debug("%s is not unmounted, unmount manually, ret:%s", mount_point,str(return_code))
        return 0

def is_file_exist(file_path):
    ret = os.path.exists(file_path)
    if not ret:
        return 1
    else:
        return 0
    
def collect_latest_tmstaf_log(tmstaf_result_path, tmp_tmstaf_log):

    dir_list = sorted(os.listdir(tmstaf_result_path))
    logging.info("collect_latest_tmstaf_log() [%s]" % dir_list)

    while True:
        latest_dir = dir_list.pop()
        result_folder = os.path.join(tmstaf_result_path, latest_dir)
        if os.path.isdir(result_folder):
            break

    shutil.copyfile(os.path.join(result_folder, "tmstaf.log"), tmp_tmstaf_log)


def agent_silent_provision(account_id, kms_url, passphrase, access_id=None, secret_key=None):
    os_type = platform.system()  # Linux or Windows
    if os_type == "Linux":
        scconfig_exec = os.path.join(get_agent_install_path(), "scconfig.sh")
    else:  # os_type = "Windows"
        scconfig_exec = os.path.join(get_agent_install_path(), "scconfig.exe")

    # EC2 or ESX
    if access_id and secret_key:  # this is an ec2 instance
        command = "%s --register --csp-id=Amazon-AWS --options=%s,%s --guid='%s' --url='%s' --passphrase='%s' \
--publish-inventory --timeout=10 --get-device-list -q" % (scconfig_exec, access_id, secret_key, account_id, kms_url, passphrase)
    else:  # this is ec2 instance, native plugin
        command = "%s --register --csp-id=Native --guid='%s' --url='%s' --passphrase='%s' \
--publish-inventory --timeout=10 --get-device-list -q" % (scconfig_exec, account_id, kms_url, passphrase)
    logging.info(command)
    p = subprocess.call(command, shell=True)
    return p


def get_cspharness_type():
    os_type = platform.system()  # Linux or Windows
    if os_type == "Windows":
        cspharness_type = "cspharness.exe"
    else:
        cspharness_type = "cspharness.sh"
    return cspharness_type


def create_cspharness_conf(csp_name="", cred_list="", map_device_list=""):
    if csp_name == "Amazon":
        plugin_path = "amazonaws.zip"
    elif csp_name == "Native":
        plugin_path = "native.zip"

    xml_str = """<config>
    <PLUGIN_PATH>%s</PLUGIN_PATH>
    <CRED_LIST>%s</CRED_LIST>
    <MAP_DEVICE_LIST>%s</MAP_DEVICE_LIST>\n</config>""" % (plugin_path, cred_list, map_device_list)

    save_path = os.path.join(get_agent_install_path(), "csp_harness.conf")

    f = open(save_path, "w")
    f.write(xml_str)
    f.close()

# called


def install_agent_windows(EndPoint, remote_filepath_exe):
    intExitCode, strStdout = secureCloud.agentBVT.staf.call_remote(EndPoint, remote_filepath_exe, [])

    """
    #execute installer fail
    if intExitCode != "0":
        return intExitCode
    """

    # shutdown staf wait reboot
    #secureCloud.agentBVT.staf.shutdown(EndPoint)
    #logging.info("start to wait staf ...")
    #LONGTIMES = 20
    #secureCloud.agentBVT.staf.wait_ready(EndPoint, 20)
    return intExitCode

# called


def install_agent_linux(remote_filepath_exe):
    command = "chmod 755 " + remote_filepath_exe
    logging.debug("Chmod 755 agent build command:" + command)
    return_code = subprocess.call(command, shell=True)

    command = "%s quiet " % (remote_filepath_exe)
    logging.debug("Agent install command:" + command)
    return_code = subprocess.call(command, shell=True)

    return return_code


def uninstall_agent(OS):
    if OS == "WINDOWS":
        command = """wmic product where name="Trend Micro SecureCloud Agent" call uninstall"""
        logging.debug("uninstall command:" + command)
    elif OS == "LINUX":
        """
        ('CentOS', '6.2', 'Final')
        ('Red Hat Enterprise Linux Server', '6.3', 'Santiago')
        ('Ubuntu', '12.10', 'quantal')
        """
        current_distribution = platform.linux_distribution()
        print current_distribution
        if current_distribution[0] == "CentOS" or current_distribution[0] == "Red Hat Enterprise Linux Server":
            command = """rpm -ev scagent"""
        elif current_distribution[0] == "Ubuntu":
            command = """dpkg --purge scagent"""

    logging.debug("uninstall command:" + command)
    return_code = subprocess.call(command, shell=True)

    logging.debug("uninstall result:" + str(return_code))

    time.sleep(60)

    return return_code



# called
def linux_rescan_iscsi_disks():
    time.sleep(20)  # waite for 10 seconds for all devices to attach to VM
    command = """find /sys/class/scsi_host/host*/scan | while read line; do echo - - - > $line; done"""
    logging.debug("Rescan iSCSI command:" + command)
    return_code = subprocess.call(command, shell=True)
    return return_code

# called
def linux_reboot_client(EndPoint, retry=10):
	#shutdown staf wait reboot

	count = 0
	ret = subprocess.call("reboot", shell=True)

	while(count < retry and ret != 0):
		time.sleep(10)
		ret = subprocess.call("reboot", shell=True)
		count += 1


	#secureCloud.agentBVT.staf.shutdown(EndPoint)
	return ret

# called
def windows_reboot_client(EndPoint, retry=10):
	#shutdown staf wait reboot

	count = 0
	ret = subprocess.call("shutdown -r", shell=True)


def insert_securecloud_conf(securecloud_conf):

    test_settings = """
[Default]
TREND_KMS_URL=https://ms.lab.securecloud.com/
LOG_LEVEL=DEBUG

[Interval]
PUBLISH_INVENTORY=5
PROVISION_DEVICE=5
UPDATE_PROVISION_PROGRESS=5"""

    os_type = platform.system()
    if os_type == "Windows":
        try:
            f = open(securecloud_conf , "w")
            try:
                f.write(test_settings)
            finally:
                f.close()
        except IOError:
            logging.error("Failed to open or write to file")
            return 1
    else:
        try:
            f = open(securecloud_conf,'r+')
            content = f.read()
            f.seek(0,0)
            f.write(test_settings + '\n\n' + content)
            f.close()
        except IOError:
            logging.error("Failed to open or write to file")
            return 1

    return 0



def run_scprov_prov(sc_path, device_type, provision_passphrase, provision_type="preserve", retry=10):
    time.sleep(3)

    """Sample
    scprov prov --devices=all|root|data|<device-list> --passphrase=<prov-passphrase> [--quiet]
    """

    command = """ "%s" prov --devices=%s -t %s --passphrase=%s  --quiet """ % (sc_path, device_type, provision_type, provision_passphrase)
    logging.debug(command)
    logging.debug("path is: %s" % sys.path)
    logging.debug("os.environ is: %s" % os.environ)
    my_env = os.environ
    my_env["LD_LIBRARY_PATH"] = ""

    count = 0
    return_code = 1
    while (return_code <> 0 and count < retry):

        if platform.dist()[0] == "SuSE":
            logging.debug("run_scprov_prov under SuSe, clean up LD_LIBRARY_PATH")
            return_code = subprocess.call(command, shell=True, env=my_env)
        else:
            return_code = subprocess.call(command, shell=True)

        logging.debug("return code:" + str(return_code))

        count += 1
        time.sleep(30)

    return return_code


# called
def run_scprov_conf(sc_path, temp_path, provision_passphrase, kms_url, kms_account_id, csp_id, policy_id, is_auto_provision, vcloud, vcloud_user, vcloud_pass, vcloud_org, retry=10):
    """
    Sample
    //AgentConfig.conf
    [Agent]
    KMS_URL=https://ms.securecloud.com:443
    ACCOUNT_ID=<account id>
    CSP=<csp id>
    POLICY=<policy id>
    AUTO_PROVISION=<yes or no>

    CSP id:
    Amazon-AWS, vCloud, CloudStack, Native

    Vcloud with
    [vCloud]
    VCSD_ADDRESS=172.18.0.10
    ORGANIZATION=tw
    USER_NAME=test
    USER_PWD=test
    """

    time.sleep(3)

    agent_config_file = """[Agent]
KMS_URL=%s
ACCOUNT_ID=%s
CSP=%s
POLICY=%s

AUTO_PROVISION=%s
""" % (kms_url, kms_account_id, csp_id, policy_id, is_auto_provision)


    if csp_id == "vCloud":
        agent_config_file += """[vCloud]
VCSD_ADDRESS=%s
ORGANIZATION=%s
USER_NAME=%s
USER_PWD=%s
""" % (vcloud, vcloud_org, vcloud_user, vcloud_pass)

    agent_config_path = temp_path + "AgentConfig.conf"

    #f = open(agent_config_path , "w")
    #f.write(agent_config_file)
    #f.close()


    try:
        if not os.path.isdir(temp_path):
            os.mkdir(temp_path)
        # This will create a new file or **overwrite an existing file**.
        f = open(agent_config_path , "w")
        try:
            f.write(agent_config_file)
        finally:
            f.close()
    except IOError:
        logging.error("Failed to open or write to file")
        return 1

    count = 0
    return_code = 1
    while (return_code <> 0 and count < retry):
        os_type = platform.system()
        if os_type == "Windows":
            command = """ "%s" conf -c %s -x %s -q """ % (sc_path, agent_config_path, provision_passphrase)
        else:
            command = """ "%s" conf -c %s -x %s -q """ % (sc_path, agent_config_path, provision_passphrase)
        logging.debug(command)

        #logging.debug("pythonpath is: %s" % sys.path)
        #logging.debug("os.environ is: %s" % os.environ)
        my_env = os.environ
        my_env["LD_LIBRARY_PATH"] = ""

        if platform.dist()[0] == "SuSE":
            logging.debug("run_scprov_prov under SuSe, clean up LD_LIBRARY_PATH")
            return_code = subprocess.call(command, shell=True, env=my_env)
        else:
            return_code = subprocess.call(command, shell=True)

        logging.debug("count:" + str(count))
        logging.debug("return code:" + str(return_code))

        count += 1
        time.sleep(30)

    return return_code


# default : 50 mins
def check_agent_side_device_provision_status(agent_config_file, disk_name, retry_time=300):

    count = 0
    provision_state = ""
    logging.debug("begin: check_agent_side_device_provision_status")

    while(provision_state != "encrypted" and count < retry_time):
        f = open(agent_config_file, "r")
        agent_config = f.read()
        f.close()

        xmldata = xml.dom.minidom.parseString(agent_config)
        securecloud_node = xmldata.getElementsByTagName("secureCloud")[0]
        agent_node = securecloud_node.getElementsByTagName("agent")[0]
        devices_node = agent_node.getElementsByTagName("devices")[0]
        device_nodes = devices_node.getElementsByTagName("device")

        for device in device_nodes:
            if disk_name == device.attributes["deviceName"].value.strip():
                provision_state = device.attributes["provisioningState"].value.strip()
                logging.debug("device provision state:%s" % (provision_state))
                if provision_state == "encrypted":
                    return 0
        count += 1
        time.sleep(10)

    return 1


def check_agent_side_device_existing(agent_config_file, disk_name, retry=200):

    count = 0
    is_existing = False
    logging.debug("begin: check_agent_side_device_existing")

    while(is_existing == False and count < retry):
        f = open(agent_config_file, "r")
        agent_config = f.read()
        f.close()

        xmldata = xml.dom.minidom.parseString(agent_config)
        securecloud_node = xmldata.getElementsByTagName("secureCloud")[0]
        agent_node = securecloud_node.getElementsByTagName("agent")[0]
        devices_node = agent_node.getElementsByTagName("devices")[0]
        device_nodes = devices_node.getElementsByTagName("device")

        for device in device_nodes:
            if disk_name == device.attributes["deviceName"].value.strip():
                logging.debug("device is found")
                is_existing = True
                return 0

        logging.debug("device is not found")
        count += 1
        time.sleep(10)

    return 1

def check_log(log_file_path,keyword, retry=5):

    count = 0
    ret = os.path.exists(log_file_path)

    while(not ret and count < retry):
        ret = os.path.exists(log_file_path)
        time.sleep(10)

    if not ret:
        logging.debug("%s is not found" % log_file_path)
        return 1

    count = 0
    is_existing = False
    logging.debug("begin. check log: %s" %log_file_path)

    while(is_existing == False and count < 5):
        f = open(log_file_path, "r")
        lines = f.readlines()
        f.close()

        for line in lines:
            line = line.strip()
            # print line
            m = re.search(keyword, line, flags=re.IGNORECASE)
            if m:
                is_existing = True
                return 0

        logging.debug("finish. keyword: '%s' is not found" %keyword)
        count += 1
        time.sleep(10)

    return 1
def check_preboot_log(preboot_log, retry=200):

    count = 0
    ret = os.path.exists(preboot_log)

    while(not ret and count < retry):
        ret = os.path.exists(preboot_log)
        time.sleep(10)

    if not ret:
        logging.debug("preboot.log is not found")
        return 1

    count = 0
    is_existing = False
    logging.debug("begin: check_agent_side_device_existing")

    while(is_existing == False and count < 200):
        f = open(preboot_log, "r")
        lines = f.readlines()
        f.close()

        for line in lines:
            line = line.strip()
            # print line
            m = re.search(r"Install preboot image successfully", line, flags=re.IGNORECASE)
            if m:
                is_existing = True
                return 0

        logging.debug("finish keyword is not found")
        count += 1
        time.sleep(10)

    return 1


def insert_test_file(test_file, retry=30):

    count = 0
    while(count < retry):
        # This will create a new file or **overwrite an existing file**.
        try:
            f = open(test_file, 'w')
            f.write("test data")
            f.close()
            return 0
        except IOError:
            logging.error("Failed to open or write to file")

        count += 1
        time.sleep(30)

    return 1


# default 10 mins
def check_test_file(test_file, retry=90):
    count = 0
    while( count < retry):
        try:
            if os.path.exists(test_file):
                f = open(test_file, 'r')
                test_data = f.read()
                f.close()

                current_platform = platform.system()
                if current_platform == "Linux":
                    is_mount_point = os.path.ismount(os.path.dirname(test_file))
                    if not is_mount_point:
                        return 1

                logging.debug("%s is found and readable" % (test_file))
                return 0
            else:
                logging.debug("%s is not found" % (test_file))
        except Exception, e:
            logging.error(e)
            logging.error("fail checking the test file:%s" % (test_file))

        count += 1
        time.sleep(10)

    return 1




def create_zero_file(dd_path, file_path, file_size):

	command = """%s if=/dev/zero of=%s bs=1M count=%s """ % (dd_path, file_path, file_size)
	logging.debug("dd command:" + command)
	return_code = subprocess.call(command, shell=True)

	return return_code


def run_zero_check(zero_path, file_path, dump_file_path):
	command = """%s -d -f %s > %s """ % (zero_path, file_path, dump_file_path)
	logging.debug("zero command:" + command)
	#return_code = subprocess.call(command, shell=True)
	#return_code = os.system(command)
	result = subprocess.Popen([zero_path, "-d", "-f", file_path, ">", dump_file_path], shell=True)
	print result

	return 0

	
def verify_zero_file(dump_file_path):
	f = open(dump_file_path , "r")
	lines = f.readlines()
	f.close()

	for line in lines:
		line = line.strip()
		#print line
		m = re.search( r"shit", line, flags=re.IGNORECASE )
		if m:
			logging.debug("find error:%s" % (line))
			return 1

	return 0

	
def do_sleep(sleep_time):
	time.sleep(sleep_time)
	return 0


def delete_agentbvt_vm():
    x = secureCloud.managementAPI.mapi_lib.mapi_lib(auth_type="api_auth")
    xml_result = x.listVM()
    vm_list = xml_result.getElementsByTagName("vmList")[0]
    vms = vm_list.getElementsByTagName("vms")[0]
    all_vm = vms.getElementsByTagName("vm")
    current = None
    for vm in all_vm:
        current_vm_name = vm.attributes["imageName"].value.strip()
        m = re.search(r"AgentAPI.agentBVT3", current_vm_name, flags=re.IGNORECASE)
        if m:
            vm_guid = vm.attributes["imageGUID"].value.strip()
            print("deleting vm name:%s, guid:%s" % (current_vm_name, vm_guid))

            xml_result = x.readVM(vm_guid)
            if xml_result:
                vm_node = xml_result.getElementsByTagName("vm")[0]
                devices_node = vm_node.getElementsByTagName("devices")[0]
                devices = devices_node.getElementsByTagName("device")
                for device in devices:
                    current_device = device.attributes["name"].value.strip()
                    current_msuid = device.attributes["msUID"].value.strip()
                    logging.debug("current device:%s" % (current_device))
                    logging.debug("current device msuid :%s" % (current_msuid))
                    result = x.deleteDeviceKey(vm_guid, current_msuid)
                    logging.debug("delete device key result:" + str(result))
                    # if not result:
                    #	return 1

                result = x.deleteVM(vm_guid)
                print("delete VM result:" + str(result))


def check_device_state(config_xml_path):
    f = open(config_xml_path)
    root_device_info = {}
    for line in f:
        #print line
        m = re.match(".*\sdeviceName=\"(.+?)\"\sguid=\"(.+?)\"\smbrSignature=\"(.+?)\"\sprovisioningState=\"(.+?)\"\sdiskType=\"(.+?)\"\sphysicalLocation=\"(.+?)\">", line)

        if m and m.group(5) == "root":
            root_device_info = {"name": m.group(1), "state": m.group(4)}
            logging.debug(m.group(1))
            logging.debug(m.group(4))
            print root_device_info
    if root_device_info:
        if root_device_info["state"] == "encrypted":
            logging.info("root device state: %s" % root_device_info["state"])
            return 0
        else:
            logging.info("root device state: %s" % root_device_info["state"])
            return 1
    else:
        logging.info("root device not found")
        return 2

def check_ssh_port(client_ip):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((client_ip, 99))
    except Exception, e:
        logging.info(e)
        print e

def calculate_speed():
    pass


def setup_proxy(tc_scconfig, proxy_setting):
    """
    Sample
    scconfig.sh -y "proxy_setting"
    scconfig.sh -y test
    """

    command = """ "%s" -y %s """ % (tc_scconfig, proxy_setting)
    logging.debug(command)
    process = subprocess.Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
    output = process.communicate()
    logging.debug(output[0])

    return_code = process.returncode
    logging.debug("return code:" + str(return_code))

    command = """ "%s" -y test """ % (tc_scconfig)
    logging.debug(command)

    process = subprocess.Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
    output = process.communicate()
    logging.debug(output[0])

    return_code = process.returncode
    logging.debug("return code:" + str(return_code))

    m = re.search(r"Connection OK", output[0])
    if m:
        return 0

    return 1




def remove_proxy(tc_scconfig):
    """
    Sample
    scconfig.sh -y remove
    """

    command = """ "%s" -y remove """ % (tc_scconfig)
    logging.debug(command)

    process = subprocess.Popen(command, shell=True, stdout=PIPE, stderr=PIPE)
    output = process.communicate()
    logging.debug(output[0])

    return_code = process.returncode
    logging.debug("return code:" + str(return_code))

    if return_code:
        return 0
    else:
        return 1



if __name__ == '__main__':
    # fp = "C:\\STAF\\data\\agentBVT\\agentInstall\\logger_linux_kh_test.ini"
    # ini_update(fp, "kh_test", "level", "1299993456")
    
    if len(sys.argv) == 2:
        if sys.argv[1] == "--clean":
            delete_agentbvt_vm()
        else:
            print "--clean\t clean up agentbvt vm"
    # vm_name = "AgentBVT-ESX-RHEL-62-x86"
    # print get_vm_guid(vm_name)
    # print delete_vm(vm_name)


    #ret = check_config_xml(r"C:\Users\kuanhung_chen\Desktop\config.xml")
    #print ret
    #check_ssh_port("172.18.0.152")

    #print_vm("agentBVT-cent62-x64-lvm")

    
    vm_name = "agentBVT-cent62-x64-lvm"
    raid_name="createRAID_raid"
    device_id_list = ["/dev/sdg","/dev/sdf"]
    raid_level="RAID0"
    raid_fs="ext3"
    raid_desc="this is test raid"
    mount_point="/mnt/test_raid"
    #print create_RAID(vm_name, raid_name, raid_level, raid_fs, device_id_list, raid_desc, mount_point)

    #encrypt_RAID("agentBVT-cent62-x64-lvm", "createRAID_raid")


    vm_name = "agentBVT-cent62-x64-lvm"
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
    security_rule = "%s,%s,%s#%s" % ("Key Request Date", "MatchAll", "equalGreaterThan", "06/01/2012")
    security_rule_list=[security_rule]

    """
    print create_policy(vm_name, EnableIC, ICAction, PostponeEnable, RevokeIntervalNumber, \
                    RevokeIntervalType, policy_name, isResourcePool, description, \
                    successAction, successActionDelay, failAction, failActionDelay, security_rule_list)
    """


    #print_runningVM()

    #get_runningVM_id_status("agentBVT-cent62-x64-lvm")


    #handle_key_request("agentBVT-cent62-x64-lvm", "approve")

    #check_device_existing("agentbvt-ub1310-x86-lvm", "/dev/sdb")