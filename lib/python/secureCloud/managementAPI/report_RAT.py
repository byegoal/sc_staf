import time
import mapi_lib
import logging
import mapi_util
import simulator_lib
import mapi_config

report_log = logging.getLogger('report_logger')
report_log.setLevel(mapi_config.log_level)
formatter = logging.Formatter('[%(levelname)s][%(filename)s][%(funcName)s][%(lineno)d]-%(message)s ')
handler = logging.StreamHandler()
handler.setFormatter(formatter)
report_log.addHandler(handler)

"""
ToDo:
revise:
getReportList(report_type): 
deleteReport(report_id):

functional:
generateReport
getReport(report_id):
exportReport(report_data): 


"""
def getTemplateList():
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	name="getTemplateList_test"
	desc="this is getTemplateList test"
	maintenance_days="15"
	has_pdf="true"
	has_xls="true"
	num_key_approve="true"
	num_key_deny="true"
	num_key_request="true"
	interval_btn_kr_and_approve="true"
	num_instance="true"
	num_image="true"
	num_device="true"
	console_audit="true"
	policy_audit="true"
	kr_audit="true"
	instance_compute_time="true"
	frequency="OneTime"
	start_datetime="2012-07-01T00:00:00"
	end_datetime="2012-07-04T00:00:00"
	start_time=""
	start_day=""
	start_date=""
	recipient_list="danny_shao@trend.com.tw"
	enable_email="true"


	xml_result = broker_api_lib.createTemplate(name, desc, maintenance_days, has_pdf, has_xls, \
						num_key_approve, num_key_deny, num_key_request, interval_btn_kr_and_approve, \
						num_instance, num_image, num_device, console_audit, policy_audit, \
						kr_audit, instance_compute_time, frequency, start_datetime, end_datetime, \
						start_time, start_day, start_date, recipient_list, enable_email)


	xml_result = broker_api_lib.getTemplateList("A")
	if not xml_result:
		report_log.debug("call getTemplateList return False")
		return False

	found_template = False
	job_list = xml_result.getElementsByTagName("ScheduledJobs")[0]
	jobs = job_list.getElementsByTagName("ScheduledJob")
	for job in jobs:
		if name == job.attributes["Name"].value.strip():
			found_template = True


	template_id = broker_api_lib.get_template_id_from_template_name(name)
	if not template_id:
		report_log.debug("cannot find the template ID")
		return False
	
	xml_result = broker_api_lib.deleteTemplate(template_id)
	if not xml_result:
		report_log.debug("call deleteTemplate return False")
		return False

	if found_template:
		return True
	else:
		report_log.debug("Unable to find the pre-inserted report")
		return False


def loadTemplate():
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	name="loadTemplate_test"
	desc="this is loadTemplate test"
	maintenance_days="15"
	has_pdf="true"
	has_xls="true"
	num_key_approve="true"
	num_key_deny="true"
	num_key_request="true"
	interval_btn_kr_and_approve="true"
	num_instance="true"
	num_image="true"
	num_device="true"
	console_audit="true"
	policy_audit="true"
	kr_audit="true"
	instance_compute_time="true"
	frequency="OneTime"
	start_datetime="2012-07-01T00:00:00"
	end_datetime="2012-07-04T00:00:00"
	start_time=""
	start_day=""
	start_date=""
	recipient_list="danny_shao@trend.com.tw"
	enable_email="true"


	xml_result = broker_api_lib.createTemplate(name, desc, maintenance_days, has_pdf, has_xls, \
						num_key_approve, num_key_deny, num_key_request, interval_btn_kr_and_approve, \
						num_instance, num_image, num_device, console_audit, policy_audit, \
						kr_audit, instance_compute_time, frequency, start_datetime, end_datetime, \
						start_time, start_day, start_date, recipient_list, enable_email)


	template_id = broker_api_lib.get_template_id_from_template_name(name)
	if not template_id:
		report_log.debug("cannot find the template ID")
		return False


	xml_result = broker_api_lib.loadTemplate(template_id)
	if not xml_result:
		report_log.debug("call loadTemplate return False")
		return False

	found_template = False
	template = xml_result.getElementsByTagName("ReportSchedule")[0]
	if name == template.attributes["Name"].value.strip():
		found_template = True

	xml_result = broker_api_lib.deleteTemplate(template_id)
	if not xml_result:
		report_log.debug("call deleteTemplate return False")
		return False

	if found_template:
		return True
	else:
		report_log.debug("Unable to find the pre-inserted report")
		return False



