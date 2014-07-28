import time
import mapi_lib
import logging
import mapi_util
import simulator_lib
import mapi_config

notify_log = logging.getLogger('notify_logger')
notify_log.setLevel(mapi_config.log_level)
formatter = logging.Formatter('[%(levelname)s][%(filename)s][%(funcName)s][%(lineno)d]-%(message)s ')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
notify_log.addHandler(handler)


#ToDo
"""
how user can get the notificationRuleEventDBID?



"""
def listAllNotifiers():
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	#create a notification
	notify_name="listAllNotifiers_test"
	desc="this is listAllNotifiers test"
	header="this is header"
	footer="this is footer"
	frequencyUnit="Minutes"
	frequencyValue="1"
	from_email="noreply@cloud9.identum.com"
	subject="this is MAPI listAllNotifiers test"
	recipients_list=["danny_shao@trend.com.tw"]
	key_manual_approve_notify=True
	key_manual_approve_notify_text=""
	key_auto_deny_notify=True
	key_auto_deny_notify_text=""
	key_auto_approve_notify=True
	key_auto_approve_notify_text=""
	key_auto_approve_after_delay_notify=True
	key_auto_approve_after_delay_notify_text=""
	kr_device_and_image_belong_diff_policy_notify=True
	kr_device_and_image_belong_diff_policy_notify_text=""
	scim_fail_notify=True
	scim_fail_notify_text=""
	device_provision_notify=True
	device_provision_notify_text=""
	provision_done_notify=True
	provision_done_notify_text=""
	provision_idle_notify=True
	provision_idle_notify_text=""
	provision_idle_time=""
	kmip_connection_fail_notify=True
	kmip_connection_fail_notify_text=""
	dsm_connection_fail_notify=True
	dsm_connection_fail_notify_text=""

	xml_result = broker_api_lib.createNotifier(notify_name, desc, header, footer, frequencyUnit, frequencyValue, \
					from_email, subject, recipients_list, key_manual_approve_notify, key_manual_approve_notify_text, \
					key_auto_deny_notify, key_auto_deny_notify_text, key_auto_approve_notify, key_auto_approve_notify_text, \
					key_auto_approve_after_delay_notify, key_auto_approve_after_delay_notify_text, \
					kr_device_and_image_belong_diff_policy_notify, kr_device_and_image_belong_diff_policy_notify_text, \
					scim_fail_notify, scim_fail_notify_text, device_provision_notify, device_provision_notify_text, \
					provision_done_notify, provision_done_notify_text, provision_idle_notify, provision_idle_notify_text, provision_idle_time, \
					kmip_connection_fail_notify, kmip_connection_fail_notify_text, dsm_connection_fail_notify, dsm_connection_fail_notify_text)
	if not xml_result:
		notify_log.debug("call createNotifier return False")
		return False

	xml_result = broker_api_lib.listAllNotifiers()
	if not xml_result:
		notify_log.debug("call listAllNotifiers return False")
		return False

	found_notify = False
	notify_list = xml_result.getElementsByTagName("notifierList")[0]
	notify_summaries = notify_list.getElementsByTagName("notifierSummary")
	for notify_summary in notify_summaries:
		if notify_name == notify_summary.attributes["name"].value.strip():
			found_notify = True	

	notify_id = broker_api_lib.get_notify_id_from_notify_name(notify_name)
	if not notify_id:
		notify_log.debug("notify id is not found")
		return False

	xml_result = broker_api_lib.deleteNotifier(notify_id)
	if not xml_result:
		notify_log.debug("call deleteNotifiers return False")
		return False

	if found_notify:
		return True
	else:
		notify_log.debug("pre-created notification is not found")	
		return False



