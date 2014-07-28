import time
import managementAPI.policy_api as policy_api
from xml.dom.minidom import parse, parseString
import logging


def createPolicy(policy_id, policy_name, image_id, device_id):

	print "in policy_test_lib createPolicy"
	print time.ctime()

	import secureCloud.policyTest.policy_config
	
	# read policy xml and replace image and device ID
	policy_path = secureCloud.policyTest.policy_config.sample_policy_path
	f = open(policy_path+policy_id, "r")
	test_data = f.read()
	test_data = test_data.format(policy_name, device_id, image_id)
	#print(test_data)

	#call API to create policy
	result = policy_api.createPolicy(test_data)
	
	#f = open("c:\\test-return.xml", "w")
	#f.write(test_data)


	dom_result = parseString(result)

	print "out policy_test_lib createPolicy"
	print time.ctime()

	if(not dom_result):
		return 0

	security_group = dom_result.getElementsByTagName("securityGroup")[0]
	if(not security_group):
		return 0

	return 1


def autoCreatePolicy(policy_name, image_id, device_id, security_rules):

	print "in policy_test_lib autoCreatePolicy"
	print time.ctime()

	test_data = createPolicyTemplate(policy_name, image_id, device_id, security_rules)
	#print(test_data)

	#f = open("c:\\test-return.xml", "w")
	#f.write(test_data)

	#call API to create policy
	result = policy_api.createPolicy(test_data)

	dom_result = parseString(result)
	if(not dom_result):
		return 0

	security_group = dom_result.getElementsByTagName("securityGroup")[0]

	print "out policy_test_lib autoCreatePolicy"
	print time.ctime()

	if(not security_group):
		return 0

	return 1


def createPolicyTemplate(policy_name, image_id, device_id, security_rules):

	print "%s, %s, %s" % (policy_name, image_id, device_id)


	policy_template = """<securityGroup 
	EnableIC="false" 
	ICAction="Nothing" 
	RevokeIntervalNumber="-1" 
	RevokeIntervalType="Hour" 
	isDeleteble="false" 
	isNameEditable="false" 
	isResourcePool="false" 
	name="%s">
	<description/>
	<successAction action="Approve" autoDelay="-1"/>
	<failedAction action="Deny" autoDelay="-1"/>
	<deviceList>
		<device id="%s"></device>
	</deviceList>
	<imageList>
		<image id="%s"></image>
	</imageList>
	<securityRuleList>
	""" % (policy_name, device_id, image_id)

	for security_rule in security_rules:

		policy_template += """<securityRule 
			id="%s" 
			matchType="%s">
			""" % (security_rule["id"], security_rule["matchType"])

		#print "id:" + security_rule["id"]
		#print "matchType:" + security_rule["matchType"]

		policy_template += "<securityRuleConditionList>\n"
		for condition in security_rule["condition_list"]:
			policy_template += """<securityRuleCondition evaluator="%s" expectedValue="%s"/>""" % (condition["evaluator"], condition["expectedValue"])
			#print "evaluator:" + condition["evaluator"]
			#print "expectedValue:" + condition["expectedValue"]
		policy_template += "</securityRuleConditionList>\n"

		policy_template += "</securityRule>\n"

	policy_template += """</securityRuleList>
</securityGroup>"""

	#print policy_template
	return policy_template

def evaluatePolicy(policy_name, device_id):
	# to-do to evaluation and parse result to see if pass or not
	# 1.get key request ID
	result = policy_api.getKeyRequestTree()

	#f = open("c:\\test-return.xml", "w")
	#f.write(result)
	
	dom_result = parseString(result)
	key_request_tree = dom_result.getElementsByTagName("keyRequestTree")[0]
	flat_requests = key_request_tree.getElementsByTagName("flatRequests")[0]
	flat_request = flat_requests.getElementsByTagName("flatRequest")

	for node in flat_request:
		current_policy_name = node.getAttribute("policyName")
		current_instance_id = node.getAttribute("instanceID")
		current_integrity = node.getAttribute("integrity")

		logging.debug("%s,%s,%s" % (current_policy_name,current_instance_id,current_integrity))

		# for every key request, policy name and instance all = policy name
		if(current_policy_name == policy_name and current_instance_id == policy_name):
			device = node.getElementsByTagName("device")[0]
			current_device_id = device.getAttribute("id")
			if(current_device_id == device_id):
				if(current_integrity == "Passed"):
					return 1
				else:
					return 0


	return 0


def deletePolicy(policy_name):

	print "in policy_test_lib deletePolicy"
	print time.ctime()


	# parse policies to get the policy ID
	result = policy_api.getPolicies()

	dom_result = parseString(result)
	if(not dom_result):
		return 0

	security_group = dom_result.getElementsByTagName("securityGroup")
	for node in security_group:
		current_policy_name = node.getAttribute("name")
		current_policy_id = node.getAttribute("id")

		if(current_policy_name == policy_name):
			break
		
	try:
		if(current_policy_id <> ""):
			result = policy_api.deletePolicy(current_policy_id)

			print "out policy_test_lib deletePolicy"
			print time.ctime()


			if(result):
				return 1
			else:
				return 0
		else:
			return 0

	except NameError:
		return 0


def generate_instance_template(instance_template_path, **input):
	f = open(instance_template_path, "w")
	instance_template = """<?xml version="1.0" encoding="utf-8"?>\r\n"""

	if("location" in input):
		instance_template += """<instance placement="%s">\r\n""" % (input["location"])
	else:
		instance_template += """<instance>\r\n"""

	if("os" in input or "arch" in input or "ports" in input):
		instance_template += """<metaList>\r\n"""

		if("os" in input):
			instance_template += """<meta key="c9a_os">%s</meta>""" % (input["os"])

		if("arch" in input):
			instance_template += """<meta key="c9a_cpu_type">%s</meta>""" % (input["arch"])

		if("ports" in input):
			instance_template += """<meta key="c9a_net_svc_ports">%s</meta>""" % (input["ports"])

		instance_template += """</metaList>\r\n"""

	instance_template += """</instance>\r\n"""
	f.write(instance_template)