def createTemplate(name, desc, maintenance_days, has_pdf, has_xls, \
						num_key_approve, num_key_deny, num_key_request, interval_btn_kr_and_approve, \
						num_instance, num_image, num_device, console_audit, policy_audit, \
						kr_audit, instance_compute_time, frequency, start_datetime, end_datetime, \
						start_time, start_day, start_date, recipient_list, enable_email):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")


	xml_result = broker_api_lib.createTemplate(name, desc, maintenance_days, has_pdf, has_xls, \
						num_key_approve, num_key_deny, num_key_request, interval_btn_kr_and_approve, \
						num_instance, num_image, num_device, console_audit, policy_audit, \
						kr_audit, instance_compute_time, frequency, start_datetime, end_datetime, \
						start_time, start_day, start_date, recipient_list, enable_email)
	if not xml_result:
		report_log.debug("call createTemplate return False")
		return False


	template_id = broker_api_lib.get_template_id_from_template_name(name)
	if not template_id:
		report_log.debug("cannot find the template ID")
		return False


	xml_result = broker_api_lib.loadTemplate(template_id)
	if not xml_result:
		report_log.debug("call loadTemplate return False")
		return False

	same_template = False
	current_template = xml_result.getElementsByTagName("ReportSchedule")[0]
	same_template = broker_api_lib.compare_report(name, desc, maintenance_days, has_pdf, has_xls, \
						num_key_approve, num_key_deny, num_key_request, interval_btn_kr_and_approve, \
						num_instance, num_image, num_device, console_audit, policy_audit, \
						kr_audit, instance_compute_time, frequency, start_datetime, end_datetime, \
						start_time, start_day, start_date, recipient_list, enable_email, current_template)

	xml_result = broker_api_lib.deleteTemplate(template_id)
	if not xml_result:
		report_log.debug("call deleteTemplate return False")
		return False

	if same_template:
		return True
	else:
		report_log.debug("Report content is not the same after created")
		return False


def deleteTemplate():
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	name="deleteTemplate_test"
	desc="this is deleteTemplate test"
	maintenance_days="15"
	has_pdf="true"
	has_xls="true"
	num_key_approve="true"
	num_key_deny="true"
	num_key_request="true"
	interval_btn_kr_and_approve="true"
	num_instance="true"
	num_image="true"
	num_device="true"
	console_audit="true"
	policy_audit="true"
	kr_audit="true"
	instance_compute_time="true"
	frequency="OneTime"
	start_datetime="2012-07-01T00:00:00"
	end_datetime="2012-07-04T00:00:00"
	start_time=""
	start_day=""
	start_date=""
	recipient_list="danny_shao@trend.com.tw"
	enable_email="true"

	xml_result = broker_api_lib.createTemplate(name, desc, maintenance_days, has_pdf, has_xls, \
						num_key_approve, num_key_deny, num_key_request, interval_btn_kr_and_approve, \
						num_instance, num_image, num_device, console_audit, policy_audit, \
						kr_audit, instance_compute_time, frequency, start_datetime, end_datetime, \
						start_time, start_day, start_date, recipient_list, enable_email)


	template_id = broker_api_lib.get_template_id_from_template_name(name)
	if not template_id:
		report_log.debug("cannot find the template ID")
		return False
	
	xml_result = broker_api_lib.deleteTemplate(template_id)
	if not xml_result:
		report_log.debug("call deleteTemplate return False")
		return False

	template_id = broker_api_lib.get_template_id_from_template_name(name)
	if template_id:
		report_log.debug("template is not deleted")
		return False
	else:
		return True


