import time
import logging
import base64
import mapi_lib
import mapi_util
import mapi_config
import urllib

#Todo API
"""
UpdateAccountSettings - imlement
updateCurrentUsersAccount - ?? how to switch account


userRights - verify method
listAllRoles - verify method
"""


logging.basicConfig(level=mapi_config.log_level)


def listCurrentUserAccounts(account_name):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	xml_result = broker_api_lib.listCurrentUserAccounts()
	if not xml_result:
		logging.debug("call listCurrentUserAccounts return False")
		return False

	account_list = xml_result.getElementsByTagName("accountList")[0]
	accounts = account_list.getElementsByTagName("account")
	for account in accounts:
		if account_name == account.attributes["name"].value.strip():
			return True

	logging.debug("account is not found")
	return False

def getCurrentAccount(account_name):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	xml_result = broker_api_lib.getCurrentAccount()
	if not xml_result:
		logging.debug("call getCurrentAccount return False")
		return False
	
	account = xml_result.getElementsByTagName("account")[0]
	if account_name == account.attributes["name"].value.strip():
		return True
	else:
		logging.debug("account is not found")
		return False




def userRights():
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	xml_result = broker_api_lib.userRights()
	if not xml_result:
		logging.debug("call userRights return False")
		return False

	#Revise - how to check rights
	rights = xml_result.getElementsByTagName("userRights")
	if rights:
		return True
	else:
		logging.debug("call userRights return False")
		return False


def listAllRoles():
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	xml_result = broker_api_lib.listAllRoles()
	if not xml_result:
		logging.debug("call listAllRoles return False")
		return False


	#Revise - how to check roles
	roles = xml_result.getElementsByTagName("roleList")
	if roles:
		return True
	else:
		logging.debug("no user role is found")
		return False


def listAllUsers(user_login_name):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	xml_result = broker_api_lib.listAllUsers()
	if not xml_result:
		logging.debug("call listAllUsers return False")
		return False
	
	user_list = xml_result.getElementsByTagName("userList")[0]
	users = user_list.getElementsByTagName("user")
	for user in users:
		if user_login_name == user.attributes["loginname"].value.strip():
			return True

	logging.debug("user is not found")
	return False

def getCurrentUser(user_login_name):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	xml_result = broker_api_lib.getCurrentUser()
	if not xml_result:
		logging.debug("call getCurrentUser return False")
		return False
	
	user = xml_result.getElementsByTagName("user")[0]
	if user_login_name == user.attributes["loginname"].value.strip():
		return True

	logging.debug("current user is not found")
	return False


def getUser(user_login_name, ext_id=False, case_sensitive=False):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")

	if ext_id:
		user_id = user_login_name
	else:
		user_id = broker_api_lib.get_user_id_from_user_name(user_login_name)
		if not user_id:
			logging.debug("no user with '%s' is found" % (user_login_name))
			return False

	if case_sensitive:
		user_id = user_id.upper()

	xml_result = broker_api_lib.getUser(user_id)
	if not xml_result:
		logging.debug("call getUser return False")
		return False


	user = xml_result.getElementsByTagName("user")[0]
	if user_login_name == user.attributes["loginname"].value.strip():
		return True

	logging.debug("user is not found")
	return False


def createUser(login_name, login_pass, user_type, first_name, last_name, email, user_role, mfa_status=None):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")

	#get user ID
	user_id = broker_api_lib.get_user_id_from_user_name(login_name)
	if user_id:
		#delete user
		result = broker_api_lib.deleteUser(user_id)
		if not result:
			logging.debug("Delete user failed")
			return False


	#create user
	xml_result = broker_api_lib.createUser(login_name, base64.b64encode(login_pass), user_type, first_name, last_name, email, user_role, mfa_status)
	if not xml_result:
		logging.debug("call createUser return False")
		return False

	#get user ID
	user_id = broker_api_lib.get_user_id_from_user_name(login_name)
	if not user_id:
		logging.debug("This user is not found")
		return False

	xml_result = broker_api_lib.getUser(user_id)
	if not xml_result:
		logging.debug("call getUser return False")
		return False
	
	current_user = xml_result.getElementsByTagName("user")[0]

	#compare if the the user if the same
	is_same = broker_api_lib.compare_user(login_name, first_name, last_name, email, user_role, current_user)

	"""
	#delete user
	result = broker_api_lib.deleteUser(user_id)
	if not result:
		logging.debug("Delete user failed")
		return False
	"""

	if is_same:
		return True
	else:
		return False



def updateUser(first_name, last_name, user_role):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")

	login_name_orig = "auto_user_orig@trend.com.tw"
	login_pass_orig = base64.b64encode("P@ssw0rd")
	user_type_orig = "localuser"
	first_name_orig = "auto_orig"
	last_name_orig = "user_orig"
	email_orig = "auto_user_orig@trend.com.tw"
	if user_role == "Administrator":
		user_role_orig = "Security Administrator"
	else:
		user_role_orig = "Administrator"


	#delete old test users
	user_id = broker_api_lib.get_user_id_from_user_name(login_name_orig)
	if user_id:
		#delete user
		result = broker_api_lib.deleteUser(user_id)
		if not result:
			logging.debug("Delete user failed")
			return False



	#create user
	xml_result = broker_api_lib.createUser(login_name_orig, base64.b64encode(login_pass_orig), user_type_orig, first_name_orig, last_name_orig, email_orig, user_role_orig)
	if not xml_result:
		logging.debug("call createUser return False")
		return False


	#get user ID
	user_id = broker_api_lib.get_user_id_from_user_name(login_name_orig)
	if not user_id:
		logging.debug("This user is not found")
		return False


	#xml_result = broker_api_lib.updateUser(user_id, first_name, last_name, user_role, email="auto_user_update@trend.com.tw", login_name="auto_user_update@trend.com.tw", login_pass=base64.b64encode("P@ssw0rd@123"), user_type="aduser")
	xml_result = broker_api_lib.updateUser(user_id, first_name, last_name, user_role)
	if not xml_result:
		logging.debug("call updateUser return False")
		return False		


	xml_result = broker_api_lib.getUser(user_id)
	if not xml_result:
		logging.debug("call getUser return False")
	current_user = xml_result.getElementsByTagName("user")[0]

	#compare if the the user if the same
	is_same = broker_api_lib.compare_user("", first_name, last_name, "", user_role, current_user)


	#delete user
	broker_api_lib.deleteUser(user_id)
	if not user_id:
		logging.debug("Delete user failed")
		return False

	if is_same:
		return True
	else:
		return False



