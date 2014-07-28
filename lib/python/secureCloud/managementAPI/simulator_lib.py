import os
import re
import time
import sys
import random
import string
import shutil
import glob
import logging
import getopt
import subprocess
from xml.dom.minidom import parse, parseString
from threading import *
import broker_api
import mapi_config

logging.basicConfig(level=mapi_config.log_level)

AGENT_PATH = mapi_config.simulator_path
WORK_PATH = mapi_config.simulator_work_path
CONFIG_CLEAR_LOG = mapi_config.simulator_clear_log


##############################################################################

# Helper functions

def nice_format(input):
    xmlstr = parseString(input)
    pretty_res = xmlstr.toprettyxml()

    return pretty_res

def check_existing_node(nodes, id):

    for node in nodes:
        current_id = node.getAttribute("id")
        if(current_id == id):
            return True

    return False

def get_node(nodes, id):

    for node in nodes:
        current_id = node.getAttribute("id")
        if(current_id == id):
            return node

def get_time(given_time=None):
    ISOTIMEFORMAT="%Y-%m-%d %H:%M:%S"

    if given_time:
        return time.strftime(ISOTIMEFORMAT, time.localtime(given_time))
    else:
        start_time = time.time()
        #print "start time:" + time.strftime(ISOTIMEFORMAT, time.localtime(start_time))
        return time.strftime(ISOTIMEFORMAT, time.localtime(start_time))

def get_random(num_digits):
    return string.join(random.sample(['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','1','2','3','4','5','6','7','8','9'], num_digits)).replace(" ","")



# Main functions