def getNotificationEvents():
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	#create a notification
	notify_name="getNotificationEvents_test"
	desc="this is getNotificationEvents test"
	header="this is header"
	footer="this is footer"
	frequencyUnit="Minutes"
	frequencyValue="1"
	from_email="noreply@cloud9.identum.com"
	subject="this is MAPI getNotificationEvents test"
	recipients_list=["danny_shao@trend.com.tw"]
	key_manual_approve_notify=True
	key_manual_approve_notify_text=""
	key_auto_deny_notify=True
	key_auto_deny_notify_text=""
	key_auto_approve_notify=True
	key_auto_approve_notify_text=""
	key_auto_approve_after_delay_notify=True
	key_auto_approve_after_delay_notify_text=""
	kr_device_and_image_belong_diff_policy_notify=True
	kr_device_and_image_belong_diff_policy_notify_text=""
	scim_fail_notify=True
	scim_fail_notify_text=""
	device_provision_notify=True
	device_provision_notify_text=""
	provision_done_notify=True
	provision_done_notify_text=""
	provision_idle_notify=True
	provision_idle_notify_text=""
	provision_idle_time=""
	kmip_connection_fail_notify=True
	kmip_connection_fail_notify_text=""
	dsm_connection_fail_notify=True
	dsm_connection_fail_notify_text=""

	xml_result = broker_api_lib.createNotifier(notify_name, desc, header, footer, frequencyUnit, frequencyValue, \
					from_email, subject, recipients_list, key_manual_approve_notify, key_manual_approve_notify_text, \
					key_auto_deny_notify, key_auto_deny_notify_text, key_auto_approve_notify, key_auto_approve_notify_text, \
					key_auto_approve_after_delay_notify, key_auto_approve_after_delay_notify_text, \
					kr_device_and_image_belong_diff_policy_notify, kr_device_and_image_belong_diff_policy_notify_text, \
					scim_fail_notify, scim_fail_notify_text, device_provision_notify, device_provision_notify_text, \
					provision_done_notify, provision_done_notify_text, provision_idle_notify, provision_idle_notify_text, provision_idle_time, \
					kmip_connection_fail_notify, kmip_connection_fail_notify_text, dsm_connection_fail_notify, dsm_connection_fail_notify_text)
	if not xml_result:
		notify_log.debug("call createNotifier return False")
		return False

	notify_id = broker_api_lib.get_notify_id_from_notify_name(notify_name)
	if not notify_id:
		notify_log.debug("notify id is not found")
		return False


	xml_result = broker_api_lib.getNotificationEvents(notify_id)
	if not xml_result:
		notify_log.debug("call getNotificationEvents return False")
		return False

	found_notify = False
	notify_node = xml_result.getElementsByTagName("notifier")[0]
	if notify_name == notify_node.attributes["name"].value.strip():
		found_notify = True	

	xml_result = broker_api_lib.deleteNotifier(notify_id)
	if not xml_result:
		notify_log.debug("call deleteNotifiers return False")
		return False

	if found_notify:
		return True
	else:
		notify_log.debug("cannot find the notification")
		return False

def createNotifier(notify_name, desc, header, footer, frequencyUnit, frequencyValue, \
					from_email, subject, recipients_list, key_manual_approve_notify, key_manual_approve_notify_text, \
					key_auto_deny_notify, key_auto_deny_notify_text, key_auto_approve_notify, key_auto_approve_notify_text, \
					key_auto_approve_after_delay_notify, key_auto_approve_after_delay_notify_text, \
					kr_device_and_image_belong_diff_policy_notify, kr_device_and_image_belong_diff_policy_notify_text, \
					scim_fail_notify, scim_fail_notify_text, device_provision_notify, device_provision_notify_text, \
					provision_done_notify, provision_done_notify_text, provision_idle_notify, provision_idle_notify_text, provision_idle_time, \
					kmip_connection_fail_notify, kmip_connection_fail_notify_text, dsm_connection_fail_notify, dsm_connection_fail_notify_text):

	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")

	xml_result = broker_api_lib.createNotifier(notify_name, desc, header, footer, frequencyUnit, frequencyValue, \
					from_email, subject, recipients_list, key_manual_approve_notify, key_manual_approve_notify_text, \
					key_auto_deny_notify, key_auto_deny_notify_text, key_auto_approve_notify, key_auto_approve_notify_text, \
					key_auto_approve_after_delay_notify, key_auto_approve_after_delay_notify_text, \
					kr_device_and_image_belong_diff_policy_notify, kr_device_and_image_belong_diff_policy_notify_text, \
					scim_fail_notify, scim_fail_notify_text, device_provision_notify, device_provision_notify_text, \
					provision_done_notify, provision_done_notify_text, provision_idle_notify, provision_idle_notify_text, provision_idle_time, \
					kmip_connection_fail_notify, kmip_connection_fail_notify_text, dsm_connection_fail_notify, dsm_connection_fail_notify_text)
	if not xml_result:
		notify_log.debug("call createNotifier return False")
		return False

	notify_id = broker_api_lib.get_notify_id_from_notify_name(notify_name)
	if not notify_id:
		notify_log.debug("notify id is not found")
		return False

	xml_result = broker_api_lib.deleteNotifier(notify_id)
	if not xml_result:
		notify_log.debug("call deleteNotifiers return False")
		return False


	return True


