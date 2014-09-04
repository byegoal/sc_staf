import sys
import hmac
import base64
import urllib2
import xml
import ConfigParser
import time
import logging
import mapi_util
import mapi_config
import os
from socket import error as SocketError
import errno
try:
    import hashlib
except ImportError:
    print("import hashlib error")
try:
    from tomcrypt import rsa
except ImportError:
    print("import tomcrypt error")
logging.basicConfig(level=mapi_config.log_level)
WORK_PATH = mapi_config.broker_api_work_path
CONFIG_PATH = mapi_config.broker_api_config_path
import secureCloud.config.result_config
import secureCloud.scAgent.file
chefLogger = secureCloud.config.result_config.chefLogger
errorLogger = secureCloud.config.result_config.errorLogger
stafLogger = secureCloud.config.result_config.stafLogger
class broker_api:

    def __init__(self, auth_type=None, broker=None, broker_passphrase=None, realm=None, access_key_id=None,
        secret_access_key=None, api_account_id=None, api_passphrase=None, user_name=None, user_pass=None, no_init=False):

        if no_init:
            conf = self.config()
            self.base_url = conf['base_url']
            self.sim_api_url = conf['sim_api_url']
        else:
            conf = self.config()
            self.base_url = conf['base_url']
            self.sim_api_url = conf['sim_api_url']
            self.auth_type = auth_type
            self.session_token = ""
            self.access_key_id = ""
            self.secret_access_key = ""
            self.user_name = ""
            self.user_pass = ""

            if broker is None:
                self.broker = conf['brokername']
            else:
                self.broker = broker

            if broker_passphrase is None:
                self.broker_passphrase = conf['broker_passphrase']
            else:
                self.broker_passphrase = broker_passphrase

            if realm is None:
                self.realm = conf["realm"]
            else:
                self.realm = realm

            if api_account_id is None:
                self.api_account_id = conf["api_account_id"]
            else:
                self.api_account_id = api_account_id

            if api_passphrase is None:
                self.api_passphrase = conf["api_passphrase"]
            else:
                self.api_passphrase = api_passphrase

            if self.auth_type == "api_auth":
                if access_key_id is None:
                    self.access_key_id = conf['access_key_id']
                else:
                    self.access_key_id = access_key_id

                if secret_access_key is None:
                    self.secret_access_key = conf['secret_access_key']
                else:
                    self.secret_access_key = secret_access_key

            elif self.auth_type == "basic_auth":
                if user_name is None:
                    self.user_name = conf["user_name"]
                else:
                    self.user_name = user_name

                if user_pass is None:
                    self.user_pass = conf["user_pass"]
                else:
                    self.user_pass = user_pass

            #logging.debug("auth_type=%s, broker=%s, broker_passphrase=%s, realm=%s, access_key_id=%s, secret_access_key=%s, api_account_id=%s, api_passphrase=%s, user_name=%s, user_pass=%s" % (self.auth_type, self.broker, self.broker_passphrase, self.realm, self.access_key_id, self.secret_access_key, self.api_account_id, self.api_passphrase, self.user_name, self.user_pass))


    def config(self):
        c = ConfigParser.SafeConfigParser()
        #print "config_path: %s" % CONFIG_PATH
        c.read(CONFIG_PATH)
        d = {}
        for key, val in c.items('sc'):
            d[key] = val
        return d

    def init_sim_config(self):
        conf = self.config()
        self.sim_api_url = conf['sim_api_url']
        self.api_account_id = conf["api_account_id"]
        self.api_passphrase = conf["api_passphrase"]


    def api_key_auth(self):
        auth_id, random_data = self.userAuthenticationRequest()
        if not auth_id:
            return False

        session_token = self.userAuthenticationResponse(auth_id, random_data)
        stafLogger.debug("2. session_token=%s"%self.session_token)
        #logging.debug("session_token:%s" % (session_token))
        
        if not session_token:
            errorLogger.error("userAuthetication Response is null")
            return False

        return session_token

    def userAuthenticationRequest(self):
        # need '/' to avoid 307 Temporary Redirect
        auth_url = self.base_url+ '/userAuth/' + self.access_key_id + "/"
        pwd_mgr = urllib2.HTTPPasswordMgr()
        pwd_mgr.add_password(self.realm, auth_url, self.broker, self.broker_passphrase)
        opener = urllib2.build_opener()
        opener.add_handler(urllib2.HTTPDigestAuthHandler(pwd_mgr))

        #logging.debug(auth_url)
        req = urllib2.Request(auth_url)
        req.add_header('Content-Type', 'application/xml; charset=utf-8')
        req.add_header('BrokerName', self.broker)

        try:
            sc_get_req = opener.open(req)
        except urllib2.HTTPError, e:
            logging.error(e)
            errorLogger.error(e)
            return False, False
        except urllib2.URLError, e:
            logging.error(e)
            errorLogger.error(e)
            return False, False
        except SocketError, e:
            if e.errno != errno.ECONNRESET:
                errorLogger.error('userAuthenticationRequest Error, message=%s'%e)
                return False, False

        try:
            res = sc_get_req.read()
            stafLogger.debug("userAuthenticationRequest sc_res=%s"%str(res))
            xmldata = xml.dom.minidom.parseString(res)
            auth_result = xmldata.getElementsByTagName("authentication")[0]
            auth_id = auth_result.attributes["id"].value.strip()
            random_data = auth_result.attributes["data"].value.strip()
            #print "Get Challenge:\nid = %s\nrandom_data = %s\n" % (auth_id, randata)
        except Exception, e:
            logging.error(e)
            errorLogger.error(e)
            return False, False

        #logging.debug("auth_id:%s, random_data:%s" % (auth_id, random_data))
        return auth_id, random_data


    def userAuthenticationResponse(self, auth_id, random_data, use_external_data=False, random_data_sensitive=False):

        if use_external_data:
            signature = random_data
        else:
            # get signature with secret_key and randata
            dig = hmac.new(self.secret_access_key, base64.b64decode(random_data), digestmod=hashlib.sha256).digest()
            signature = base64.b64encode(dig)
            #print "Decode randata, HMAC with secret_key, calc signature = %s\n" % signature

        if random_data_sensitive:
            signature = signature.upper()


        # get auth token
        res_xml = """<?xml version="1.0" encoding="utf-8"?><authentication id="%s" data="%s" accountId="%s" />""" % (auth_id, signature, self.api_account_id)
        #logging.debug(res_xml)

        # need '/' to avoid 307 Temporary Redirect
        auth_url = self.base_url+ '/userAuth/' + self.access_key_id + "/"
        #logging.debug(auth_url)
        pwd_mgr = urllib2.HTTPPasswordMgr()
        pwd_mgr.add_password(self.realm, auth_url, self.broker, self.broker_passphrase)
        opener = urllib2.build_opener()
        opener.add_handler(urllib2.HTTPDigestAuthHandler(pwd_mgr))
        #stafLogger.debug("auth_url=%s, broker name=%s, broker_passphrase=%s, realm=%s"%(auth_url,self.broker,self.broker_passphrase,self.realm))
        req = urllib2.Request(auth_url)
        req.add_header('Content-Type', 'application/xml; charset=utf-8')
        req.add_header('BrokerName', self.broker)
        req.add_data(res_xml)

        try:
            sc_get_req = opener.open(req)
        except urllib2.HTTPError, e:
            logging.error(e)
            errorLogger.error("userAuthenticationResponse error:%"%e)
            return False
        except urllib2.URLError, e:
            logging.error(e)
            errorLogger.error("userAuthenticationResponse error:%"%e)
            return False

        res = sc_get_req.read()
        stafLogger.debug("api response:%s" % str(res))
        xmldata = xml.dom.minidom.parseString(res)
        auth_result = xmldata.getElementsByTagName("authenticationResult")[0]
        session_token = auth_result.attributes["token"].value.strip()
        stafLogger.debug("api response, session_token:%s" % (session_token))
        #logging.debug("session token : %s" % session_token)

        return session_token


    def basic_auth(self, encrypt_pass=True):

        if encrypt_pass:
            # get server's public key
            pubkey = self.get_certificate()
            if not pubkey:
                return False

            from tomcrypt import rsa

            # encrypt user password
            key = rsa.Key(pubkey)
            pub = key.public
            #print pub.as_string()

            password = bytes(self.user_pass)
            encrypted_password = pub.encrypt(password, None, "sha256", "oaep")
            encrypted_password = base64.b64encode(encrypted_password)
        else:
            encrypted_password = self.user_pass

        req_xml = """<?xml version="1.0" encoding="utf-8"?><authentication xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" id="" data="%s" accountId="%s" />""" % (encrypted_password, self.api_account_id)
        #logging.debug(req_xml)

        auth_url = self.base_url+ 'userBasicAuth/' + self.user_name + "?tenant="
        logging.debug(auth_url)
        pwd_mgr = urllib2.HTTPPasswordMgr()
        pwd_mgr.add_password(self.realm, auth_url, self.broker, self.broker_passphrase)
        opener = urllib2.build_opener()
        opener.add_handler(urllib2.HTTPDigestAuthHandler(pwd_mgr))

        req = urllib2.Request(auth_url)
        req.add_header('Content-Type', 'application/xml; charset=utf-8')
        req.add_header('BrokerName', self.broker)
        req.add_data(req_xml)

        try:
            sc_get_req = opener.open(req)
        except urllib2.HTTPError, e:
            logging.error(e)
            return False
        except urllib2.URLError, e:
            logging.error(e)
            return False

        res = sc_get_req.read()
        #logging.debug(res)

        xmldata = xml.dom.minidom.parseString(res)
        auth_result = xmldata.getElementsByTagName("authenticationResult")[0]
        session_token = auth_result.attributes["token"].value.strip()
        #logging.debug("session token : %s" % session_token)

        return session_token


    def get_certificate(self):
        auth_url = self.base_url + "PublicCertificate/"

        req_xml = """<?xml version="1.0" encoding="utf-8"?><certificateRequest xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" version="2" />"""


        pwd_mgr = urllib2.HTTPPasswordMgr()
        pwd_mgr.add_password(self.realm, auth_url, self.broker, self.broker_passphrase)
        opener = urllib2.build_opener()
        opener.add_handler(urllib2.HTTPDigestAuthHandler(pwd_mgr))

        req = urllib2.Request(auth_url)
        req.add_header('Content-Type', 'application/xml; charset=utf-8')
        req.add_header('BrokerName', self.broker)

        try:
            sc_get_req = opener.open(req)
        except urllib2.HTTPError, e:
            logging.error(e)
            errorLogger.error(e)
            return False
        except urllib2.URLError, e:
            logging.error(e)
            errorLogger.error(e)
            return False

        res = sc_get_req.read()
        #logging.debug(res)

        try:
            xmldata = xml.dom.minidom.parseString(res)
            certificate_response = xmldata.getElementsByTagName("certificateResponse")[0]

            objWriteResponse = open("C:\\Documents and Settings\\Administrator\\Desktop\\response.txt","a")
            objWriteResponse.writelines(certificate_response)
            objWriteResponse.close()

            certificate_list = certificate_response.getElementsByTagName("certificateList")[0]

            objWriteResponse = open("C:\\Documents and Settings\\Administrator\\Desktop\\list.txt","a")
            objWriteResponse.writelines(certificate_list)
            objWriteResponse.close()

            certificate_node = certificate_response.getElementsByTagName("certificate")[0]

            objWriteResponse = open("C:\\Documents and Settings\\Administrator\\Desktop\\node.txt","a")
            objWriteResponse.writelines(certificate_node)
            objWriteResponse.close()

            certificate = mapi_util.getText(certificate_node)

            objWriteResponse = open("C:\\Documents and Settings\\Administrator\\Desktop\\certificate.txt","a")
            objWriteResponse.writelines(str(certificate))
            objWriteResponse.close()

            certificate = """-----BEGIN RSA PUBLIC KEY-----\n%s\n-----END RSA PUBLIC KEY-----\n""" % (certificate)
            certificate = str(certificate)


            #print certificate
        except Exception, e:
            logging.error(e)
            errorLogger.error(e)
            return False

        return certificate


    def sc_request(self, resource='', method='get', data=''):
      try:
         logging.debug("Start sc_request")
         stafLogger.debug("Start sc_request")
         if not self.session_token:
            if self.auth_type == "api_auth":
                self.session_token = self.api_key_auth()

            elif self.auth_type == "basic_auth":
                self.session_token = self.basic_auth()


         
         pwd_mgr = urllib2.HTTPPasswordMgr()
         api_url = self.base_url+'/'+resource+'/'
         pwd_mgr.add_password(self.realm, api_url, self.broker, self.broker_passphrase)
         opener = urllib2.build_opener()
         opener.add_handler(urllib2.HTTPDigestAuthHandler(pwd_mgr))

         req = urllib2.Request(api_url)

         logging.debug("url:%s" % (api_url))

         if method == 'post' and data != '':
            logging.debug(data)
            req.add_data(data)
         elif method == 'delete':
            req.get_method = lambda: 'DELETE'
         else:
            pass
        
         req.add_header('Content-Type', 'application/xml; charset=utf-8')
         req.add_header('BrokerName', self.broker)
         req.add_header('X-UserSession', self.session_token)
          #objWriteFile = open("C:\\Documents and Settings\\Administrator\\Desktop\\result.txt","a")
        #strWriteString = 'Content-Type', 'application/xml; charset=utf-8'+"\n"+"current request token: " +  self.session_token + "\ncurrent request BrokerName: " + self.broker + "\n"
        #objWriteFile.writelines(strWriteString)
        #objWriteFile.close()
        #stafLogger.debug("current request session_token:%s" % (self.session_token))
        #print "current request token:%s" % (self.session_token)
         try:
            sc_get_req = opener.open(req)

         except urllib2.HTTPError, e:
            logging.error(e)
            errorLogger.error("http error: %s"%e)
            return False
         except Exception, e:
            errorLogger.error("2.sc_request error: %s"%e)
            return False
         rawstr = sc_get_req.read()
         logging.debug("End sc_request")
         stafLogger.debug("End sc_request")
        #stafLogger.debug("request=%s"%rawstr)
         if(rawstr == ""):
            return True
         else:
            return rawstr
        
      except Exception, e:
            errorLogger.error("sc_request Error: %s"%e)
            time.sleep(0.5)
            return False

    def digest_authentication_test(self, realm, digest_broker_name, digest_broker_pass, header_broker_name):

        auth_url = self.base_url + "PublicCertificate/"

        req_xml = """<?xml version="1.0" encoding="utf-8"?><certificateRequest xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema" version="2" />"""
        #logging.debug(req_xml)

        pwd_mgr = urllib2.HTTPPasswordMgr()
        pwd_mgr.add_password(realm, auth_url, digest_broker_name, digest_broker_pass)
        opener = urllib2.build_opener()
        opener.add_handler(urllib2.HTTPDigestAuthHandler(pwd_mgr))

        req = urllib2.Request(auth_url)
        req.add_header('Content-Type', 'application/xml; charset=utf-8')
        req.add_header('BrokerName', header_broker_name)

        try:
            sc_get_req = opener.open(req)
        except urllib2.HTTPError, e:
            logging.error(e)
            return False
        except urllib2.URLError, e:
            logging.error(e)
            return False

        res = sc_get_req.read()
        logging.debug(res)

        if not res:
            return False

        return True


    # ---------------------------------------------------------------------

    # vm
    def listVM(self):
        result = self.sc_request(resource='vm/')
        return result

    def readVM(self, vm_guid):
        result = self.sc_request(resource='vm/'+vm_guid)
        return result
    def updateVM(self, vm_guid,update_data):
        result = self.sc_request(resource='vm/'+vm_guid,method="post",data=update_data)      
        return result
    def deleteDevice(self, vm_guid, device_guid):
        delete_url = "/vm/%s/device/%s/" % (vm_guid, device_guid)
        result = self.sc_request(resource=delete_url, method="delete")
        return result
    
    def deleteDeviceKey(self, vm_guid, device_guid):
        delete_url = "/vm/%s/device/%s/key/" % (vm_guid, device_guid)

        result = self.sc_request(resource=delete_url, method="delete")
        return result

    def cancelPending(self, vm_guid, device_guid):
        delete_url = "/vm/%s/device/%s/encrypt/" % (vm_guid, device_guid)

        result = self.sc_request(resource=delete_url, method="delete")
        return result
    
    def deleteVM(self, vm_guid):
        result = self.sc_request(resource='vm/'+vm_guid, method="delete")
        return result

    def runningVM(self):
        result = self.sc_request(resource='runningVM/')
        return result

    def createRAID(self, vm_guid, raid_data):
        request_url = "vm/%s/device/raid/" % (vm_guid)
        result = self.sc_request(resource=request_url, method="post", data=raid_data)
        return result

    def encryptRAID(self, vm_guid, raid_data):
        request_url = "vm/%s/encrypt/" % (vm_guid)
        result = self.sc_request(resource=request_url, method="post", data=raid_data)
        return result

    def runningVMKeyRequest(self, key_request_id, action):
        #python post body cannot be empty
        request_body = """<?xml version="1.0" encoding="utf-8"?>"""
        request_url = "runningVM/keyRequest/%s/%s/" % (key_request_id, action)
        result = self.sc_request(resource=request_url, method="post", data=request_body)
        return result
    
    def encryptVM(self, vm_guid,encrypt_data):
        request_url = "vm/%s/encrypt/" % (vm_guid)
        result = self.sc_request(resource=request_url, method="post", data=encrypt_data)
        return result









    # Legacy

    # image and device
    def cloneDevice(self, device_id, device_data):
        result = self.sc_request(resource='device/clone/'+device_id, method="post", data=device_data)
        return result

    def listAllDevices(self):
        result = self.sc_request(resource='device')
        return result

    def getDevice(self, device_id):
        result = self.sc_request(resource='device/'+device_id)
        return result

    def updateDevice(self, device_id, device_data):
        result = self.sc_request(resource='device/'+device_id, method="post", data=device_data)
        return result



    def encryptDevice(self, device_id, device_data):
        result = self.sc_request(resource='device/encrypt/'+device_id, method="post", data=device_data)
        return result

    def exportDevice(self, device_id, device_data):
        result = self.sc_request(resource='device/export/'+device_id, method="post", data=device_data)
        return result



    def readRAID(self, raid_id):
        result = self.sc_request(resource='device/raid/'+raid_id)
        return result

    def updateRAID(self, raid_id, raid_data):
        result = self.sc_request(resource='device/raid/'+raid_id, method="post", data=raid_data)
        return result

    def deleteRAID(self, raid_id):
        result = self.sc_request(resource='device/raid/'+raid_id, method="delete")
        return result

    def listAllImages(self):
        result = self.sc_request(resource='image')
        return result

    def getImage(self, image_id):
        result = self.sc_request(resource='image/'+image_id)
        return result

    def updateImage(self, image_id, image_data):
        result = self.sc_request(resource='image/'+image_id, method="post", data=image_data)
        return result

    def deleteImage(self, image_id):
        result = self.sc_request(resource='image/'+image_id, method="delete")
        return result

    def listAllProviders(self):
        result = self.sc_request(resource='provider')
        return result

    def getProvider(self, provider_id):
        result = self.sc_request(resource='provider/'+provider_id)
        return result

    # policy
    def createSecurityGroup(self, sg_data):
        result = self.sc_request(resource='securityGroup', method="post", data=sg_data)
        return result


    def listAllSecurityGroups(self):
        result = self.sc_request(resource='securityGroup')
        return result
    def getSecurityGroup(self, sg_id):
        result = self.sc_request(resource='securityGroup/'+sg_id)
        return result

    def updateSecurityGroup(self, sg_id, sg_data):
        result = self.sc_request(resource='securityGroup/'+sg_id, method="post", data=sg_data)
        return result

    def deleteSecurityGroup(self, sg_id):
        result = self.sc_request(resource="securityGroup/"+sg_id, method='delete')
        return result

    def getSecurityGroupSetting(self):
        result = self.sc_request(resource='securityGroupSetting')
        return result

    def putSecurityGroupSetting(self, sgs_data):
        result = self.sc_request(resource='securityGroupSetting', method="post", data=sgs_data)
        return result

    def listAllSecurityRules(self):
        result = self.sc_request(resource='securityRule')
        return result

    def getSecurityRule(self, sr_id):
        result = self.sc_request(resource='securityRule/'+sr_id)
        return result

    # instance and KR
    def getDeviceKeyRequest(self, kr_id):
        result = self.sc_request(resource='deviceKeyRequest/'+kr_id)
        return result

    def updateDeviceKeyRequest(self, dkr_id, dkr_data):
        result = self.sc_request(resource='deviceKeyRequest/'+dkr_id, method="post", data=dkr_data)
        return result

    def getInstance(self, instance_id):
        result = self.sc_request(resource='instance/'+instance_id)
        return result

    def flatRequests(self):
        result = self.sc_request(resource='keyRequestTree')
        return result

    def keyRequestTree(self, pattern):
        result = self.sc_request(resource='keyRequestTree/'+pattern)
        return result

    def listAllRuleResults(self, rule_id):
        result = self.sc_request(resource='ruleEvaluation/'+rule_id)
        return result

    def listLimitedRuleResults(self, rule_id, rule_pattern):
        result = self.sc_request(resource='ruleEvaluation/'+rule_id+"/"+rule_pattern)
        return result

    # account, users, rights, roles
    def listCurrentUserAccounts(self):
        result = self.sc_request(resource='accounts')
        return result


    def updateCurrentUsersAccount(self, account_id, account_data):
        result = self.sc_request(resource='accounts/'+account_id, method="post", data=account_data)
        return result

    def userRights(self):
        result = self.sc_request(resource='rights')
        return result

    def listAllRoles(self):
        result = self.sc_request(resource='roles')
        return result

    def createUser(self, user_data):
        result = self.sc_request(resource='user', method="post", data=user_data)
        return result

    def listAllUsers(self):
        result = self.sc_request(resource='user')
        return result

    def getCurrentUser(self):
        result = self.sc_request(resource='currentuser')
        return result

    def getUser(self, user_id):
        result = self.sc_request(resource='user/'+user_id)
        return result

    def updateUser(self, user_id, user_data):
        result = self.sc_request(resource='user/'+user_id, method="post", data=user_data)
        return result

    def deleteUser(self, user_id):
        result = self.sc_request(resource='user/'+user_id, method="delete")
        return result

    def getCurrentAccount(self):
        result = self.sc_request(resource='acctData')
        return result

    def updatePassphrase(self, passphrase):
        result = self.sc_request(resource='acctData/passphrase', method="post", data=passphrase)
        return result

    def updateAccountSettings(self, account_info):
        result = self.sc_request(resource='acctData/settings', method="post", data=account_info)
        return result

    def listTimezones(self):
        result = self.sc_request(resource='timezone')
        return result

    # No more
    """
    def readTimezone(time_zone_id):
        result = sc_request(resource='timezone/'+time_zone_id+"/")
        return result
    """

    def listLanguages(self):
        result = self.sc_request(resource='language')
        return result

    def getUserPreference(self):
        result = self.sc_request(resource='userPreference')
        return result

    def updateUserPreference(self, user_pref):
        result = self.sc_request(resource='userPreference', method="post", data=user_pref)
        return result

    def updateUserlogin(self, user_login, user_login_info):
        result = self.sc_request(resource='user/logintext/'+user_login, method="post", data=user_login_info)
        return result

    def updateRolesMFAMode(self, user_id, mfa_info):
        result = self.sc_request(resource='mfaroles', method="post", data=mfa_pref)
        return result

    def unregisterUserMFADevice(self, user_id):
        result = self.sc_request(resource='user/'+user_id+"/mfa", method="delete")
        return result


    # licenses
    def listLicenses():
        result = self.sc_request(resource='licenses')
        return result

    def getLicense(self, license_id):
        result = self.sc_request(resource='licenses/'+license_id)
        return result

    def addLicense(self, license_data):
        result = self.sc_request(resource='licenses', method="post", data=license_data)
        return result

    def updateLicense(self, license_id, license_data):
        result = self.sc_request(resource='licenses/'+license_id, method="post", data=license_data)
        return result

    def updateLicenseOnline(self, license_id, license_data=""):
        result = self.sc_request(resource='licenses/onlineupdate/'+license_id, method="post", data=license_data)
        return result

    # administration
    def readDSMConnSettings(self):
        result = self.sc_request(resource='dsmConnSettings')
        return result

    def updateDSMConnSettings(self, dsm_data):
        result = self.sc_request(resource='dsmConnSettings', method="post", data=dsm_data)
        return result

    def getKmipConnectionSetting(self):
        result = self.sc_request(resource='kmip/setting')
        return result

    def setKmipConnectionSetting(self, kmip_data):
        result = self.sc_request(resource='kmip/setting', method="post", data=kmip_data)
        return result

    # log
    def listLogGroups(self):
        result = self.sc_request(resource='LogGroups')
        return result

    def queryLog(self, log_data):
        result = self.sc_request(resource='LogQuery', method="post", data=log_data)
        return result

    def exportLogQuery(self, log_data):
        result = self.sc_request(resource='ExportLogQuery', method="post", data=log_data)
        return result

    def listLogArchives(self):
        result = self.sc_request(resource='LogArchive')
        return result

    def getLogArchive(self, log_id):
        result = self.sc_request(resource='LogArchive/'+log_id)
        return result

    def deleteLog(self, log_id):
        result = self.sc_request(resource='LogDelete/'+log_id, method="delete")
        return result

    # notify
    def createNotifier(self, notify_data):
        result = self.sc_request(resource='notifier', method="post", data=notify_data)
        return result

    def listAllNotifiers(self):
        result = self.sc_request(resource='notifier')
        return result

    def getNotificationEvents(self, notify_id):
        result = self.sc_request(resource='notifier/'+notify_id)
        return result

    def updateNotifier(self, notify_id, notify_data):
        result = self.sc_request(resource='notifier/'+notify_id, method="post", data=notify_data)
        return result

    def deleteNotifier(self, notify_id):
        result = self.sc_request(resource='notifier/'+notify_id, method="delete")
        return result

    # report
    def getReport(self, report_data):
        result = self.sc_request(resource='reports', method="post", data=report_data)
        return result

    def getTemplateList(self, report_type):
        result = self.sc_request(resource='reportscheduling/type/'+report_type)
        return result

    def deleteTemplate(self, template_id):
        result = self.sc_request(resource='reportscheduling/'+template_id, method="delete")
        return result

    def createTemplate(self, template_data):
        result = self.sc_request(resource='reportscheduling', method="post", data=template_data)
        return result

    def updateTemplate(self, template_id, template_data):
        result = self.sc_request(resource='reportscheduling/'+template_id, method="post", data=template_data)
        return result

    def loadTemplate(self, template_id):
        result = self.sc_request(resource='reportscheduling/'+template_id)
        return result

    def generateReport(self, report_data):
        result = self.sc_request(resource='reportscheduling/generate', method="post", data=report_data)
        return result

    def getReportList(self, report_type):
        result = self.sc_request(resource='reportarchive/type/'+report_type)
        return result

    def deleteReport(self, report_id):
        result = self.sc_request(resource='reportarchive/'+report_id, method="delete")
        return result

    def exportReport(self, report_data):
        result = self.sc_request(resource='reportarchive', method="post", data=report_data)
        return result

    # server status
    def getServerData():
        result = self.sc_request(resource='serverData')
        return result

    def serviceStatus():
        result = self.sc_request(resource='status')
        return result

    def getEntryPoint():
        result = self.sc_request(resource='entrypoint')
        return result

    # PLX
    def plxProfileSync(self, profile_data):
        result = self.sc_request(resource='plx/profsync', method="post", data=profile_data)
        return result

    def plxLicenseProvision(self, license_data):
        result = self.sc_request(resource='plx/licenseprov', method="post", data=license_data)
        return result