def updateTemplate(name, desc, maintenance_days, has_pdf, has_xls, \
						num_key_approve, num_key_deny, num_key_request, interval_btn_kr_and_approve, \
						num_instance, num_image, num_device, console_audit, policy_audit, \
						kr_audit, instance_compute_time, frequency, start_datetime, end_datetime, \
						start_time, start_day, start_date, recipient_list, enable_email):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	name_orig="updateTemplate_test_orig"
	desc_orig="this is updateTemplate test orig"
	maintenance_days_orig="10"
	has_pdf_orig="false"
	has_xls_orig="false"
	num_key_approve_orig="true"
	num_key_deny_orig=""
	num_key_request_orig=""
	interval_btn_kr_and_approve_orig=""
	num_instance_orig=""
	num_image_orig=""
	num_device_orig=""
	console_audit_orig=""
	policy_audit_orig=""
	kr_audit_orig=""
	instance_compute_time_orig=""
	frequency_orig="OneTime"
	start_datetime_orig="2012-07-01T00:00:00"
	end_datetime_orig="2012-07-04T00:00:00"
	start_time_orig=""
	start_day_orig=""
	start_date_orig=""
	recipient_list_orig="danny_shao@trend.com.tw"
	enable_email_orig="false"


	xml_result = broker_api_lib.createTemplate(name_orig, desc, maintenance_days_orig, has_pdf_orig, has_xls_orig, \
						num_key_approve_orig, num_key_deny_orig, num_key_request_orig, interval_btn_kr_and_approve_orig, \
						num_instance_orig, num_image_orig, num_device_orig, console_audit_orig, policy_audit_orig, \
						kr_audit_orig, instance_compute_time_orig, frequency_orig, start_datetime_orig, end_datetime_orig, \
						start_time_orig, start_day_orig, start_date_orig, recipient_list_orig, enable_email_orig)
	if not xml_result:
		report_log.debug("call createTemplate return False")
		return False


	template_id = broker_api_lib.get_template_id_from_template_name(name_orig)
	if not template_id:
		report_log.debug("cannot find the template ID")
		return False

	xml_result = broker_api_lib.updateTemplate(template_id, name, desc, maintenance_days, has_pdf, has_xls, \
						num_key_approve, num_key_deny, num_key_request, interval_btn_kr_and_approve, \
						num_instance, num_image, num_device, console_audit, policy_audit, \
						kr_audit, instance_compute_time, frequency, start_datetime, end_datetime, \
						start_time, start_day, start_date, recipient_list, enable_email)
	if not xml_result:
		report_log.debug("call updateTemplate return False")
		return False


	xml_result = broker_api_lib.loadTemplate(template_id)
	if not xml_result:
		report_log.debug("call loadTemplate return False")
		return False

	same_template = False
	current_template = xml_result.getElementsByTagName("ReportSchedule")[0]
	same_template = broker_api_lib.compare_report(name, desc, maintenance_days, has_pdf, has_xls, \
						num_key_approve, num_key_deny, num_key_request, interval_btn_kr_and_approve, \
						num_instance, num_image, num_device, console_audit, policy_audit, \
						kr_audit, instance_compute_time, frequency, start_datetime, end_datetime, \
						start_time, start_day, start_date, recipient_list, enable_email, current_template)

	xml_result = broker_api_lib.deleteTemplate(template_id)
	if not xml_result:
		report_log.debug("call deleteTemplate return False")
		return False

	if same_template:
		return True
	else:
		report_log.debug("Report content is not the same after created")
		return False