def updateNotifier(notify_name, desc, header, footer, frequencyUnit, frequencyValue, \
					from_email, subject, recipients_list, key_manual_approve_notify, key_manual_approve_notify_text, \
					key_auto_deny_notify, key_auto_deny_notify_text, key_auto_approve_notify, key_auto_approve_notify_text, \
					key_auto_approve_after_delay_notify, key_auto_approve_after_delay_notify_text, \
					kr_device_and_image_belong_diff_policy_notify, kr_device_and_image_belong_diff_policy_notify_text, \
					scim_fail_notify, scim_fail_notify_text, device_provision_notify, device_provision_notify_text, \
					provision_done_notify, provision_done_notify_text, provision_idle_notify, provision_idle_notify_text, provision_idle_time, \
					kmip_connection_fail_notify, kmip_connection_fail_notify_text, dsm_connection_fail_notify, dsm_connection_fail_notify_text):

	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	#create a notification
	notify_name_orig="updateNotifier_test_orig"
	desc_orig="this is updateNotifier test_orig"
	header_orig="this is header_orig"
	footer_orig="this is footer_orig"
	frequencyUnit_orig="Individual"
	frequencyValue_orig="0"
	from_email_orig="noreply_orig@cloud9.identum.com"
	subject_orig="this is MAPI updateNotifier test_orig"
	recipients_list_orig=["danny_shao_orig@trend.com.tw"]
	key_manual_approve_notify_orig=True
	key_manual_approve_notify_text_orig=""
	key_auto_deny_notify_orig=False
	key_auto_deny_notify_text_orig=""
	key_auto_approve_notify_orig=False
	key_auto_approve_notify_text_orig=""
	key_auto_approve_after_delay_notify_orig=False
	key_auto_approve_after_delay_notify_text_orig=""
	kr_device_and_image_belong_diff_policy_notify_orig=False
	kr_device_and_image_belong_diff_policy_notify_text_orig=""
	scim_fail_notify_orig=False
	scim_fail_notify_text_orig=""
	device_provision_notify_orig=False
	device_provision_notify_text_orig=""
	provision_done_notify_orig=False
	provision_done_notify_text_orig=""
	provision_idle_notify_orig=False
	provision_idle_notify_text_orig=""
	provision_idle_time_orig=""
	kmip_connection_fail_notify_orig=False
	kmip_connection_fail_notify_text_orig=""
	dsm_connection_fail_notify_orig=False
	dsm_connection_fail_notify_text_orig=""

	xml_result = broker_api_lib.createNotifier(notify_name_orig, desc_orig, header_orig, footer_orig, frequencyUnit_orig, frequencyValue_orig, \
					from_email_orig, subject_orig, recipients_list_orig, key_manual_approve_notify_orig, key_manual_approve_notify_text_orig, \
					key_auto_deny_notify_orig, key_auto_deny_notify_text_orig, key_auto_approve_notify_orig, key_auto_approve_notify_text_orig, \
					key_auto_approve_after_delay_notify_orig, key_auto_approve_after_delay_notify_text_orig, \
					kr_device_and_image_belong_diff_policy_notify_orig, kr_device_and_image_belong_diff_policy_notify_text_orig, \
					scim_fail_notify_orig, scim_fail_notify_text_orig, device_provision_notify_orig, device_provision_notify_text_orig, \
					provision_done_notify_orig, provision_done_notify_text_orig, provision_idle_notify_orig, provision_idle_notify_text_orig, provision_idle_time_orig, \
					kmip_connection_fail_notify_orig, kmip_connection_fail_notify_text_orig, dsm_connection_fail_notify_orig, dsm_connection_fail_notify_text_orig)
	if not xml_result:
		notify_log.debug("call createNotifier return False")
		return False

	notify_id = broker_api_lib.get_notify_id_from_notify_name(notify_name_orig)
	if not notify_id:
		notify_log.debug("notify id is not found")
		return False


	xml_result = broker_api_lib.updateNotifier(notify_id, notify_name, desc, header, footer, frequencyUnit, frequencyValue, \
					from_email, subject, recipients_list, key_manual_approve_notify, key_manual_approve_notify_text, \
					key_auto_deny_notify, key_auto_deny_notify_text, key_auto_approve_notify, key_auto_approve_notify_text, \
					key_auto_approve_after_delay_notify, key_auto_approve_after_delay_notify_text, \
					kr_device_and_image_belong_diff_policy_notify, kr_device_and_image_belong_diff_policy_notify_text, \
					scim_fail_notify, scim_fail_notify_text, device_provision_notify, device_provision_notify_text, \
					provision_done_notify, provision_done_notify_text, provision_idle_notify, provision_idle_notify_text, provision_idle_time, \
					kmip_connection_fail_notify, kmip_connection_fail_notify_text, dsm_connection_fail_notify, dsm_connection_fail_notify_text)
	if not xml_result:
		notify_log.debug("call updateNotifier return False")
		return False


	xml_result = broker_api_lib.getNotificationEvents(notify_id)
	if not xml_result:
		notify_log.debug("call getNotificationEvents return False")
		return False

	notify_node = xml_result.getElementsByTagName("notifier")[0]
	is_same_notify = broker_api_lib.compare_notify(notify_name, desc, header, footer, frequencyUnit, frequencyValue, \
					from_email, subject, recipients_list, key_manual_approve_notify, key_manual_approve_notify_text, \
					key_auto_deny_notify, key_auto_deny_notify_text, key_auto_approve_notify, key_auto_approve_notify_text, \
					key_auto_approve_after_delay_notify, key_auto_approve_after_delay_notify_text, \
					kr_device_and_image_belong_diff_policy_notify, kr_device_and_image_belong_diff_policy_notify_text, \
					scim_fail_notify, scim_fail_notify_text, device_provision_notify, device_provision_notify_text, \
					provision_done_notify, provision_done_notify_text, provision_idle_notify, provision_idle_notify_text, provision_idle_time, \
					kmip_connection_fail_notify, kmip_connection_fail_notify_text, dsm_connection_fail_notify, dsm_connection_fail_notify_text, \
					notify_node)

	xml_result = broker_api_lib.deleteNotifier(notify_id)
	if not xml_result:
		notify_log.debug("call deleteNotifiers return False")
		return False

	if is_same_notify:
		return True
	else:
		notify_log.debug("some values are not updated")
		return False



