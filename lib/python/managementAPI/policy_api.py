import xml.parsers.expat
import time
#from sc_management_api import get_auth_token, sc_request
from secureCloud.managementAPI import broker_api
from xml.dom import minidom

def createPolicy(policy_template):

    print "in policy_api createPolicy"
    print time.ctime()

    broker_api_obj = broker_api.broker_api(auth_type="api_auth", broker="", broker_passphrase="", realm="", access_key_id="", secret_access_key="", api_account_id="", api_passphrase="", user_name="", user_pass="")

    #result = sc_request(resource='securityGroup',method="post",data=policy_template)
    result = broker_api_obj.createSecurityGroup(policy_template)

    print "out policy_api createPolicy"
    print time.ctime()

    return result

def getKeyRequestTree():

    broker_api_obj = broker_api.broker_api(auth_type="api_auth", broker="", broker_passphrase="", realm="", access_key_id="", secret_access_key="", api_account_id="", api_passphrase="", user_name="", user_pass="")
    #result = sc_request(resource='keyRequestTree')
    result = broker_api_obj.flatRequests()
    return result
    
def deletePolicy(policy_id):
    print "in policy_api deletePolicy"
    print time.ctime()

    broker_api_obj = broker_api.broker_api(auth_type="api_auth", broker="", broker_passphrase="", realm="", access_key_id="", secret_access_key="", api_account_id="", api_passphrase="", user_name="", user_pass="")
    #result = sc_request(resource="securityGroup/"+policy_id, method='delete')
    result = broker_api_obj.deleteSecurityGroup(policy_id)

    print "out policy_api deletePolicy"
    print time.ctime()

    return result

def getPolicies():

    broker_api_obj = broker_api.broker_api(auth_type="api_auth", broker="", broker_passphrase="", realm="", access_key_id="", secret_access_key="", api_account_id="", api_passphrase="", user_name="", user_pass="")
    #result = sc_request(resource='securityGroup')
    result = broker_api_obj.listAllSecurityGroups()
    return result

def getDevices():

    broker_api_obj = broker_api.broker_api(auth_type="api_auth", broker="", broker_passphrase="", realm="", access_key_id="", secret_access_key="", api_account_id="", api_passphrase="", user_name="", user_pass="")
    #result = sc_request(resource='device')
    result = broker_api_obj.listAllDevices()
    return result

def getDevice(device_id):

    broker_api_obj = broker_api.broker_api(auth_type="api_auth", broker="", broker_passphrase="", realm="", access_key_id="", secret_access_key="", api_account_id="", api_passphrase="", user_name="", user_pass="")
    #result = sc_request(resource='device/'+device_id)
    result = broker_api_obj.getDevice(device_id)
    return result

def updateDevice(device_id, device_data):

    broker_api_obj = broker_api.broker_api(auth_type="api_auth", broker="", broker_passphrase="", realm="", access_key_id="", secret_access_key="", api_account_id="", api_passphrase="", user_name="", user_pass="")
    #result = sc_request(resource='device/'+device_id, method="post", data=device_data)
    result = broker_api_obj.updateDevice(device_id, device_data)
    return result

def encryptDevice(device_id, device_data):

    broker_api_obj = broker_api.broker_api(auth_type="api_auth", broker="", broker_passphrase="", realm="", access_key_id="", secret_access_key="", api_account_id="", api_passphrase="", user_name="", user_pass="")
    #result = sc_request(resource='device/encrypt/'+device_id, method="post", data=device_data)
    result = broker_api_obj.encryptDevice(device_id, device_data)
    return result

if __name__ == '__main__':

    print getPolicies()