def create_config(config_name, csp_provider, csp_zone, image_id, device_id_list, account_id="", api_url="", api_passphrase=""):

    mapi_lib = broker_api.broker_api()

    if not account_id:
        account_id = mapi_lib.api_account_id
    if not api_passphrase:
        api_passphrase = mapi_lib.api_passphrase
    if not api_url:
        api_url = mapi_lib.sim_api_url


    agent_config = WORK_PATH + config_name + ".xml"

    agent_data = """<?xml version="1.0"?>
<root>
  <devices>
   </devices>
  <images>
  </images>
  <providers>
  </providers>
  <Settings>
    <MainFormSetting accountID="%s" agentAPIURI="%s/Agent/API.svc/" agentVersion="2.0" imageID="" passphrase="%s" provider="temp_csp" provisionAPIURI="%s/Provisioning/API.svc/" service="QA" zone="temp_zone" />
  </Settings>
  <message>
    <headers />
  </message>
</root>""" % (account_id, api_url, api_passphrase, api_url)


    dom_obj = parseString(agent_data)
    root_node = dom_obj.getElementsByTagName("root")[0]
    devices = root_node.getElementsByTagName("devices")[0]
    device = devices.getElementsByTagName("device")
    
    images = root_node.getElementsByTagName("images")[0]
    image = images.getElementsByTagName("image")

    providers = root_node.getElementsByTagName("providers")[0]
    provider = root_node.getElementsByTagName("provider")


    # create a csp
    new_csp_node = dom_obj.createElement("provider")
    new_zones_node = dom_obj.createElement("zones")
    new_zone_node = dom_obj.createElement("zone")

    new_csp_node.setAttribute("id", csp_provider)
    new_csp_node.setAttribute("isSelfProvision", "False")

    new_zone_node.setAttribute("id", csp_zone)
    new_zones_node.appendChild(new_zone_node)
    new_csp_node.appendChild(new_zones_node)
    
    is_existing = check_existing_node(provider, csp_provider)
    if(not is_existing):
        providers.appendChild(new_csp_node)


    new_device_list = []
    # create device
    if device_id_list is not None:
        for device_id in device_id_list:
            device_name = device_id
            device_provider = csp_provider
            device_zone = csp_zone
            device_mount_point = "/mnt/" + device_id
            device_file_system = "EXT3"
            device_access_type = "ReadWrite"
            device_state = "Unknown"
            device_kms = "qa"
            device_km_type = "LUKS"
            device_iv = "Plain"
            device_cipher = "AES"
            device_key_size = "128"
            device_mode = "CBC"
            device_capacity = "1G"
            device_info = ""
            device_parentImageId = image_id
            device_AutomationProvisionDevice = "False"

            new_device_node = dom_obj.createElement("device")  
            new_device_node.setAttribute("id", device_id)
            new_device_node.setAttribute("name", device_name)
            new_device_node.setAttribute("provider", device_provider)
            new_device_node.setAttribute("zone", device_zone)
            new_device_node.setAttribute("mountPoint", device_mount_point)
            new_device_node.setAttribute("fileSystemType", device_file_system)
            new_device_node.setAttribute("accessType", device_access_type)
            new_device_node.setAttribute("state", device_state)
            new_device_node.setAttribute("kms", device_kms)
            new_device_node.setAttribute("kmType", device_km_type)
            new_device_node.setAttribute("iv", device_iv)
            new_device_node.setAttribute("cipher", device_cipher)
            new_device_node.setAttribute("keySize", device_key_size)
            new_device_node.setAttribute("mode", device_mode)
            new_device_node.setAttribute("capacity", device_capacity)
            new_device_node.setAttribute("info", device_info)
            new_device_node.setAttribute("parentImageId", device_parentImageId)
            new_device_node.setAttribute("AutomationProvisionDevice", device_AutomationProvisionDevice)

            
            is_existing = check_existing_node(device, device_id)
            if(not is_existing):
                devices.appendChild(new_device_node)
                new_device_list.append(new_device_node)

                #new_image_device_node = new_device_node.cloneNode(True)
                #image.appendChild(new_image_device_node)



    # create an image
    image_name = image_id
    image_provider = csp_provider
    image_zone = csp_zone
    image_imageId = ""
    image_state = "unknown"
    image_kms = "qa"
    image_os = "RedHat Enterprise Linux 5 x86"
    image_version = "2"
    image_arch = "x86_32"
    image_info = ""

    new_image_node = dom_obj.createElement("image")  
    new_image_node.setAttribute("id", image_id)
    new_image_node.setAttribute("name", image_name)
    new_image_node.setAttribute("provider", image_provider)
    new_image_node.setAttribute("zone", image_zone)
    new_image_node.setAttribute("imageId", image_imageId)
    new_image_node.setAttribute("state", image_state)
    new_image_node.setAttribute("kms", image_kms)
    new_image_node.setAttribute("os", image_os)
    new_image_node.setAttribute("version", image_version)
    new_image_node.setAttribute("arch", image_arch)
    new_image_node.setAttribute("info", image_info)
    

    new_credential_node = dom_obj.createElement("credentialKey")
    new_credential_node.setAttribute("name", "cred-0")
    new_credential_node.setAttribute("length", "50")
    new_image_node.appendChild(new_credential_node)

    is_existing = check_existing_node(image, image_id)
    if(not is_existing):
        for new_device in new_device_list:
            new_image_device_node = new_device_node.cloneNode(True)
            new_image_node.appendChild(new_image_device_node)

        images.appendChild(new_image_node)

    new_agent_data = dom_obj.toxml()
    #print new_agent_data

    f = open(agent_config, "w")
    f.write(new_agent_data)
    f.close()

    #time.sleep(2)


def call_agent(agent_temp_script, agent_command, agent_config, action):

    logging.debug("START-%s" % action)

    logging.debug("Agent Command:%s" % (agent_command))
    f = open(agent_temp_script, "w")
    f.write(agent_command)
    f.close()
    #time.sleep(2)

    temp = "%s -c \"%s\" \"%s\" " % (AGENT_PATH, agent_config, agent_temp_script)
    logging.debug("Executing:%s" % (temp))

    #proc = subprocess.Popen(temp, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    proc = subprocess.Popen(temp, shell=True)
    stdout_value, stderr_value = proc.communicate()

    if stderr_value:
        logging.debug("STDERR:")
        logging.debug(stderr_value)
        
    if stdout_value:
        logging.debug("STDOUT:")
        logging.debug(stdout_value)
     
    logging.debug("END-%s" % action)