def generateReport(name, desc, maintenance_days, has_pdf, has_xls, \
						num_key_approve, num_key_deny, num_key_request, interval_btn_kr_and_approve, \
						num_instance, num_image, num_device, console_audit, policy_audit, \
						kr_audit, instance_compute_time, frequency, start_datetime, end_datetime, \
						start_time, start_day, start_date, recipient_list, enable_email):
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")

	xml_result = broker_api_lib.createTemplate(name, desc, maintenance_days, has_pdf, has_xls, \
						num_key_approve, num_key_deny, num_key_request, interval_btn_kr_and_approve, \
						num_instance, num_image, num_device, console_audit, policy_audit, \
						kr_audit, instance_compute_time, frequency, start_datetime, end_datetime, \
						start_time, start_day, start_date, recipient_list, enable_email)
	if not xml_result:
		report_log.debug("call createTemplate return False")
		return False

	xml_result = broker_api_lib.generateReport(name, desc, maintenance_days, has_pdf, has_xls, \
						num_key_approve, num_key_deny, num_key_request, interval_btn_kr_and_approve, \
						num_instance, num_image, num_device, console_audit, policy_audit, \
						kr_audit, instance_compute_time, frequency, start_datetime, end_datetime, \
						start_time, start_day, start_date, recipient_list, enable_email)
	if not xml_result:
		report_log.debug("call generateReport return False")
		return False


	report_node = xml_result.getElementsByTagName("ReportFile")[0]
	if not report_node:
		report_log.debug("no report file")
		return False
	
	data_node = report_node.getElementsByTagName("Data")[0]
	if not data_node:
		report_log.debug("no report file")
		return False	


	"""
	template_id = broker_api_lib.get_template_id_from_template_name(name)
	if not template_id:
		report_log.debug("cannot find the template ID")
		return False

	xml_result = broker_api_lib.deleteTemplate(template_id)
	if not xml_result:
		report_log.debug("call deleteTemplate return False")
		return False
	"""
	return True


def getReportList():
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	"""
	name="getTemplateList_test"
	desc="this is getTemplateList test"
	maintenance_days="15"
	has_pdf="true"
	has_xls="true"
	num_key_approve="true"
	num_key_deny="true"
	num_key_request="true"
	interval_btn_kr_and_approve="true"
	num_instance="true"
	num_image="true"
	num_device="true"
	console_audit="true"
	policy_audit="true"
	kr_audit="true"
	instance_compute_time="true"
	frequency="OneTime"
	start_datetime="2012-07-01T00:00:00"
	end_datetime="2012-07-04T00:00:00"
	start_time=""
	start_day=""
	start_date=""
	recipient_list="danny_shao@trend.com.tw"
	enable_email="true"


	xml_result = broker_api_lib.createTemplate(name, desc, maintenance_days, has_pdf, has_xls, \
						num_key_approve, num_key_deny, num_key_request, interval_btn_kr_and_approve, \
						num_instance, num_image, num_device, console_audit, policy_audit, \
						kr_audit, instance_compute_time, frequency, start_datetime, end_datetime, \
						start_time, start_day, start_date, recipient_list, enable_email)
	"""

	xml_result = broker_api_lib.getReportList("A")
	if not xml_result:
		report_log.debug("call getReportList return False")
		return False

	"""
	found_report = False
	job_list = xml_result.getElementsByTagName("ArchivedReports")[0]
	jobs = job_list.getElementsByTagName("ArchivedReport")
	for job in jobs:
		if name == job.attributes["Name"].value.strip():
			found_report = True


	report_id = broker_api_lib.get_report_id_from_report_name(name)
	if not report_id:
		report_log.debug("cannot find the report ID")
		return False
	
	xml_result = broker_api_lib.deleteReport(report_id)
	if not xml_result:
		report_log.debug("call deleteReport return False")
		return False

	if found_report:
		return True
	else:
		report_log.debug("Unable to find the pre-inserted report")
		return False
	"""