def deleteNotifier():
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	#create a notification
	notify_name="deleteNotifier"
	desc="this is deleteNotifier test"
	header="this is header"
	footer="this is footer"
	frequencyUnit="Minutes"
	frequencyValue="1"
	from_email="noreply@cloud9.identum.com"
	subject="this is MAPI deleteNotifier test"
	recipients_list=["danny_shao@trend.com.tw"]
	key_manual_approve_notify=True
	key_manual_approve_notify_text=""
	key_auto_deny_notify=True
	key_auto_deny_notify_text=""
	key_auto_approve_notify=True
	key_auto_approve_notify_text=""
	key_auto_approve_after_delay_notify=True
	key_auto_approve_after_delay_notify_text=""
	kr_device_and_image_belong_diff_policy_notify=True
	kr_device_and_image_belong_diff_policy_notify_text=""
	scim_fail_notify=True
	scim_fail_notify_text=""
	device_provision_notify=True
	device_provision_notify_text=""
	provision_done_notify=True
	provision_done_notify_text=""
	provision_idle_notify=True
	provision_idle_notify_text=""
	provision_idle_time=""
	kmip_connection_fail_notify=True
	kmip_connection_fail_notify_text=""
	dsm_connection_fail_notify=True
	dsm_connection_fail_notify_text=""

	xml_result = broker_api_lib.createNotifier(notify_name, desc, header, footer, frequencyUnit, frequencyValue, \
					from_email, subject, recipients_list, key_manual_approve_notify, key_manual_approve_notify_text, \
					key_auto_deny_notify, key_auto_deny_notify_text, key_auto_approve_notify, key_auto_approve_notify_text, \
					key_auto_approve_after_delay_notify, key_auto_approve_after_delay_notify_text, \
					kr_device_and_image_belong_diff_policy_notify, kr_device_and_image_belong_diff_policy_notify_text, \
					scim_fail_notify, scim_fail_notify_text, device_provision_notify, device_provision_notify_text, \
					provision_done_notify, provision_done_notify_text, provision_idle_notify, provision_idle_notify_text, provision_idle_time, \
					kmip_connection_fail_notify, kmip_connection_fail_notify_text, dsm_connection_fail_notify, dsm_connection_fail_notify_text)
	if not xml_result:
		notify_log.debug("call createNotifier return False")
		return False

	notify_id = broker_api_lib.get_notify_id_from_notify_name(notify_name)
	if not notify_id:
		notify_log.debug("notify id is not found")
		return False

	xml_result = broker_api_lib.deleteNotifier(notify_id)
	if not xml_result:
		notify_log.debug("call deleteNotifiers return False")
		return False

	return True