def upload_inventory(config_name, image_id):
    agent_config = WORK_PATH + config_name + ".xml"

    # Register Image
    agent_temp_script = WORK_PATH + "temp_" + config_name + ".txt"
    agent_command = "CreateSession\r\n RegisterImage %s \r\n exit \r\n" % (image_id)
    call_agent(agent_temp_script, agent_command, agent_config, "RegisterImage")

    # Publish Inventory
    agent_temp_script = WORK_PATH + "temp_" + config_name + ".txt"
    agent_command = "CreateSession\r\n PublishInventory -i %s \r\n exit \r\n" % (image_id)
    call_agent(agent_temp_script, agent_command, agent_config, "PublishInventory")



def encrypt_device(config_name, image_id, device_id_list):
    agent_config = WORK_PATH + config_name + ".xml"

    # Get Provision Action
    agent_temp_script = WORK_PATH + "temp_" + config_name + ".txt"
    agent_command = "CreateSession\r\n GetProvisionAction -i %s \r\n exit \r\n" % (image_id)
    call_agent(agent_temp_script, agent_command, agent_config, "GetProvisionAction")

    str_device_id = ""
    for device_id in device_id_list:
        str_device_id += device_id + " "

    # Encrypt devices
    agent_temp_script = WORK_PATH + "temp_" + config_name + ".txt"
    agent_command = "CreateSession\r\n EncryptDevice -i %s %s \r\n exit \r\n" % (image_id, str_device_id)
    call_agent(agent_temp_script, agent_command, agent_config, "EncryptDevice")



def create_instance(config_name, image_id, instance_id=""):
    
    agent_config = WORK_PATH + config_name + ".xml"

    if instance_id == "":
        instance_id = "inst-" + image_id

    # get mount list
    agent_temp_script = WORK_PATH + "temp_" + config_name + ".txt"
    agent_command = "CreateSession\r\n GetMountList -i %s \r\n  exit \r\n" % (image_id)
    call_agent(agent_temp_script, agent_command, agent_config, "CreateInstance")


    # create instance
    agent_temp_script = WORK_PATH + "temp_" + config_name + ".txt"
    agent_command = "CreateSession\r\n CreateInstance -i %s %s \r\n  exit \r\n" % (image_id, instance_id)
    #agent_command = "CreateSession\r\n CreateInstance -i %s %s \r\n  ShowInstance \r\n TerminateInstance %s \r\n exit \r\n" % (image_id, instance_id, instance_id)
    call_agent(agent_temp_script, agent_command, agent_config, "CreateInstance")




#clean up 
if CONFIG_CLEAR_LOG:
    for filename in glob.glob(WORK_PATH + "*.log"):
        os.remove(filename)
        
    for filename in glob.glob(WORK_PATH + "csp*.xml"):
        os.remove(filename)

    for filename in glob.glob(WORK_PATH + "temp*.txt"):
        os.remove(filename)

    for filename in glob.glob(WORK_PATH + "*.err"):
        f = open(filename, "r")
        error_log = f.read()
        print filename
        print error_log
        f.close()

        os.remove(filename)


if __name__ == '__main__':
    config_name="test1"
    csp_provider="test_csp1"
    csp_zone="test_zone1"
    image_id="test_image1"
    device_id_list=["test1_device1"]
    create_config(config_name, csp_provider, csp_zone, image_id, device_id_list)
    upload_inventory(config_name, image_id)
    encrypt_device(config_name, image_id, device_id_list)
    #create_instance(config_name, image_id)