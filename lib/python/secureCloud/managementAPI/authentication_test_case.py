import time
import mapi_lib
import logging
import mapi_util
import mapi_config
import simulator_lib




def digest_authentication_test(realm, digest_broker_name, digest_broker_pass, header_broker_name):
	broker_api_lib = mapi_lib.mapi_lib(no_init=True)

	return broker_api_lib.digest_authentication_test(realm, digest_broker_name, digest_broker_pass, header_broker_name)

def get_certificate():
	broker_api_lib = mapi_lib.mapi_lib()

	return broker_api_lib.get_certificate()

def basic_auth(auth_type, api_account_id, user_name, user_pass, encrypt_pass=True):
	broker_api_lib = mapi_lib.mapi_lib(auth_type=auth_type, api_account_id=api_account_id, user_name=user_name, user_pass=user_pass)

	return broker_api_lib.basic_auth(encrypt_pass)

def userAuthenticationRequest(auth_type, access_key_id):
	broker_api_lib = mapi_lib.mapi_lib(auth_type=auth_type, access_key_id=access_key_id)

	return broker_api_lib.userAuthenticationRequest()


def userAuthenticationResponse(auth_type, access_key_id, secret_access_key, api_account_id, ext_auth_id, ext_random_data, auth_id_sensitive=False, random_data_sensitive=False, use_external_data=False):
	broker_api_lib = mapi_lib.mapi_lib(auth_type=auth_type, access_key_id=access_key_id, secret_access_key=secret_access_key, api_account_id=api_account_id)

	return broker_api_lib.userAuthenticationResponse(ext_auth_id, ext_random_data, auth_id_sensitive, random_data_sensitive, use_external_data)