def generate_icm_template(icm_template_path, **input):
	f = open(icm_template_path, "w")
	icm_template = """<security_products>\r\n"""

	if("ossec" in input):
		icm_template += """<security_product id="b3784c5b-894a-439e-8013-cfdea5781128" version="1.0">
	<vendor>
		OSSEC
	</vendor>
	<product_name>
		OSSEC
	</product_name>
	<product_family>
		Cloud Security
	</product_family>
	<product_version>
		%s
	</product_version>
	<summary>
		OSSEC installation NOT FOUND!
	</summary>
	</security_product>
""" % (input["ossec"])

	if("osce" in input):
		icm_template += """<security_product id="dabd1a57-aeb7-4b12-9b5f-6081ba81687e" version="1" >
		<vendor>$L10N_COMPANY_NAME$</vendor>
		<product_name>$L10N_PRD_OSCE_NAME$</product_name>
		<product_family>$L10N_PRD_OSCE_FAMILY$</product_family>
		<product_version>%s</product_version>
		<summary>$L10N_PRD_OSCE_DESC$</summary>
	</security_product>""" % (input["osce"])

	if("splx" in input):
		icm_template += """<security_product id="dabd1a57-aeb7-4b12-9b5f-6081ba81687e" version="1" >
	<vendor>
		$L10N_COMPANY_NAME$
	</vendor>
	<product_name>
		$L10N_PRD_SPLX_NAME$
	</product_name>
	<product_family>
		$L10N_PRD_SPLX_FAMILY$
	</product_family>
	<product_version>
		%s
	</product_version>
	<summary>
		$L10N_PRD_SPLX_DESC$
	</summary>
	</security_product>""" % (input["splx"])

	if("ds" in input):
		icm_template += """<security_product id="dabd1a57-aeb7-4b12-9b5f-6081ba81687e" version="1" >
		<vendor>$L10N_COMPANY_NAME$</vendor>
		<product_name>$L10N_PRD_DSA_NAME$</product_name>
		<product_family>$L10N_PRD_DSA_FAMILY$</product_family> 	
		<product_version>%s</product_version>
		<summary>$L10N_PRD_DSA_DESC$</summary>
	</security_product>""" % (input["ds"])

	if("vs_engine" in input or "vs_pattern" in input):
		vs_engine = ""
		vs_pattern = ""
		
		if("vs_engine" in input):
			vs_engine = input["vs_engine"]
			#print "vs_engine:%s" % vs_engine

		if("vs_pattern" in input):
			vs_pattern = input["vs_pattern"]
			#print "vs_pattern:%s" % vs_pattern
		
		icm_template += """<security_product id="dabd1a57-aeb7-4b12-9b5f-6081ba81687e" version="1.0" >
    <vendor>
      $L10N_COMPANY_NAME$
    </vendor>
    <product_name>
      $L10N_PRD_OSCE_NAME$
    </product_name>
    <product_family>
      $L10N_PRD_OSCE_FAMILY$
    </product_family>
    <product_version>
      10.0
    </product_version>
    <summary>
      $L10N_PRD_OSCE_DESC$
    </summary>
    <product_updates>
      <module name="VSAPI">
        <description> $L10N_COMP_AV_DESC$ </description>
        <sub_module name="$L10N_AV_PTN_C_NAME$" file="lpt$vpn" version="%s">
          <description> $L10N_AV_PTN_C_DESC$ </description>
        </sub_module>
        <sub_module name="$L10N_AV_PTN_S_NAME$" file="icrc$oth" version="0.000.00">
          <description> $L10N_AV_PTN_S_DESC$ </description>
        </sub_module>
        <sub_module name="$L10N_AV_ENG_NAME$" file="vsapi" version="%s">
          <description> $L10N_AV_ENG_DESC$ </description>
        </sub_module>
      </module>
    </product_updates>
</security_product>""" % (vs_pattern, vs_engine)

	icm_template += "</security_products>"
	f.write(icm_template)
	

def launch_instance(image_id, instance_id, steps_path, instance_template_path="", icm_template_path=""):
	f = open(steps_path, "w")
	steps = "CreateSession\r\n CreateInstance "

	steps += " -i %s " % (image_id)

	if(instance_template_path <> ""):
		steps += " -t %s " % (instance_template_path)

	if(icm_template_path <> ""):
		steps += " -r %s " % (icm_template_path)

	steps += " %s \r\n EndSession\r\n" % (instance_id)
	f.write(steps)


def get_device_msuid(device_id):
	result = policy_api.getDevices()
	#print result
	#f = open("c:\\test-return.xml", "w")
	#f.write(result)
	
	dom_result = parseString(result)
	device_list = dom_result.getElementsByTagName("deviceList")[0]
	devices = device_list.getElementsByTagName("device")
	
	for node in devices:
		current_device_id = node.getAttribute("id")
		current_device_msuid = node.getAttribute("msUID")

		if(current_device_id == device_id):
			return current_device_msuid
			
	return ""

def get_device(device_msuid):
	result = policy_api.getDevice(device_msuid)
	return result

def update_device(device_msuid, device_data):
	result = policy_api.updateDevice(device_msuid, device_data)
	return result

def encrypt_device(device_msuid, device_data):
	result = policy_api.encryptDevice(device_msuid, device_data)
	return result


def testFunction():
	print policy_api.getPolicies()


	
if __name__ == '__main__':
	testFunction()