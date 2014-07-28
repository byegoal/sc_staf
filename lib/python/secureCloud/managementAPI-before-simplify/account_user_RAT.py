import time
import mapi_lib
import logging
import base64


#Todo API
"""
UpdateAccountSettings - imlement
updateCurrentUsersAccount - ?? how to switch account


userRights - verify method
listAllRoles - verify method
"""


account_user_log = logging.getLogger('account_user_logger')
account_user_log.setLevel(logging.DEBUG)
formatter = logging.Formatter('[%(levelname)s][%(filename)s][%(funcName)s][%(lineno)d]-%(message)s ')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
account_user_log.addHandler(handler)


def listCurrentUserAccounts(account_name):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	xml_result = broker_api_lib.listCurrentUserAccounts()
	if not xml_result:
		account_user_log.debug("call listCurrentUserAccounts return False")
		return False

	account_list = xml_result.getElementsByTagName("accountList")[0]
	accounts = account_list.getElementsByTagName("account")
	for account in accounts:
		if account_name == account.attributes["name"].value.strip():
			return True

	account_user_log.debug("account is not found")
	return False

def getCurrentAccount(account_name):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	xml_result = broker_api_lib.getCurrentAccount()
	if not xml_result:
		account_user_log.debug("call getCurrentAccount return False")
		return False
	
	account = xml_result.getElementsByTagName("account")[0]
	if account_name == account.attributes["name"].value.strip():
		return True
	else:
		account_user_log.debug("account is not found")
		return False


# todo implement UpdateAccountSettings
def updateCurrentUsersAccount(account_name, new_account_name):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	"""
	account_id = broker_api_lib.get_account_id_from_account_name(new_account_name)
	if not account_id:
		return False
	"""

	account_id = "81087E05-9C64-4BFA-BFE0-72407A398042"


	xml_result = broker_api_lib.updateCurrentUsersAccount(account_id)
	if not xml_result:
		return False

	"""
	account = xml_result.getElementsByTagName("account")

	xml_result = broker_api_lib.getCurrentAccount()
	if not xml_result:
		return False
	account_data = xml_result.getElementsByTagName("account")
	account_data = account_data[0]
	account_name = account_data.attributes["name"].value.strip()
	print account_name


	if account_name == new_account_name:
		return True
	else:
		return False
	"""

def userRights():
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	xml_result = broker_api_lib.userRights()
	if not xml_result:
		account_user_log.debug("call userRights return False")
		return False

	#Revise - how to check rights
	rights = xml_result.getElementsByTagName("userRights")
	if rights:
		return True
	else:
		account_user_log.debug("call userRights return False")
		return False


def listAllRoles():
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	xml_result = broker_api_lib.listAllRoles()
	if not xml_result:
		account_user_log.debug("call listAllRoles return False")
		return False


	#Revise - how to check roles
	roles = xml_result.getElementsByTagName("roleList")
	if roles:
		return True
	else:
		account_user_log.debug("no user role is found")
		return False


def listAllUsers(user_login_name):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	xml_result = broker_api_lib.listAllUsers()
	if not xml_result:
		account_user_log.debug("call listAllUsers return False")
		return False
	
	user_list = xml_result.getElementsByTagName("userList")[0]
	users = user_list.getElementsByTagName("user")
	for user in users:
		if user_login_name == user.attributes["loginname"].value.strip():
			return True

	account_user_log.debug("user is not found")
	return False

def getCurrentUser(user_login_name):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	xml_result = broker_api_lib.getCurrentUser()
	if not xml_result:
		account_user_log.debug("call getCurrentUser return False")
		return False
	
	user = xml_result.getElementsByTagName("user")[0]
	if user_login_name == user.attributes["loginname"].value.strip():
		return True

	account_user_log.debug("current user is not found")
	return False


def getUser(user_login_name):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	user_id = broker_api_lib.get_user_id_from_user_name(user_login_name)
	if not user_id:
		account_user_log.debug("no user with '%s' is found" % (user_login_name))
		return False
	
	xml_result = broker_api_lib.getUser(user_id)
	if not xml_result:
		account_user_log.debug("call getUser return False")
	user = xml_result.getElementsByTagName("user")[0]

	if user_login_name == user.attributes["loginname"].value.strip():
		return True

	account_user_log.debug("user is not found")
	return False


def createUser(login_name, login_pass, user_type, auth_type, is_license, first_name, last_name, email, user_role, mfa_status):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	#create user
	xml_result = broker_api_lib.createUser(login_name, base64.b64encode(login_pass), user_type, auth_type, is_license, first_name, last_name, email, user_role, mfa_status)
	if not xml_result:
		account_user_log.debug("call createUser return False")
		return False

	#get user ID
	user_id = broker_api_lib.get_user_id_from_user_name(login_name)
	if not user_id:
		account_user_log.debug("This user is not found")
		return False

	xml_result = broker_api_lib.getUser(user_id)
	if not xml_result:
		account_user_log.debug("call getUser return False")
	current_user = xml_result.getElementsByTagName("user")[0]

	#compare if the the user if the same
	is_same = broker_api_lib.compare_user(login_name, first_name, last_name, email, user_role, current_user)

	#delete user
	broker_api_lib.deleteUser(user_id)
	if not user_id:
		account_user_log.debug("Delete user failed")
		return False

	if is_same:
		return True
	else:
		return False



