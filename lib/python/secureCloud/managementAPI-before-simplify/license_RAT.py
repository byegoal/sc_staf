import time
import mapi_lib
import logging
import mapi_util
import mapi_config
import simulator_lib

license_log = logging.getLogger('license_logger')
license_log.setLevel(mapi_config.log_level)
formatter = logging.Formatter('[%(levelname)s][%(filename)s][%(funcName)s][%(lineno)d]-%(message)s ')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
license_log.addHandler(handler)


def listLicenses():
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	#pre-inserted license
	ac = "SD-7VP8-6TSFV-PUKPP-3LFEF-YLLXM-PRKKG"

	xml_result = broker_api_lib.listLicenses()
	if not xml_result:
		license_log.debug("call listLicenses return False")
		return False

	found_ac = False
	license_list = xml_result.getElementsByTagName("licenseList")[0]
	licenses = license_list.getElementsByTagName("license")
	for license in licenses:
		if ac == license.attributes["ac"].value.strip():
			found_ac = True

	if found_ac:
		return True
	else:
		license_log.debug("No license is found")
		return False


def getLicense():
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	#pre-inserted license
	ac = "SD-7VP8-6TSFV-PUKPP-3LFEF-YLLXM-PRKKG"

	license_id = broker_api_lib.get_license_id_from_ac(ac)
	if not license_id:
		license_log.debug("no license id is found")
		return False

	xml_result = broker_api_lib.getLicense(license_id)
	if not xml_result:
		license_log.debug("call getLicense return False")
		return False

	license = xml_result.getElementsByTagName("license")[0]
	current_ac = license.attributes["ac"].value.strip()
	if ac == current_ac:
		return True
	else:
		license_log.debug("cannot find the license")
		return False

# todo test
def addLicense(ac):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")

	xml_result = broker_api_lib.addLicense(ac)
	if not xml_result:
		return False

	"""
	xml_result = broker_api_lib.getLicense(license_id)
	if not xml_result:
		return False
	
	license = xml_result.getElementsByTagName("license")[0]
	if license:
		return True
	else:
		return False
	"""

	return True

# todo test
def updateLicense():
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	license_id="1"
	xml_result = broker_api_lib.updateLicense(license_id)
	if not xml_result:
		license_log.debug("call updateLicense return False")
		return False

	"""
	xml_result = broker_api_lib.getLicense(license_id)
	if not xml_result:
		return False
	
	license = xml_result.getElementsByTagName("license")[0]
	if license:
		return True
	else:
		return False
	"""

	return True


# Not work, UI has error as well
def updateLicenseOnline():
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	#pre-inserted license
	ac = "SD-7VP8-6TSFV-PUKPP-3LFEF-YLLXM-PRKKG"

	license_id = broker_api_lib.get_license_id_from_ac(ac)
	if not license_id:
		license_log.debug("no license id is found")
		return False


	xml_result = broker_api_lib.updateLicenseOnline(license_id)
	if not xml_result:
		license_log.debug("call updateLicenseOnline return False")
		return False

	"""
	xml_result = broker_api_lib.getLicense(license_id)
	if not xml_result:
		return False
	
	license = xml_result.getElementsByTagName("license")[0]
	if license:
		return True
	else:
		return False
	"""

	return True

if __name__ == '__main__':

	"""
	SD-7VP8-6TSFV-PUKPP-3LFEF-YLLXM-PRKKG
	SD-D5L6-3GZJ9-LV58P-CXGNB-MTYZV-KAQMD
	SD-UVDB-QN7ES-KJ9DR-4FRJR-T6CDK-EZWAK
	"""

	#print listLicenses()

	#print getLicense()

	#ac = "SD-RWCK-5AZT9-R3KGT-PNBPL-BN4GE-GSBRQ"
	#print addLicense(ac)

	#print updateLicenseOnline()

	print updateLicense()