if __name__ == '__main__':

	# RAT case
	"""
	realm = "securecloud@trend.com"
	digest_broker_name = "danny"
	digest_broker_pass = "ClOuD9"
	header_broker_name = "danny"
	"""

	# no realm
	# result:fail, HTTP Error 401: Unauthorized
	"""
	realm = ""
	digest_broker_name = "danny"
	digest_broker_pass = "ClOuD9"
	header_broker_name = "danny"
	"""

	# wrong realm
	# result:fail, HTTP Error 401: Unauthorized
	"""
	realm = mapi_util.random_str(20)
	digest_broker_name = "danny"
	digest_broker_pass = "ClOuD9"
	header_broker_name = "danny"
	"""

	# realm case sensitive
	# result:fail, HTTP Error 401: Unauthorized
	"""
	realm = "SECURECLOUD@TREND.COM"
	digest_broker_name = "danny"
	digest_broker_pass = "ClOuD9"
	header_broker_name = "danny"
	"""
	
	# realm special char
	# result:fail, HTTP Error 401: Unauthorized
	"""
	realm = mapi_util.SPECIAL_CHARS
	digest_broker_name = "danny"
	digest_broker_pass = "ClOuD9"
	header_broker_name = "danny"
	"""

	# no digest broker name
	# result:fail, HTTP Error 401: digest auth failed
	"""
	realm = "securecloud@trend.com"
	digest_broker_name = ""
	digest_broker_pass = "ClOuD9"
	header_broker_name = "danny"
	"""

	# wrong digest broker name
	# result:fail, HTTP Error 401: digest auth failed
	"""
	realm = "securecloud@trend.com"
	digest_broker_name = mapi_util.random_str(20)
	digest_broker_pass = "ClOuD9"
	header_broker_name = "danny"
	"""

	# digest broker name case sensitive
	# result:fail, HTTP Error 401: digest auth failed
	"""
	realm = "securecloud@trend.com"
	digest_broker_name = "DANNY"
	digest_broker_pass = "ClOuD9"
	header_broker_name = "danny"
	"""

	# digest broker name special char
	# result:fail, HTTP Error 500: Index was outside the bounds of the array.
	"""
	realm = "securecloud@trend.com"
	digest_broker_name = mapi_util.SPECIAL_CHARS
	digest_broker_pass = "ClOuD9"
	header_broker_name = "danny"
	"""

	# no digest broker pass
	# result:fail, HTTP Error 401: digest auth failed
	"""
	realm = "securecloud@trend.com"
	digest_broker_name = "danny"
	digest_broker_pass = ""
	header_broker_name = "danny"
	"""

	# wrong digest broker pass
	# result:fail, HTTP Error 401: digest auth failed
	"""
	realm = "securecloud@trend.com"
	digest_broker_name = "danny"
	digest_broker_pass = mapi_util.random_str(20)
	header_broker_name = "danny"
	"""

	# digest broker pass case sensitive
	# result:fail, HTTP Error 401: digest auth failed
	"""
	realm = "securecloud@trend.com"
	digest_broker_name = "danny"
	digest_broker_pass = "cloud9"
	header_broker_name = "danny"
	"""

	# digest broker pass special chars
	# result:fail, HTTP Error 401: digest auth failed
	"""
	realm = "securecloud@trend.com"
	digest_broker_name = "danny"
	digest_broker_pass = mapi_util.SPECIAL_CHARS
	header_broker_name = "danny"
	"""

	# no header broker name
	# result:fail, HTTP Error 401: Unauthorized
	"""
	realm = "securecloud@trend.com"
	digest_broker_name = "danny"
	digest_broker_pass = mapi_util.SPECIAL_CHARS
	header_broker_name = ""
	"""

	# wrong header broker name
	# result:fail, HTTP Error 401: Unauthorized
	"""
	realm = "securecloud@trend.com"
	digest_broker_name = "danny"
	digest_broker_pass = mapi_util.SPECIAL_CHARS
	header_broker_name = mapi_util.random_str(20)
	"""


	# header broker name case sensitive
	# result:fail, HTTP Error 401: Unauthorized
	"""
	realm = "securecloud@trend.com"
	digest_broker_name = "danny"
	digest_broker_pass = mapi_util.SPECIAL_CHARS
	header_broker_name = "DANNY"
	"""

	# header broker name special chars
	# result:fail, HTTP Error 401: Unauthorized
	"""
	realm = "securecloud@trend.com"
	digest_broker_name = "danny"
	digest_broker_pass = "ClOuD9"
	header_broker_name = mapi_util.SPECIAL_CHARS
	"""
	
	#print digest_authentication_test(realm, digest_broker_name, digest_broker_pass, header_broker_name)

	# -------------------------------------------

	#print get_certificate()

	# -------------------------------------------

	#RAT
	
	api_account_id = "250C5CF1-62B6-4CDD-91C6-58F0307FE75E"
	#api_account_id = "EB43453B-4484-4DE4-AFDD-4B9C76E7D14C"
	user_name = "shaodanny@gmail.com"
	#user_name = "m318021@gmail.com"
	#user_pass = "P@ssw0rd"
	user_pass = "P@ssw0rd@123"
	

	# empty account id
	# result: pass
	"""
	api_account_id = ""
	user_name = "shaodanny@gmail.com"
	user_pass = "P@ssw0rd@123"
	"""
	
	# non-existing account id
	# result: fail,HTTP Error 403: Forbidden
	"""
	api_account_id = "00000000-0000-0000-0000-000000000000"
	user_name = "shaodanny@gmail.com"
	user_pass = "P@ssw0rd@123"
	"""

	# invalid account id
	# result: fail,HTTP Error 403: Forbidden
	"""
	api_account_id = "asdfasdfsdtfgdfg87d89fyaeao8sdfg79ay"
	user_name = "shaodanny@gmail.com"
	user_pass = "P@ssw0rd@123"
	"""

	# account id case sensitive
	# result: pass, bug should be case sensitive?
	"""
	api_account_id = "250c5cf1-62b6-4cdd-91c6-58f0307fe75e".upper()
	user_name = "shaodanny@gmail.com"
	user_pass = "P@ssw0rd@123"
	"""

	# account id special chars
	# result: fail,HTTP Error 500: Whitespace must appear between attributes. Line 1, position 377.
	"""
	api_account_id = mapi_util.SPECIAL_CHARS
	user_name = "shaodanny@gmail.com"
	user_pass = "P@ssw0rd@123"
	"""

	# empty user name
	# result: fail,HTTP Error 404: Not Found
	"""
	api_account_id = "250C5CF1-62B6-4CDD-91C6-58F0307FE75E"
	user_name = ""
	user_pass = "P@ssw0rd@123"
	"""

	# non-existing user name
	# result: fail,HTTP Error 403: Forbidden
	"""
	api_account_id = "250C5CF1-62B6-4CDD-91C6-58F0307FE75E"
	user_name = mapi_util.random_str(20)
	user_pass = "P@ssw0rd@123"
	"""

	# user name case sensitive
	# result: pass, bug should be sensitive
	"""
	api_account_id = "250C5CF1-62B6-4CDD-91C6-58F0307FE75E"
	user_name = "SHAODANNY@GMAIL.COM"
	user_pass = "P@ssw0rd@123"
	"""

	# user name special chars
	# result: fail,HTTP Error 403: Forbidden
	"""
	api_account_id = "250C5CF1-62B6-4CDD-91C6-58F0307FE75E"
	user_name = mapi_util.SPECIAL_CHARS
	user_pass = "P@ssw0rd@123"
	"""

	# wrong pass
	# result: fail,HTTP Error 403: Forbidden
	"""
	api_account_id = "250C5CF1-62B6-4CDD-91C6-58F0307FE75E"
	user_name = "shaodanny@gmail.com"
	user_pass = mapi_util.random_str(20)
	"""

	# pass case sensitive
	# result: fail,HTTP Error 403: Forbidden
	"""
	api_account_id = "250C5CF1-62B6-4CDD-91C6-58F0307FE75E"
	user_name = "shaodanny@gmail.com"
	user_pass = "P@SSW0RD@123"
	"""
	
	#print basic_auth("basic_auth", api_account_id, user_name, user_pass)

	# empty pass
	# result: fail,HTTP Error 403: Forbidden
	"""
	api_account_id = "250C5CF1-62B6-4CDD-91C6-58F0307FE75E"
	user_name = "shaodanny@gmail.com"
	user_pass = ""
	"""

	#print basic_auth("basic_auth", api_account_id, user_name, user_pass, encrypt_pass=False)


	# -------------------------------------------

	#RAT
	# access_key_id = "grVAP1k5xBE3xUhVt7tO"

	# empty access key ID
	# result: fail,HTTP Error 404: Not Found
	"""
	access_key_id = ""
	"""

	# wrong access key ID
	# result: fail,HTTP Error 400: Bad Request
	"""
	access_key_id = mapi_util.random_str(20)
	"""

	# access key ID case sensitive
	# result: pass,bug should be case sensitive
	"""
	access_key_id = "grVAP1k5xBE3xUhVt7tO"
	access_key_id = access_key_id.upper()
	"""

	#print userAuthenticationRequest("api_auth", access_key_id)


	# -------------------------------------------

	# RAT
	"""
	access_key_id = "grVAP1k5xBE3xUhVt7tO"
	secret_access_key = "c1yiaB6l2MqkNChb3oDv7xtN7qeCl8B6LVdi3hDT"
	api_account_id = "250C5CF1-62B6-4CDD-91C6-58F0307FE75E"
	ext_auth_id = None
	ext_random_data = None
	"""

	# empty access key ID
	# result: fail,HTTP Error 404: Not Found
	"""
	access_key_id = ""
	secret_access_key = "c1yiaB6l2MqkNChb3oDv7xtN7qeCl8B6LVdi3hDT"
	api_account_id = "250C5CF1-62B6-4CDD-91C6-58F0307FE75E"
	ext_auth_id = None
	ext_random_data = None
	"""

	# wrong access key ID
	# result: fail,HTTP Error 400: Bad Request
	"""
	access_key_id = mapi_util.random_str(20)
	secret_access_key = "c1yiaB6l2MqkNChb3oDv7xtN7qeCl8B6LVdi3hDT"
	api_account_id = "250C5CF1-62B6-4CDD-91C6-58F0307FE75E"
	ext_auth_id = None
	ext_random_data = None
	"""

	# access key ID case sensitive
	# result: pass,bug should be case sensitive
	"""
	access_key_id = "grVAP1k5xBE3xUhVt7tO".upper()
	secret_access_key = "c1yiaB6l2MqkNChb3oDv7xtN7qeCl8B6LVdi3hDT"
	api_account_id = "250C5CF1-62B6-4CDD-91C6-58F0307FE75E"
	ext_auth_id = None
	ext_random_data = None
	"""

	# empty secret access key
	# result: fail,HTTP Error 403: Forbidden
	"""
	access_key_id = "grVAP1k5xBE3xUhVt7tO"
	secret_access_key = ""
	api_account_id = "250C5CF1-62B6-4CDD-91C6-58F0307FE75E"
	ext_auth_id = None
	ext_random_data = None
	"""

	# wrong secret access key
	# result: fail,HTTP Error 403: Forbidden
	"""
	access_key_id = "grVAP1k5xBE3xUhVt7tO"
	secret_access_key = mapi_util.random_str(20)
	api_account_id = "250C5CF1-62B6-4CDD-91C6-58F0307FE75E"
	ext_auth_id = None
	ext_random_data = None
	"""

	# empty account ID
	# result: pass, it's optional
	"""
	access_key_id = "grVAP1k5xBE3xUhVt7tO"
	secret_access_key = "c1yiaB6l2MqkNChb3oDv7xtN7qeCl8B6LVdi3hDT"
	api_account_id = ""
	ext_auth_id = None
	ext_random_data = None
	"""

	# wrong account ID
	# result: fail,HTTP Error 403: Forbidden
	"""
	access_key_id = "grVAP1k5xBE3xUhVt7tO"
	secret_access_key = "c1yiaB6l2MqkNChb3oDv7xtN7qeCl8B6LVdi3hDT"
	api_account_id = mapi_util.random_str(20)
	ext_auth_id = None
	ext_random_data = None
	"""

	# empty auth ID
	# result: fail,HTTP Error 400: Bad Request
	"""
	access_key_id = "grVAP1k5xBE3xUhVt7tO"
	secret_access_key = "c1yiaB6l2MqkNChb3oDv7xtN7qeCl8B6LVdi3hDT"
	api_account_id = "250C5CF1-62B6-4CDD-91C6-58F0307FE75E"
	ext_auth_id = ""
	ext_random_data = None
	"""

	# wrong auth ID
	# result: fail,HTTP Error 403: Forbidden
	"""
	access_key_id = "grVAP1k5xBE3xUhVt7tO"
	secret_access_key = "c1yiaB6l2MqkNChb3oDv7xtN7qeCl8B6LVdi3hDT"
	api_account_id = "250C5CF1-62B6-4CDD-91C6-58F0307FE75E"
	ext_auth_id = mapi_util.random_str(20)
	ext_random_data = None
	"""

	# auth ID special chars
	# result: fail,HTTP Error 500: Whitespace must appear between attributes. Line 1
	"""
	access_key_id = "grVAP1k5xBE3xUhVt7tO"
	secret_access_key = "c1yiaB6l2MqkNChb3oDv7xtN7qeCl8B6LVdi3hDT"
	api_account_id = "250C5CF1-62B6-4CDD-91C6-58F0307FE75E"
	ext_auth_id = mapi_util.SPECIAL_CHARS
	ext_random_data = None
	"""

	#print userAuthenticationResponse("api_auth", access_key_id, secret_access_key, api_account_id, ext_auth_id, ext_random_data)

	# empty random data
	# result: fail,HTTP Error 403: Forbidden
	"""
	access_key_id = "grVAP1k5xBE3xUhVt7tO"
	secret_access_key = "c1yiaB6l2MqkNChb3oDv7xtN7qeCl8B6LVdi3hDT"
	api_account_id = "250C5CF1-62B6-4CDD-91C6-58F0307FE75E"
	ext_auth_id = None
	ext_random_data = ""
	"""


	# wrong random data
	# result: fail,HTTP Error 403: Forbidden
	"""
	access_key_id = "grVAP1k5xBE3xUhVt7tO"
	secret_access_key = "c1yiaB6l2MqkNChb3oDv7xtN7qeCl8B6LVdi3hDT"
	api_account_id = "250C5CF1-62B6-4CDD-91C6-58F0307FE75E"
	ext_auth_id = None
	ext_random_data = mapi_util.random_str(20)
	"""

	# random data special chars
	# result: fail, Error 500: Whitespace must appear between attributes.
	"""
	access_key_id = "grVAP1k5xBE3xUhVt7tO"
	secret_access_key = "c1yiaB6l2MqkNChb3oDv7xtN7qeCl8B6LVdi3hDT"
	api_account_id = "250C5CF1-62B6-4CDD-91C6-58F0307FE75E"
	ext_auth_id = None
	ext_random_data = mapi_util.SPECIAL_CHARS
	"""

	#print userAuthenticationResponse("api_auth", access_key_id, secret_access_key, api_account_id, ext_auth_id, ext_random_data, False, False, True)

	# auth ID case sensitive
	# result: pass, bug: case id should be sensitive
	"""
	access_key_id = "grVAP1k5xBE3xUhVt7tO"
	secret_access_key = "c1yiaB6l2MqkNChb3oDv7xtN7qeCl8B6LVdi3hDT"
	api_account_id = "250C5CF1-62B6-4CDD-91C6-58F0307FE75E"
	ext_auth_id = None
	ext_random_data = None
	"""

	#print userAuthenticationResponse("api_auth", access_key_id, secret_access_key, api_account_id, ext_auth_id, ext_random_data, True, False)


	# random data case sensitive
	# result: fail,HTTP Error 403: Forbidden
	"""
	access_key_id = "grVAP1k5xBE3xUhVt7tO"
	secret_access_key = "c1yiaB6l2MqkNChb3oDv7xtN7qeCl8B6LVdi3hDT"
	api_account_id = "250C5CF1-62B6-4CDD-91C6-58F0307FE75E"
	ext_auth_id = None
	ext_random_data = None
	"""
	
	#print userAuthenticationResponse("api_auth", access_key_id, secret_access_key, api_account_id, ext_auth_id, ext_random_data, False, True, False)













	# -------------------------------------------
	# -------------------------------------------
	# -------------------------------------------