def updateUser(login_name, first_name, last_name, email, user_role):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	login_name = "auto_user_update@trend.com.tw"
	login_pass = base64.b64encode("P@ssw0rd")
	user_type = "localuser"
	auth_type = "localuser"
	is_license = "false"
	first_name_orig = "auto"
	last_name_orig = "user"
	email = "auto_user_update@trend.com.tw"
	user_role_orig = "Administrator"
	mfa_status = "false"

	#create user
	xml_result = broker_api_lib.createUser(login_name, login_pass, user_type, auth_type, is_license, first_name_orig, last_name_orig, email, user_role_orig, mfa_status)
	if not xml_result:
		account_user_log.debug("call createUser return False")
		return False


	#get user ID
	user_id = broker_api_lib.get_user_id_from_user_name(login_name)
	if not user_id:
		account_user_log.debug("This user is not found")
		return False


	xml_result = broker_api_lib.updateUser(user_id, first_name, last_name, email, user_role)
	if not xml_result:
		account_user_log.debug("call updateUser return False")
		return False


	xml_result = broker_api_lib.getUser(user_id)
	if not xml_result:
		account_user_log.debug("call getUser return False")
	current_user = xml_result.getElementsByTagName("user")[0]

	#compare if the the user if the same
	is_same = broker_api_lib.compare_user(login_name, first_name, last_name, email, user_role, current_user)


	#delete user
	broker_api_lib.deleteUser(user_id)
	if not user_id:
		account_user_log.debug("Delete user failed")
		return False

	if is_same:
		return True
	else:
		return False



def deleteUser(login_name):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")

	# Temp info for the deleted user
	login_name = "auto_user@trend.com.tw"
	login_pass = base64.b64encode("P@ssw0rd")
	user_type = "localuser"
	auth_type = "localuser"
	is_license = "false"
	first_name = "delete"
	last_name = "user"
	email = "auto_user_update@trend.com.tw"
	user_role = "Administrator"
	mfa_status = "false"

	#create user
	xml_result = broker_api_lib.createUser(login_name, login_pass, user_type, auth_type, is_license, first_name, last_name, email, user_role, mfa_status)
	if not xml_result:
		account_user_log.debug("call createUser return False")
		return False

	#get user ID
	user_id = broker_api_lib.get_user_id_from_user_name(login_name)
	if not user_id:
		account_user_log.debug("This user is not found")
		return False

	#delete user
	broker_api_lib.deleteUser(user_id)
	if not user_id:
		account_user_log.debug("Delete user failed")
		return False
	else:
		return True




def updatePassphrase(account_name, new_passphrase):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	#get account ID
	account_id = broker_api_lib.get_account_id_from_account_name(account_name)
	if not account_id:
		account_user_log.debug("Account is not found")
		return False

	#update account passphrase
	xml_result = broker_api_lib.updatePassphrase(account_id, new_passphrase)
	if not xml_result:
		account_user_log.debug("call updatePassphrase return False")
		return False

	#get current account information
	xml_result = broker_api_lib.getCurrentAccount()
	if not xml_result:
		account_user_log.debug("get current account information failed")
		return False

	account = xml_result.getElementsByTagName("account")[0]
	current_passphrase = account.attributes["passphrase"].value.strip()


	#Change back
	xml_result = broker_api_lib.updatePassphrase(account_id, "P@ssw0rd")
	if not xml_result:
		account_user_log.debug("Fail to change the passphrase back")
		return False


	#check if passphrase is updated
	if new_passphrase == current_passphrase:
		return True
	else:
		account_user_log.debug("Passphrase is not changed")
		return False



def listTimezones():
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	xml_result = broker_api_lib.listTimezones()
	if not xml_result:
		account_user_log.debug("call listTimezones return False")
		return False
	
	timezone_list = xml_result.getElementsByTagName("timezoneList")[0]
	if timezone_list:
		return True
	else:
		account_user_log.debug("no timezone data")
		return False



def readTimezone(timezone_id):
	"""
	print timezone_id
	encoded_timezone_id = urllib.quote(timezone_id)
	print encoded_timezone_id
	xml_result = broker_api_lib.readTimezone(encoded_timezone_id)
	if not xml_result:
		return False
	
	timezone = xml_result.getElementsByTagName("timezone")[0]
	if timezone_id == account.attributes["timezoneId"].value.strip():
		return True
	else:
		return False
	"""

	print "no more this API"