def getReport():
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	"""
	name="loadTemplate_test"
	desc="this is loadTemplate test"
	maintenance_days="15"
	has_pdf="true"
	has_xls="true"
	num_key_approve="true"
	num_key_deny="true"
	num_key_request="true"
	interval_btn_kr_and_approve="true"
	num_instance="true"
	num_image="true"
	num_device="true"
	console_audit="true"
	policy_audit="true"
	kr_audit="true"
	instance_compute_time="true"
	frequency="OneTime"
	start_datetime="2012-07-01T00:00:00"
	end_datetime="2012-07-04T00:00:00"
	start_time=""
	start_day=""
	start_date=""
	recipient_list="danny_shao@trend.com.tw"
	enable_email="true"


	xml_result = broker_api_lib.createTemplate(name, desc, maintenance_days, has_pdf, has_xls, \
						num_key_approve, num_key_deny, num_key_request, interval_btn_kr_and_approve, \
						num_instance, num_image, num_device, console_audit, policy_audit, \
						kr_audit, instance_compute_time, frequency, start_datetime, end_datetime, \
						start_time, start_day, start_date, recipient_list, enable_email)
	"""

	# delete later
	name="[Name of your report] (09 Jul 2012 02:11:30 UTC)"

	report_id = broker_api_lib.get_report_id_from_report_name(name)
	if not report_id:
		report_log.debug("cannot find the report ID")
		return False


	xml_result = broker_api_lib.getReport(report_id)
	if not xml_result:
		report_log.debug("call getReport return False")
		return False

	found_report = False
	report = xml_result.getElementsByTagName("ArchivedReport")[0]
	if name == report.attributes["Name"].value.strip():
		found_report = True

	xml_result = broker_api_lib.deleteReport(template_id)
	if not xml_result:
		report_log.debug("call deleteReport return False")
		return False

	if found_report:
		return True
	else:
		report_log.debug("Unable to find the pre-inserted report")
		return False




def deleteReport():
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	"""
	name="deleteTemplate_test"
	desc="this is deleteTemplate test"
	maintenance_days="15"
	has_pdf="true"
	has_xls="true"
	num_key_approve="true"
	num_key_deny="true"
	num_key_request="true"
	interval_btn_kr_and_approve="true"
	num_instance="true"
	num_image="true"
	num_device="true"
	console_audit="true"
	policy_audit="true"
	kr_audit="true"
	instance_compute_time="true"
	frequency="OneTime"
	start_datetime="2012-07-01T00:00:00"
	end_datetime="2012-07-04T00:00:00"
	start_time=""
	start_day=""
	start_date=""
	recipient_list="danny_shao@trend.com.tw"
	enable_email="true"

	xml_result = broker_api_lib.createTemplate(name, desc, maintenance_days, has_pdf, has_xls, \
						num_key_approve, num_key_deny, num_key_request, interval_btn_kr_and_approve, \
						num_instance, num_image, num_device, console_audit, policy_audit, \
						kr_audit, instance_compute_time, frequency, start_datetime, end_datetime, \
						start_time, start_day, start_date, recipient_list, enable_email)
	"""

	#delete later
	name = "[Name of your report] (05 Jul 2012 08:09:39 UTC)"

	report_id = broker_api_lib.get_report_id_from_report_name(name)
	print report_id
	if not report_id:
		report_log.debug("cannot find the template ID")
		return False
	
	xml_result = broker_api_lib.deleteReport(report_id)
	if not xml_result:
		report_log.debug("call deleteTemplate return False")
		return False

	report_id = broker_api_lib.get_report_id_from_report_name(name)
	print report_id
	if report_id:
		report_log.debug("report is not deleted")
		return False
	else:
		return True


def exportReport():
	broker_api_lib = mapi_lib.mapi_lib(auth_type="api_auth")
	
	return