if __name__ == '__main__':

    #print getPolicies()

    # tested API
    #print readDSMConnSettings()
    #print listCurrentUserAccounts()
    #print userRights()
    #print listAllDevices()
    #print getDevice("91b3215b-afcc-4c63-a94c-51abfa600880")
    #print listAllImages()
    #print getImage("b8fbd0a3-efd6-411e-a212-9f2060222328")
    #print listLicenses()
    #print getLicense("372")
    #print listLogGroups()
    #print listAllNotifiers()
    #print getNotificationEvents("1027")
    #print listAllProviders()
    #print getProvider("amazon-ec2")
    #print listAllRoles()
    #print listAllSecurityGroups()
    #print getSecurityGroup("dd57b1c0-0a70-4201-9063-13a8da40ccae")
    #print getSecurityGroupSetting()
    #print listAllSecurityRules()
    #print getSecurityRule("e541d7c1-b681-4221-a2c0-68bfd87debaa")
    #print listAllUsers()
    #print getCurrentUser()
    #print getUser("d8dada6e-3ba6-4209-98a0-3340ff8ce0cb")
    #print getServerData()
    #print getCurrentAccount()
    #print listTimezones()
    #print getKmipConnectionSetting()

    #x = broker_api(auth_type="api_auth", broker="danny", broker_passphrase="ClOuD9", realm="securecloud@trend.com", access_key_id="grVAP1k5xBE3xUhVt7tO", secret_access_key="c1yiaB6l2MqkNChb3oDv7xtN7qeCl8B6LVdi3hDT", api_account_id="250C5CF1-62B6-4CDD-91C6-58F0307FE75E", api_passphrase="P@ssw0rd")
    #x = broker_api(auth_type="api_auth", access_key_id="grVAP1k5xBE3xUhVt7tO", secret_access_key="c1yiaB6l2MqkNChb3oDv7xtN7qeCl8B6LVdi3hDT", api_account_id="250C5CF1-62B6-4CDD-91C6-58F0307FE75E", api_passphrase="P@ssw0rd")
    #x = broker_api(auth_type="basic_auth", broker="danny", broker_passphrase="ClOuD9", realm="securecloud@trend.com", api_account_id="250C5CF1-62B6-4CDD-91C6-58F0307FE75E", user_name="shaodanny@gmail.com", user_pass="P@ssw0rd@123")
    #print x.session_token

    #x = broker_api(auth_type="basic_auth", user_name="danny3_shao@trend.com.tw", user_pass="P@ssw0rd@123",api_account_id="2F73B65D-99D2-47BE-A975-094D298D5A52")
    #x = broker_api(auth_type="basic_auth", user_name="shaodanny@gmail.com", user_pass="P@ssw0rd@123")
    #print x.listAllDevices()

    #realm = "securecloud@trend.com"
    #digest_broker_name = "danny"
    #digest_broker_pass = "ClOuD9"
    #header_broker_name = "danny"

    #x = broker_api(no_init=True)
    #print x.digest_authentication_test(realm, digest_broker_name, digest_broker_pass, header_broker_name)


    x = broker_api(auth_type="api_auth")
    print x.listVM()

    #image_guid = "6133b187-ab40-4a80-b1f1-3e794b272f9b"
    #print x.readVM(image_guid)