def deleteUser(login_name, ext_id=False, case_sensitive=False):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")

	if ext_id:
		user_id = login_name
	else:
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

		#delete old test users
		user_id = broker_api_lib.get_user_id_from_user_name(login_name)
		if user_id:
			#delete user
			result = broker_api_lib.deleteUser(user_id)
			if not result:
				logging.debug("Delete user failed")
				return False

		#create user
		xml_result = broker_api_lib.createUser(login_name, login_pass, user_type, first_name, last_name, email, user_role, mfa_status)
		#xml_result = broker_api_lib.createUser(login_name, login_pass, user_type, auth_type, is_license, first_name, last_name, email, user_role, mfa_status)
		if not xml_result:
			logging.debug("call createUser return False")
			return False

		#get user ID
		user_id = broker_api_lib.get_user_id_from_user_name(login_name)
		if not user_id:
			logging.debug("This user is not found")
			return False

	if case_sensitive:
		user_id = user_id.upper()

	#delete user
	result = broker_api_lib.deleteUser(user_id)
	if not result:
		logging.debug("Delete user failed")
		return False

	#get user
	xml_result = broker_api_lib.getUser(user_id)
	if xml_result:
		logging.debug("the user is not deleted")
		return False

	return True


def updatePassphrase(account_name, new_passphrase, ext_account_id=False):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")

	if ext_account_id:
		account_id = account_name
	else:
		#get account ID
		account_id = broker_api_lib.get_account_id_from_account_name(account_name)
		if not account_id:
			logging.debug("Account is not found")
			return False

	#update account passphrase
	xml_result = broker_api_lib.updatePassphrase(account_id, new_passphrase)
	if not xml_result:
		logging.debug("call updatePassphrase return False")
		return False

	#get current account information
	xml_result = broker_api_lib.getCurrentAccount()
	if not xml_result:
		logging.debug("get current account information failed")
		return False

	account = xml_result.getElementsByTagName("account")[0]
	current_passphrase = account.attributes["passphrase"].value.strip()


	#Change back
	xml_result = broker_api_lib.updatePassphrase(account_id, "P@ssw0rd")
	if not xml_result:
		logging.debug("Fail to change the passphrase back")
		return False


	#check if passphrase is updated
	if new_passphrase == current_passphrase:
		return True
	else:
		logging.debug("Passphrase is not changed")
		return False



def listTimezones():
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	xml_result = broker_api_lib.listTimezones()
	if not xml_result:
		logging.debug("call listTimezones return False")
		return False
	
	timezone_list = xml_result.getElementsByTagName("timezoneList")[0]
	if timezone_list:
		return True
	else:
		logging.debug("no timezone data")
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



def listLanguages():
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	xml_result = broker_api_lib.listLanguages()
	if not xml_result:
		logging.debug("call listLanguages return False")
		return False
	
	language_list = xml_result.getElementsByTagName("languageList")[0]
	if language_list:
		return True
	else:
		logging.debug("no language data")
		return False


def getUserPreference():
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	xml_result = broker_api_lib.getUserPreference()
	if not xml_result:
		logging.debug("call getUserPreference return False")
		return False

	user_pref = xml_result.getElementsByTagName("userPreference")[0]
	language_code = user_pref.attributes["languageCode"].value.strip()
	if language_code:
		return True
	else:
		logging.debug("no user preference")
		return False


def updateUserPreference(language_code):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	xml_result = broker_api_lib.updateUserPreference(language_code)
	if not xml_result:
		logging.debug("call updateUserPreference return False")
		return False

	xml_result = broker_api_lib.getUserPreference()
	if not xml_result:
		logging.debug("call getUserPreference return False")
		return False

	user_pref = xml_result.getElementsByTagName("userPreference")[0]
	current_language_code = user_pref.attributes["languageCode"].value.strip()

	# change back
	xml_result = broker_api_lib.updateUserPreference("en")
	if not xml_result:
		logging.debug("call updateUserPreference return False")
		return False

	if language_code == current_language_code:
		return True
	else:
		logging.debug("user preference is not updated")
		return False




# ####################################################################################