def temp():
	template_list = ["3d843f8d-07e4-4249-ad84-11b61891735f",
	"15b81d3a-b6a3-4388-861e-439e08977cdb",
	"2b98f9c5-7126-49a7-a3eb-aaedf838d519",
	"b755f15e-4b5b-429f-98e9-56b1019f84d0",
	"a4b6f47a-e24a-4b5e-85aa-37f058fc995a",
	"99fc5f5a-45c1-4271-ad34-c7af0a8f2675"]
	for template_id in template_list:
		xml_result = broker_api_lib.deleteTemplate(template_id)
		if not xml_result:
			report_log.debug("call deleteTemplate return False")
			return False


if __name__ == '__main__':
	name="createTemplate_test"
	desc="this is createTemplate test"
	maintenance_days="15"
	has_pdf="true"
	has_xls="true"
	num_key_approve="true"
	num_key_deny="true"
	num_key_request="true"
	interval_btn_kr_and_approve="true"
	num_instance="true"
	num_image="true"
	num_device="true"
	console_audit="true"
	policy_audit="true"
	kr_audit="true"
	instance_compute_time="true"
	frequency="OneTime"
	start_datetime="2012-07-01T00:00:00"
	end_datetime="2012-07-04T00:00:00"
	start_time=""
	start_day=""
	start_date=""
	recipient_list="danny_shao@trend.com.tw"
	enable_email="true"


	#print createTemplate(name, desc, maintenance_days, has_pdf, has_xls, \
	#					num_key_approve, num_key_deny, num_key_request, interval_btn_kr_and_approve, \
	#					num_instance, num_image, num_device, console_audit, policy_audit, \
	#					kr_audit, instance_compute_time, frequency, start_datetime, end_datetime, \
	#					start_time, start_day, start_date, recipient_list, enable_email)


	#print getTemplateList()

	#print loadTemplate()

	#print deleteTemplate()

	#temp()

	name="updateTemplate_test"
	desc="this is updateTemplate test"
	maintenance_days="15"
	has_pdf="true"
	has_xls="true"
	num_key_approve="true"
	num_key_deny="true"
	num_key_request="true"
	interval_btn_kr_and_approve="true"
	num_instance="true"
	num_image="true"
	num_device="true"
	console_audit="true"
	policy_audit="true"
	kr_audit="true"
	instance_compute_time="true"
	frequency="Weekly"
	start_datetime="2012-07-01T00:00:00"
	end_datetime="2012-07-04T00:00:00"
	start_time="8"
	start_day="2"
	start_date=""
	recipient_list="danny_shao@trend.com.tw"
	enable_email="true"


	#print updateTemplate(name, desc, maintenance_days, has_pdf, has_xls, \
	#					num_key_approve, num_key_deny, num_key_request, interval_btn_kr_and_approve, \
	#					num_instance, num_image, num_device, console_audit, policy_audit, \
	#					kr_audit, instance_compute_time, frequency, start_datetime, end_datetime, \
	#					start_time, start_day, start_date, recipient_list, enable_email)



	name="generateReport_test"
	desc="this is generateReport test"
	maintenance_days="15"
	has_pdf="true"
	has_xls="false"
	num_key_approve="true"
	num_key_deny="true"
	num_key_request="true"
	interval_btn_kr_and_approve="true"
	num_instance="true"
	num_image="true"
	num_device="true"
	console_audit="true"
	policy_audit="true"
	kr_audit="true"
	instance_compute_time="true"
	frequency="OneTime"
	start_datetime="2012-07-01T00:00:00"
	end_datetime="2012-07-04T00:00:00"
	start_time=""
	start_day=""
	start_date=""
	recipient_list="danny_shao@trend.com.tw"
	enable_email="true"


	#print generateReport(name, desc, maintenance_days, has_pdf, has_xls, \
	#					num_key_approve, num_key_deny, num_key_request, interval_btn_kr_and_approve, \
	#					num_instance, num_image, num_device, console_audit, policy_audit, \
	#					kr_audit, instance_compute_time, frequency, start_datetime, end_datetime, \
	#					start_time, start_day, start_date, recipient_list, enable_email)


	#getReportList()


	#print deleteReport()

	#print getReport()