# Bug using API can change timeout more than 8 hrs
def updateAccountSettings(account_name, new_timezone, new_dateFormat, new_session_timeout):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	account_id = broker_api_lib.get_account_id_from_account_name(account_name)
	if not account_id:
		account_user_log.debug("no account is found with this account name")
		return False

	xml_result = broker_api_lib.updateAccountSettings(account_id, new_timezone, new_dateFormat, new_session_timeout)
	if not xml_result:
		account_user_log.debug("call updateAccountSettings return False")
		return False
	
	xml_result = broker_api_lib.getCurrentAccount()
	if not xml_result:
		account_user_log.debug("call getCurrentAccount return False")
		return False
	
	account_data = xml_result.getElementsByTagName("account")
	account_data = account_data[0]
	timezone = account_data.attributes["timezoneID"].value.strip()
	date_format = account_data.attributes["dateFormat"].value.strip()
	session_timeout = account_data.attributes["sessionTimeout"].value.strip()
	

	#change it back
	xml_result = broker_api_lib.updateAccountSettings(account_id, "Tokyo Standard Time", "dd/MM/yyyy", "480")
	if not xml_result:
		account_user_log.debug("Fail to change timezone back")
		return False


	if timezone == new_timezone and date_format == new_dateFormat and session_timeout == new_session_timeout:
		return True
	else:
		account_user_log.debug("account setting is not changed")
		account_user_log.debug("current timezone:%s, current date_format:%s, current session timeout" % (timezone, date_format), session_timeout)
		return False


def listLanguages():
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	xml_result = broker_api_lib.listLanguages()
	if not xml_result:
		account_user_log.debug("call listLanguages return False")
		return False
	
	language_list = xml_result.getElementsByTagName("languageList")[0]
	if language_list:
		return True
	else:
		account_user_log.debug("no language data")
		return False


def getUserPreference():
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	xml_result = broker_api_lib.getUserPreference()
	if not xml_result:
		account_user_log.debug("call getUserPreference return False")
		return False

	user_pref = xml_result.getElementsByTagName("userPreference")[0]
	language_code = user_pref.attributes["languageCode"].value.strip()
	if language_code:
		return True
	else:
		account_user_log.debug("no user preference")
		return False


def updateUserPreference(language_code):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	xml_result = broker_api_lib.updateUserPreference(language_code)
	if not xml_result:
		account_user_log.debug("call updateUserPreference return False")
		return False

	xml_result = broker_api_lib.getUserPreference()
	if not xml_result:
		account_user_log.debug("call getUserPreference return False")
		return False

	user_pref = xml_result.getElementsByTagName("userPreference")[0]
	current_language_code = user_pref.attributes["languageCode"].value.strip()

	# change back
	xml_result = broker_api_lib.updateUserPreference("en")
	if not xml_result:
		account_user_log.debug("call updateUserPreference return False")
		return False

	if language_code == current_language_code:
		return True
	else:
		account_user_log.debug("user preference is not updated")
		return False


def updateUserlogin(user_login, last_pass, new_pass):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")

	xml_result = broker_api_lib.updateUserlogin(user_login, base64.b64encode(last_pass), base64.b64encode(new_pass))
	if not xml_result:
		account_user_log.debug("call updateUserlogin return False")
		return False


if __name__ == '__main__':

	account_name="shaodanny@gmail.com"
	user_login_name = "shaodanny@gmail.com"
	account2_name="shaodanny+2@gmail.com"

	#print listCurrentUserAccounts(account_name)
	#print getCurrentAccount(account_name)
	#print userRights()
	#print listAllRoles()
	#print updateCurrentUsersAccount(account_name, account2_name)
	#print listAllUsers(user_login_name)
	#print getCurrentUser(user_login_name)
	#print getUser(user_login_name)


	login_name = "auto_user@trend.com.tw"
	login_pass = "P@ssw0rd"
	user_type = "localuser"
	auth_type = "localuser"
	is_license = "false"
	first_name = "auto"
	last_name = "user"
	email = "auto_user@trend.com.tw"
	user_role = "Administrator"
	mfa_status = "false"
	#print createUser(login_name, login_pass, user_type, auth_type, is_license, first_name, last_name, email, user_role, mfa_status)


	login_name = "auto_user_update@trend.com.tw"
	first_name = "auto_update"
	last_name = "user_update"
	email = "auto_user_update@trend.com.tw"
	user_role = "Security Administrator"
	#print updateUser(login_name, first_name, last_name, email, user_role)

	user_login_name = "auto_user@trend.com.tw"
	#print deleteUser(user_login_name)

	account_name = "shaodanny@gmail.com"
	new_passphrase = "P@ssw0rd@123"
	#print updatePassphrase(account_name, new_passphrase)


	#print listTimezones()

	timezone_id = "Taipei Standard Time"
	#print readTimezone(timezone_id)

	account_name = "shaodanny@gmail.com"
	new_timezone = "Taipei Standard Time"
	new_dateFormat = "yyyy/MM/dd"
	new_session_timeout = "960"
	#print updateAccountSettings(account_name, new_timezone, new_dateFormat, new_session_timeout)

	#print listLanguages()

	#print getUserPreference()

	language_code = "ja"
	#print updateUserPreference(language_code)

	user_login_name = "shaodanny@gmail.com"
	last_pass = "P@ssw0rd"
	new_pass = "P@ssw0rd@123"
	updateUserlogin(user_login_name, last_pass, new_pass)