# Bug using API can change timeout more than 8 hrs
def updateAccountSettings(account_name, new_timezone, new_dateFormat, new_session_timeout):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	account_id = broker_api_lib.get_account_id_from_account_name(account_name)
	if not account_id:
		logging.debug("no account is found with this account name")
		return False

	xml_result = broker_api_lib.updateAccountSettings(account_id, new_timezone, new_dateFormat, new_session_timeout)
	if not xml_result:
		logging.debug("call updateAccountSettings return False")
		return False
	
	xml_result = broker_api_lib.getCurrentAccount()
	if not xml_result:
		logging.debug("call getCurrentAccount return False")
		return False
	
	account_data = xml_result.getElementsByTagName("account")
	account_data = account_data[0]
	result = broker_api_lib.compare_account_setting(new_timezone, new_dateFormat, new_session_timeout, account_data)
	

	#change it back
	"""
	xml_result = broker_api_lib.updateAccountSettings(account_id, "Tokyo Standard Time", "dd/MM/yyyy", "480")
	if not xml_result:
		logging.debug("Fail to change timezone back")
		return False
	"""

	if result:
		return True
	else:
		logging.error("account setting is not changed")
		return False

def putTimeZoneForUpdateAccountSetting(account_name, new_dateFormat, new_session_timeout):

	dictTimeZone = mapi_config.TimeZone_mapping
	lstTimeZone = []
	for strDictKey in dictTimeZone:
		new_timezone = dictTimeZone[strDictKey]
		result = updateAccountSettings(account_name, new_timezone, new_dateFormat, new_session_timeout)
		if result == False:
			print "False"
			print account_name, new_timezone, new_dateFormat, new_session_timeout
			print "\n"
			break
		else:
			pass

	return result



def updateUserlogin(user_login, last_pass, new_pass):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")

	if last_pass == None:
		xml_result = broker_api_lib.updateUserlogin(user_login, last_pass, base64.b64encode(new_pass))
	elif new_pass == None:
		xml_result = broker_api_lib.updateUserlogin(user_login, base64.b64encode(last_pass), new_pass)
	else:
		xml_result = broker_api_lib.updateUserlogin(user_login, base64.b64encode(last_pass), base64.b64encode(new_pass))
	#xml_result = broker_api_lib.updateUserlogin(user_login, base64.b64encode(last_pass), base64.b64encode(new_pass))
	if not xml_result:
		logging.debug("call updateUserlogin return False")
		return False

	return True


# todo implement UpdateAccountSettings
def updateCurrentUsersAccount(account_name, new_account_name):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	"""
	account_id = broker_api_lib.get_account_id_from_account_name(new_account_name)
	if not account_id:
		return False
	"""

	#account_id = "81087E05-9C64-4BFA-BFE0-72407A398042"
	account_id = "EB43453B-4484-4DE4-AFDD-4B9C76E7D14C"
	
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