if __name__ == '__main__':
	notify_name="createNotifier_test"
	desc="this is createNotifier test"
	header="this is header"
	footer="this is footer"
	frequencyUnit="Minutes"
	frequencyValue="1"
	from_email="noreply@cloud9.identum.com"
	subject="this is MAPI createNotifier test"
	recipients_list=["danny_shao@trend.com.tw"]
	key_manual_approve_notify=True
	key_manual_approve_notify_text=""
	key_auto_deny_notify=True
	key_auto_deny_notify_text=""
	key_auto_approve_notify=True
	key_auto_approve_notify_text=""
	key_auto_approve_after_delay_notify=True
	key_auto_approve_after_delay_notify_text=""
	kr_device_and_image_belong_diff_policy_notify=True
	kr_device_and_image_belong_diff_policy_notify_text=""
	scim_fail_notify=True
	scim_fail_notify_text=""
	device_provision_notify=True
	device_provision_notify_text=""
	provision_done_notify=True
	provision_done_notify_text=""
	provision_idle_notify=True
	provision_idle_notify_text=""
	provision_idle_time=""
	kmip_connection_fail_notify=True
	kmip_connection_fail_notify_text=""
	dsm_connection_fail_notify=True
	dsm_connection_fail_notify_text=""

	#print createNotifier(notify_name, desc, header, footer, frequencyUnit, frequencyValue, \
	#				from_email, subject, recipients_list, key_manual_approve_notify, key_manual_approve_notify_text, \
	#				key_auto_deny_notify, key_auto_deny_notify_text, key_auto_approve_notify, key_auto_approve_notify_text, \
	#				key_auto_approve_after_delay_notify, key_auto_approve_after_delay_notify_text, \
	#				kr_device_and_image_belong_diff_policy_notify, kr_device_and_image_belong_diff_policy_notify_text, \
	#				scim_fail_notify, scim_fail_notify_text, device_provision_notify, device_provision_notify_text, \
	#				provision_done_notify, provision_done_notify_text, provision_idle_notify, provision_idle_notify_text, provision_idle_time, \
	#				kmip_connection_fail_notify, kmip_connection_fail_notify_text, dsm_connection_fail_notify, dsm_connection_fail_notify_text)


	#print listAllNotifiers()

	#print deleteNotifier()

	#print getNotificationEvents()

	notify_name="updateNotifier_test"
	desc="this is updateNotifier test"
	header="this is header"
	footer="this is footer"
	frequencyUnit="Minutes"
	frequencyValue="1"
	from_email="noreply@cloud9.identum.com"
	subject="this is MAPI updateNotifier test"
	recipients_list=["danny_shao@trend.com.tw"]
	key_manual_approve_notify=True
	key_manual_approve_notify_text="manual approve updated"
	key_auto_deny_notify=True
	key_auto_deny_notify_text="deny notify updated"
	key_auto_approve_notify=True
	key_auto_approve_notify_text="key approve updated"
	key_auto_approve_after_delay_notify=True
	key_auto_approve_after_delay_notify_text="approve after delay updated"
	kr_device_and_image_belong_diff_policy_notify=True
	kr_device_and_image_belong_diff_policy_notify_text="belong diff policy updated"
	scim_fail_notify=True
	scim_fail_notify_text="sicm notify updated"
	device_provision_notify=True
	device_provision_notify_text="provision notify updated"
	provision_done_notify=True
	provision_done_notify_text="provision done notify updated"
	provision_idle_notify=True
	provision_idle_notify_text="provision idle updated"
	provision_idle_time="10"
	kmip_connection_fail_notify=True
	kmip_connection_fail_notify_text="kmip fail updated"
	dsm_connection_fail_notify=True
	dsm_connection_fail_notify_text="dsm fail updated"

	#print updateNotifier(notify_name, desc, header, footer, frequencyUnit, frequencyValue, \
	#				from_email, subject, recipients_list, key_manual_approve_notify, key_manual_approve_notify_text, \
	#				key_auto_deny_notify, key_auto_deny_notify_text, key_auto_approve_notify, key_auto_approve_notify_text, \
	#				key_auto_approve_after_delay_notify, key_auto_approve_after_delay_notify_text, \
	#				kr_device_and_image_belong_diff_policy_notify, kr_device_and_image_belong_diff_policy_notify_text, \
	#				scim_fail_notify, scim_fail_notify_text, device_provision_notify, device_provision_notify_text, \
	#				provision_done_notify, provision_done_notify_text, provision_idle_notify, provision_idle_notify_text, provision_idle_time, \
	#				kmip_connection_fail_notify, kmip_connection_fail_notify_text, dsm_connection_fail_notify, dsm_connection_fail_notify_text)