if __name__ == '__main__':

	# old unit test
	account_name="m318021@gmail.com"
	user_login_name = "m318021@gmail.com"
	account2_name="m318021@gmail.com"

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
	#updateUserlogin(user_login_name, last_pass, new_pass)



	# --------------------------------------

	# RAT
	account_name="shaodanny@gmail.com"
	#print listCurrentUserAccounts(account_name)

	# --------------------------------------

	# RAT	
	account_name="shaodanny@gmail.com"
	#print getCurrentAccount(account_name)

	# --------------------------------------

	# RAT	
	#print userRights()

	# --------------------------------------

	# RAT	
	#print listAllRoles()

	# --------------------------------------

	# RAT	
	user_login_name = "shaodanny@gmail.com"
	#print listAllUsers(user_login_name)

	# --------------------------------------

	# RAT	
	user_login_name = "shaodanny@gmail.com"
	#print getCurrentUser(user_login_name)

	# --------------------------------------

	# RAT
	"""
	user_name = "auto_user@trend.com.tw"
	"""
	#print getUser(user_name)

	# empty user ID
	# result: pass, return all users
	"""
	user_id = ""
	"""
	
	# user_id = "00000000-0000-0000-0000-000000000000"
	# result: fail,HTTP Error 400: Bad Request
	
	user_id = "00000000-0000-0000-0000-000000000000"
	
	
	# user_id = random 36 chars
	# result: fail,HTTP Error 400: Bad Request
	"""
	user_id = mapi_util.random_str(36)
	"""
	
	# user_id = special chars
	# result: fail,HTTP Error 401: Unauthorized
	"""
	user_id = mapi_util.SPECIAL_CHARS
	"""
	
	print getUser(user_id, ext_id=True)


	# user_id = case sensitive
	# result: pass
	"""
	user_name = "shaodanny@gmail.com"
	"""
	
	#print getUser(user_name, False, True)

	# --------------------------------------

	# RAT
	user_name = "auto_user@trend.com.tw"
	#print deleteUser(user_name)

	# empty user ID
	# result: fail,HTTP Error 405: Method Not Allowed
	"""
	user_id = ""
	"""
	
	# user_id = "00000000-0000-0000-0000-000000000000"
	# result: fail,HTTP Error 400: Bad Request
	"""
	user_id = "00000000-0000-0000-0000-000000000000"
	"""
	
	# user_id = random 36 chars
	# result: fail,HTTP Error 400: Bad Request
	"""
	user_id = mapi_util.random_str(36)
	"""
	
	# user_id = special chars
	# result: fail,HTTP Error 307: Temporary Redirect
	"""
	user_id = mapi_util.SPECIAL_CHARS
	"""
	
	#print deleteUser(user_id, True)


	# user_id = case sensitive
	# result: pass
	"""
	user_name = "auto_user@trend.com.tw"
	"""
	
	#print deleteUser(user_name, False, True)


	# --------------------------------------

	# RAT
	#print listTimezones()

	# --------------------------------------

	# RAT
	#print listLanguages()
	
	# --------------------------------------

	# RAT
	#print getUserPreference()

	# --------------------------------------

	language_list = ["en","ja","fr","de","it","es"]

	"""
	for language_code in language_list:
		print updateUserPreference(language_code)
	"""

	# language_code = ""
	# result: fail,HTTP Error 400: Bad Request
	"""
	language_code = ""
	print updateUserPreference(language_code)
	"""
	
	# invalid language code
	# result: fail,HTTP Error 400: Bad Request
	"""
	language_code = "zz"
	print updateUserPreference(language_code)
	"""

	# special chars
	# result: fail,HTTP Error 500: Whitespace must appear between attributes.
	"""
	language_code = mapi_util.SPECIAL_CHARS
	print updateUserPreference(language_code)
	"""
	
	# case sensitive
	# result: pass, update successfully but the result is still lower case, bug?
	"""
	language_code = "EN"
	print updateUserPreference(language_code)
	"""


	# --------------------------------------

	"""
	The passphrase should be 8 to 32 characters, containing at least one of the following:
	upper case, lower case, numeral, and special character (~!@#$%^&*()_+)
	"""

	# RAT
	account_name = "shaodanny@gmail.com"
	new_passphrase = "P@ssw0rd@123"
	#print updatePassphrase(account_name, new_passphrase)


	# empty account ID
	# result: fail, HTTP Error 400: Bad Request
	account_id = ""
	new_passphrase = "P@ssw0rd@123"
	#print updatePassphrase(account_id, new_passphrase, True)

	# non-existing account ID
	# result: fail, HTTP Error 400: Bad Request
	account_id = "00000000-0000-0000-0000-000000000000"
	new_passphrase = "P@ssw0rd@123"
	#print updatePassphrase(account_id, new_passphrase, True)


	# account ID = random 36 chars
	# result: fail, HTTP Error 400: Bad Request
	account_id = mapi_util.random_str(36)
	new_passphrase = "P@ssw0rd@123"
	#print updatePassphrase(account_id, new_passphrase, True)


	# account ID = special chars
	# result: fail, HTTP Error 500: Whitespace must appear between attributes.
	account_id = mapi_util.SPECIAL_CHARS
	new_passphrase = "P@ssw0rd@123"
	#print updatePassphrase(account_id, new_passphrase, True)

	# account ID = max + 1
	# result: fail, HTTP Error 400: Bad Request
	account_id = mapi_util.random_str(1025)
	new_passphrase = "P@ssw0rd@123"
	#print updatePassphrase(account_id, new_passphrase, True)


	# update other account's passphrase
	# result: fail,HTTP Error 400: Bad Request
	account_name = "2F73B65D-99D2-47BE-A975-094D298D5A52" # danny3_shao@trend.com.tw
	new_passphrase = "P@ssw0rd@123"
	#print updatePassphrase(account_name, new_passphrase, True)


	# passphrase = ""
	# result:fail, HTTP Error 500: Internal Server Error
	account_name = "shaodanny@gmail.com"
	new_passphrase = ""
	#print updatePassphrase(account_name, new_passphrase)

	# passphrase = "aA1@"
	# result:pass, bug, should be at least 8 chars
	account_name = "shaodanny@gmail.com"
	new_passphrase = "aA1@"
	#print updatePassphrase(account_name, new_passphrase)

	# passphrase = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaA1@"
	# result:pass, bug, should not exceed 32 chars
	account_name = "shaodanny@gmail.com"
	new_passphrase = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaA1@"
	#print updatePassphrase(account_name, new_passphrase)

	# passphrase = "1A@@@@@@"
	# result:pass, bug, should contain lower case
	account_name = "shaodanny@gmail.com"
	new_passphrase = "1A@@@@@@"
	#print updatePassphrase(account_name, new_passphrase)

	# passphrase = "1a@@@@@@"
	# result:pass, bug, shoudd contain upper case
	account_name = "shaodanny@gmail.com"
	new_passphrase = "1a@@@@@@"
	#print updatePassphrase(account_name, new_passphrase)

	# passphrase = "aA@@@@@@"
	# result:pass, bug, should contain number
	account_name = "shaodanny@gmail.com"
	new_passphrase = "aA@@@@@@"
	#print updatePassphrase(account_name, new_passphrase)

	# passphrase = "123456aA"
	# result:pass, bug, should contain special char
	account_name = "shaodanny@gmail.com"
	new_passphrase = "123456aA"
	#print updatePassphrase(account_name, new_passphrase)

	# passphrase = special chars
	# result:fail,HTTP Error 500: Whitespace must appear between attributes.
	account_name = "shaodanny@gmail.com"
	new_passphrase = mapi_util.SPECIAL_CHARS + "aA1"
	#print updatePassphrase(account_name, new_passphrase)


	# --------------------------------------

	# RAT
	"""
	login_name = "auto_user@trend.com.tw"
	login_pass = "P@ssw0rd"
	user_type = "localuser"
	first_name = "auto"
	last_name = "user"
	email = "auto_user@trend.com.tw"
	user_role = "Administrator"
	mfa_status = None
	"""


	# empty login name
	# result: fail, HTTP Error 400: Bad Request
	"""
	login_name = ""
	login_pass = "P@ssw0rd"
	user_type = "localuser"
	first_name = "auto"
	last_name = "user"
	email = "auto_user@trend.com.tw"
	user_role = "Administrator"
	mfa_status = None
	"""

	# login name UI max 360
	# result: pass
	"""
	login_name = mapi_util.random_str(360)
	login_pass = "P@ssw0rd"
	user_type = "localuser"
	first_name = "auto"
	last_name = "user"
	email = "auto_user@trend.com.tw"
	user_role = "Administrator"
	mfa_status = None
	"""
	
	# login name UI max 360 + 1
	# result: pass, bug should be no more than 360 chars
	"""
	login_name = mapi_util.random_str(361)
	login_pass = "P@ssw0rd"
	user_type = "localuser"
	first_name = "auto"
	last_name = "user"
	email = "auto_user@trend.com.tw"
	user_role = "Administrator"
	mfa_status = None
	"""

	# login name special chars
	# result: fail,HTTP Error 500: Whitespace must appear between attributes.
	"""
	login_name = mapi_util.SPECIAL_CHARS
	login_pass = "P@ssw0rd"
	user_type = "localuser"
	first_name = "auto"
	last_name = "user"
	email = "auto_user@trend.com.tw"
	user_role = "Administrator"
	mfa_status = None
	"""
	
	# empty pass
	# result: pass, empty pass just like UI
	"""
	login_name = "auto_user@trend.com.tw"
	login_pass = ""
	user_type = "localuser"
	first_name = "auto"
	last_name = "user"
	email = "auto_user@trend.com.tw"
	user_role = "Administrator"
	mfa_status = None
	"""

	# passphrase = "aA1@", should be at least 8 chars
	# result:fail,HTTP Error 400: Bad Request
	"""
	login_name = "auto_user@trend.com.tw"
	login_pass = "aA1@"
	user_type = "localuser"
	first_name = "auto"
	last_name = "user"
	email = "auto_user@trend.com.tw"
	user_role = "Administrator"
	mfa_status = None
	"""

	# passphrase = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaA1@", should not exceed 32 chars
	# result:fail,HTTP Error 400: Bad Request
	"""	
	login_name = "auto_user@trend.com.tw"
	login_pass = "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaA1@"
	user_type = "localuser"
	first_name = "auto"
	last_name = "user"
	email = "auto_user@trend.com.tw"
	user_role = "Administrator"
	mfa_status = None
	"""

	# passphrase = "1A@@@@@@", should contain lower case
	# result:fail,HTTP Error 400: Bad Request
	"""
	login_name = "auto_user@trend.com.tw"
	login_pass = "1A@@@@@@"
	user_type = "localuser"
	first_name = "auto"
	last_name = "user"
	email = "auto_user@trend.com.tw"
	user_role = "Administrator"
	mfa_status = None
	"""

	# passphrase = "1a@@@@@@", should contain upper case
	# result:fail,HTTP Error 400: Bad Request
	"""
	login_name = "auto_user@trend.com.tw"
	login_pass =  "1a@@@@@@"
	user_type = "localuser"
	first_name = "auto"
	last_name = "user"
	email = "auto_user@trend.com.tw"
	user_role = "Administrator"
	mfa_status = None
	"""


	# passphrase = "aA@@@@@@", should contain number
	# result:fail,HTTP Error 400: Bad Request
	"""
	login_name = "auto_user@trend.com.tw"
	login_pass =  "aA@@@@@@"
	user_type = "localuser"
	first_name = "auto"
	last_name = "user"
	email = "auto_user@trend.com.tw"
	user_role = "Administrator"
	mfa_status = None
	"""

	# passphrase = "123456aA", should contain special char
	# result:fail,HTTP Error 400: Bad Request
	"""
	login_name = "auto_user@trend.com.tw"
	login_pass =  "123456aA"
	user_type = "localuser"
	first_name = "auto"
	last_name = "user"
	email = "auto_user@trend.com.tw"
	user_role = "Administrator"
	mfa_status = None
	"""
	
	# passphrase = "123456aA", should contain special char
	# result:pass, bug
	"""
	login_name = "auto_user@trend.com.tw"
	login_pass =  "123456aA"
	user_type = "localuser"
	first_name = "auto"
	last_name = "user"
	email = "auto_user@trend.com.tw"
	user_role = "Administrator"
	mfa_status = None
	"""
	
	# passphrase = special chars
	# result:fail,HTTP Error 500: Whitespace must appear between attributes.
	"""
	login_name = "auto_user@trend.com.tw"
	login_pass =  mapi_util.SPECIAL_CHARS
	user_type = "localuser"
	first_name = "auto"
	last_name = "user"
	email = "auto_user@trend.com.tw"
	user_role = "Administrator"
	mfa_status = None
	"""

	# no user type
	# result: fail,HTTP Error 400: Bad Request
	"""
	login_name = "auto_user@trend.com.tw"
	login_pass = "P@ssw0rd"
	user_type = None
	first_name = "auto"
	last_name = "user"
	email = "auto_user@trend.com.tw"
	user_role = "Administrator"
	mfa_status = None
	"""

	# empty user type
	# result: fail,HTTP Error 400: Bad Request
	"""
	login_name = "auto_user@trend.com.tw"
	login_pass = "P@ssw0rd"
	user_type = ""
	first_name = "auto"
	last_name = "user"
	email = "auto_user@trend.com.tw"
	user_role = "Administrator"
	mfa_status = None
	"""

	# wrong user type
	# result: pass, bug should block?
	"""
	login_name = "auto_user@trend.com.tw"
	login_pass = "P@ssw0rd"
	user_type = mapi_util.random_str(20)
	first_name = "auto"
	last_name = "user"
	email = "auto_user@trend.com.tw"
	user_role = "Administrator"
	mfa_status = None
	"""

	# user type special chars
	# result: fail,HTTP Error 500: Whitespace must appear between attributes.
	"""
	login_name = "auto_user@trend.com.tw"
	login_pass = "P@ssw0rd"
	user_type = mapi_util.SPECIAL_CHARS
	first_name = "auto"
	last_name = "user"
	email = "auto_user@trend.com.tw"
	user_role = "Administrator"
	mfa_status = None
	"""

	# user type case sensitive
	# result: pass, not case senstive bug?
	"""
	login_name = "auto_user@trend.com.tw"
	login_pass = "P@ssw0rd"
	user_type = "LOCALUSER"
	first_name = "auto"
	last_name = "user"
	email = "auto_user@trend.com.tw"
	user_role = "Administrator"
	mfa_status = None
	"""

	# user type ssouser
	# result: pass
	"""
	login_name = "auto_user@trend.com.tw"
	#login_pass = "P@ssw0rd"
	user_type = "ssouser"
	#first_name = "auto"
	#last_name = "user"
	#email = "auto_user@trend.com.tw"
	user_role = "Administrator"
	mfa_status = None
	"""

	# user type aduser
	# result: pass, like localuser
	"""
	login_name = "auto_user@trend.com.tw"
	login_pass = "P@ssw0rd"
	user_type = "aduser"
	first_name = "auto"
	last_name = "user"
	email = "auto_user@trend.com.tw"
	user_role = "Administrator"
	mfa_status = None
	"""


	# no first name
	# result: fail,HTTP Error 400: Bad Request
	"""
	login_name = "auto_user@trend.com.tw"
	login_pass = "P@ssw0rd"
	user_type = "localuser"
	first_name = None
	last_name = "user"
	email = "auto_user@trend.com.tw"
	user_role = "Administrator"
	mfa_status = None
	"""

	# empty first name
	# result: fail,HTTP Error 400: Bad Request
	"""
	login_name = "auto_user@trend.com.tw"
	login_pass = "P@ssw0rd"
	user_type = "localuser"
	first_name = ""
	last_name = "user"
	email = "auto_user@trend.com.tw"
	user_role = "Administrator"
	mfa_status = None
	"""

	# first_name UI max 360
	# result:pass
	"""
	login_name = "auto_user@trend.com.tw"
	login_pass = "P@ssw0rd"
	user_type = "localuser"
	first_name = mapi_util.random_str(360)
	last_name = "user"
	email = "auto_user@trend.com.tw"
	user_role = "Administrator"
	mfa_status = None
	"""

	# first_name UI max 360+1
	# result:pass, bug max is 360
	"""
	login_name = "auto_user@trend.com.tw"
	login_pass = "P@ssw0rd"
	user_type = "localuser"
	first_name = mapi_util.random_str(361)
	last_name = "user"
	email = "auto_user@trend.com.tw"
	user_role = "Administrator"
	mfa_status = None
	"""

	# first_name special chars
	# result:pass, UI allow as well
	"""
	login_name = "auto_user@trend.com.tw"
	login_pass = "P@ssw0rd"
	user_type = "localuser"
	first_name = mapi_util.SPECIAL_CHARS
	last_name = "user"
	email = "auto_user@trend.com.tw"
	user_role = "Administrator"
	mfa_status = None
	"""

	# no last_name
	# result: fail,HTTP Error 400: Bad Request
	"""
	login_name = "auto_user@trend.com.tw"
	login_pass = "P@ssw0rd"
	user_type = "localuser"
	first_name = "auto"
	last_name = None
	email = "auto_user@trend.com.tw"
	user_role = "Administrator"
	mfa_status = None
	"""

	# last_name = UI max 360
	# result: pass
	"""
	login_name = "auto_user@trend.com.tw"
	login_pass = "P@ssw0rd"
	user_type = "localuser"
	first_name = "auto"
	last_name = mapi_util.random_str(360)
	email = "auto_user@trend.com.tw"
	user_role = "Administrator"
	mfa_status = None
	"""

	# last_name = UI max 360+1 
	# result: pass, bug
	"""
	login_name = "auto_user@trend.com.tw"
	login_pass = "P@ssw0rd"
	user_type = "localuser"
	first_name = "auto"
	last_name = mapi_util.random_str(361)
	email = "auto_user@trend.com.tw"
	user_role = "Administrator"
	mfa_status = None
	"""

	# last_name = special chars
	# result: pass
	"""
	login_name = "auto_user@trend.com.tw"
	login_pass = "P@ssw0rd"
	user_type = "localuser"
	first_name = "auto"
	last_name = mapi_util.SPECIAL_CHARS
	email = "auto_user@trend.com.tw"
	user_role = "Administrator"
	mfa_status = None
	"""

	# no email
	# result: fail,HTTP Error 400: Bad Request
	"""
	login_name = "auto_user@trend.com.tw"
	login_pass = "P@ssw0rd"
	user_type = "localuser"
	first_name = "auto"
	last_name = "user"
	email = None
	user_role = "Administrator"
	mfa_status = None
	"""

	# empty email
	# result: fail,HTTP Error 400: Bad Request
	"""
	login_name = "auto_user@trend.com.tw"
	login_pass = "P@ssw0rd"
	user_type = "localuser"
	first_name = "auto"
	last_name = "user"
	email = ""
	user_role = "Administrator"
	mfa_status = None
	"""


	# email = UI max 360
	# result: pass, bug db max is 320, extra chars are truncated
	"""
	login_name = "auto_user@trend.com.tw"
	login_pass = "P@ssw0rd"
	user_type = "localuser"
	first_name = "auto"
	last_name = "user"
	email = mapi_util.random_str(351) + "@test.com"
	user_role = "Administrator"
	mfa_status = None
	"""
	
	# email = specail chars
	# result: fail,HTTP Error 400: Bad Request
	"""
	login_name = "auto_user@trend.com.tw"
	login_pass = "P@ssw0rd"
	user_type = "localuser"
	first_name = "auto"
	last_name = "user"
	email = mapi_util.SPECIAL_CHARS
	user_role = "Administrator"
	mfa_status = None
	"""

	# user_role = "Administrator"
	# result: pass
	"""
	login_name = "auto_user@trend.com.tw"
	login_pass = "P@ssw0rd"
	user_type = "localuser"
	first_name = "auto"
	last_name = "user"
	email = "auto_user@trend.com.tw"
	user_role = "Administrator"
	mfa_status = None
	"""

	# user_role = "Auditor"
	# result: pass
	"""
	login_name = "auto_user@trend.com.tw"
	login_pass = "P@ssw0rd"
	user_type = "localuser"
	first_name = "auto"
	last_name = "user"
	email = "auto_user@trend.com.tw"
	user_role = "Auditor"
	mfa_status = None
	"""

	# user_role = "Key Approver"
	# result: pass
	"""
	login_name = "auto_user@trend.com.tw"
	login_pass = "P@ssw0rd"
	user_type = "localuser"
	first_name = "auto"
	last_name = "user"
	email = "auto_user@trend.com.tw"
	user_role = "Key Approver"
	mfa_status = None
	"""
	
	# user_role = "Data Analyst"
	# result: pass
	"""
	login_name = "auto_user@trend.com.tw"
	login_pass = "P@ssw0rd"
	user_type = "localuser"
	first_name = "auto"
	last_name = "user"
	email = "auto_user@trend.com.tw"
	user_role = "Data Analyst"
	mfa_status = None
	"""

	# user_role = "Security Administrator"
	# result: pass
	"""
	login_name = "auto_user@trend.com.tw"
	login_pass = "P@ssw0rd"
	user_type = "localuser"
	first_name = "auto"
	last_name = "user"
	email = "auto_user@trend.com.tw"
	user_role = "Security Administrator"
	mfa_status = None
	"""

	# user_role = random 10 chars
	# result: fail, HTTP Error 500: Internal Server Error
	"""
	login_name = "auto_user@trend.com.tw"
	login_pass = "P@ssw0rd"
	user_type = "localuser"
	first_name = "auto"
	last_name = "user"
	email = "auto_user@trend.com.tw"
	user_role = mapi_util.random_str(10)
	mfa_status = None
	"""

	# user_role = db max 50 chars
	# result: fail, HTTP Error 500: Internal Server Error
	"""
	login_name = "auto_user@trend.com.tw"
	login_pass = "P@ssw0rd"
	user_type = "localuser"
	first_name = "auto"
	last_name = "user"
	email = "auto_user@trend.com.tw"
	user_role = mapi_util.random_str(50)
	mfa_status = None
	"""

	# user_role = ADMINISTRATOR, case sensitive
	# result: pass, is not case insensitive, bug?
	"""
	login_name = "auto_user@trend.com.tw"
	login_pass = "P@ssw0rd"
	user_type = "localuser"
	first_name = "auto"
	last_name = "user"
	email = "auto_user@trend.com.tw"
	user_role = "ADMINISTRATOR"
	mfa_status = None
	"""

	# user_role = special chars
	# result: fail,HTTP Error 500: There is an error in XML document (4, 288).
	"""
	login_name = "auto_user@trend.com.tw"
	login_pass = "P@ssw0rd"
	user_type = "localuser"
	first_name = "auto"
	last_name = "user"
	email = "auto_user@trend.com.tw"
	user_role = mapi_util.SPECIAL_CHARS
	mfa_status = None
	"""


	#print createUser(login_name, login_pass, user_type, first_name, last_name, email, user_role, mfa_status)


	# --------------------------------------
	# --------------------------------------
	# --------------------------------------
	# --------------------------------------
	# --------------------------------------


	#RAT
	"""
	first_name = "auto_update"
	last_name = "user_update"
	user_role = "Administrator"
	"""

	# no first name
	# result: pass, keep original no change
	"""
	first_name = None
	last_name = "user"
	user_role = "Administrator"
	"""

	# empty first name
	# result: pass, keep original no change
	"""
	first_name = ""
	last_name = "user"
	user_role = "Administrator"
	"""

	# first_name UI max 360
	# result:pass
	"""
	first_name = mapi_util.random_str(360)
	last_name = "user"
	user_role = "Administrator"
	"""

	# first_name UI max 360+1
	# result:pass, bug max is 360
	"""
	first_name = mapi_util.random_str(361)
	last_name = "user"
	user_role = "Administrator"
	"""

	# To-Do : fail in the validation cuz & -> amp; in the application
	# first_name special chars
	# result:pass, UI allow as well
	"""
	first_name = mapi_util.SPECIAL_CHARS
	last_name = "user"
	user_role = "Administrator"
	"""

	# no last_name
	# result: pass, keep original no change
	"""
	first_name = "auto"
	last_name = None
	user_role = "Administrator"
	"""

	# empty last_name
	# result: pass, keep original no change
	"""
	first_name = "auto"
	last_name = ""
	user_role = "Administrator"
	"""


	# last_name = UI max 360
	# result: pass
	"""
	first_name = "auto"
	last_name = mapi_util.random_str(360)
	user_role = "Administrator"
	"""

	# last_name = UI max 360+1 
	# result: pass, bug
	"""
	first_name = "auto"
	last_name = mapi_util.random_str(361)
	user_role = "Administrator"
	"""

	# To-Do : fail in the validation cuz & -> amp; in the application
	# last_name = special chars
	# result: pass
	"""
	first_name = "auto"
	last_name = mapi_util.SPECIAL_CHARS
	user_role = "Administrator"
	"""

	# user_role = "Administrator"
	# result: pass
	"""
	first_name = "auto"
	last_name = "user"
	user_role = "Administrator"
	"""

	# user_role = "Auditor"
	# result: pass
	"""
	first_name = "auto"
	last_name = "user"
	user_role = "Auditor"
	"""

	# user_role = "Key Approver"
	# result: pass
	"""
	first_name = "auto"
	last_name = "user"
	user_role = "Key Approver"
	"""
	
	# user_role = "Data Analyst"
	# result: pass
	"""
	first_name = "auto"
	last_name = "user"
	user_role = "Data Analyst"
	"""

	# user_role = "Security Administrator"
	# result: pass
	"""
	first_name = "auto"
	last_name = "user"
	user_role = "Security Administrator"
	"""

	# user_role = random 10 chars
	# result: fail, HTTP Error 500: Internal Server Error
	"""
	first_name = "auto"
	last_name = "user"
	user_role = mapi_util.random_str(10)
	"""

	# user_role = db max 50 chars
	# result: fail, HTTP Error 500: Internal Server Error
	"""
	first_name = "auto"
	last_name = "user"
	user_role = mapi_util.random_str(50)
	"""

	# user_role = ADMINISTRATOR, case sensitive
	# result: pass, is not case insensitive, bug?
	"""
	first_name = "auto"
	last_name = "user"
	user_role = "ADMINISTRATOR"
	"""

	# user_role = special chars
	# result: fail,HTTP Error 500: There is an error in XML document (4, 288).
	"""
	first_name = "auto"
	last_name = "user"
	user_role = mapi_util.SPECIAL_CHARS
	"""

	#print updateUser(first_name, last_name, user_role)


	#RAT
	"""
	account_name = "shaodanny@gmail.com"
	new_timezone = "Taipei Standard Time"
	new_dateFormat = "yyyy/MM/dd"
	new_session_timeout = "960"
	"""

	# new_dateFormat = "DD/MM/YYYY"
	# result: pass
	"""
	account_name = "shaodanny@gmail.com"
	new_timezone = "Taipei Standard Time"
	new_dateFormat = "DD/MM/YYYY"
	new_session_timeout = "960"
	"""
	
	# new_dateFormat = "YYYY/MM/DD"
	# result: pass
	"""
	account_name = "shaodanny@gmail.com"
	new_timezone = "Taipei Standard Time"
	new_dateFormat = "YYYY/MM/DD"
	new_session_timeout = "960"
	"""
	
	# new_dateFormat = "YYYY/MM/DD"
	# result: pass
	"""
	account_name = "shaodanny@gmail.com"
	new_timezone = "Taipei Standard Time"
	new_dateFormat = "MM/DD/YYYY"
	new_session_timeout = "960"
	"""

	# new_dateFormat = empty
	# result: pass, no change
	"""
	account_name = "shaodanny@gmail.com"
	new_timezone = "Taipei Standard Time"
	new_dateFormat = None
	new_session_timeout = "960"
	"""

	# new_dateFormat = ""
	# result: pass, no change
	"""
	account_name = "shaodanny@gmail.com"
	new_timezone = "Taipei Standard Time"
	new_dateFormat = ""
	new_session_timeout = "960"
	"""

	# new_dateFormat = random char
	# result: pass, bug, should only specific format
	""" check
	account_name = "m318021@gmail.com"
	new_timezone = "Taipei Standard Time"
	new_dateFormat = mapi_util.random_str(10)
	new_session_timeout = "960"
	"""

	# new_dateFormat = mm/dd/yyyy
	# result: pass, date format is not case sensitive
	"""check
	account_name = "m318021@gmail.com"
	new_timezone = "Taipei Standard Time"
	new_dateFormat = "mm/dd/yyyy"
	new_session_timeout = "960"
	"""
	
	# new_dateFormat = special char
	# result: fail,HTTP Error 500: Whitespace must appear between attributes.
	"""check
	account_name = "m318021@gmail.com"
	new_timezone = "Taipei Standard Time"
	new_dateFormat = mapi_util.SPECIAL_CHARS
	new_session_timeout = "960"
	"""

	# new_session_timeout = empty
	# result: pass, no change
	"""check
	account_name = "m318021@gmail.com"
	new_timezone = "Taipei Standard Time"
	new_dateFormat = "mm/dd/yyyy"
	new_session_timeout = None
	"""

	# new_session_timeout = ""
	# result: fail,HTTP Error 500: There is an error in XML document (1, 134).
	"""check
	account_name = "m318021@gmail.com"
	new_timezone = "Taipei Standard Time"
	new_dateFormat = "mm/dd/yyyy"
	new_session_timeout = ""
	"""


	#print updateAccountSettings(account_name, new_timezone, new_dateFormat, new_session_timeout)
	

	#RAT
	user_login_name = "m318021@gmail.com"
	last_pass = "P@ssw0rd@123"
	new_pass = "P@ssw0rd"
	print updateUserlogin(user_login_name, last_pass, new_pass)


	#RAT
	account_name="shaodanny@gmail.com"
	user_login_name = "shaodanny@gmail.com"
	account2_name="shaodanny+2@gmail.com"
	#print updateCurrentUsersAccount(account_name, account2_name)

