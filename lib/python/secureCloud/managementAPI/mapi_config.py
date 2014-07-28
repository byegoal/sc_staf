import logging
import platform


log_level = logging.DEBUG

broker_api_work_path = "c:\\mapi_temp\\"
os_type = platform.system()
if os_type == "Windows":
    broker_api_config_path = "C:\\STAF\\lib\\python\\secureCloud\\managementAPI\\sc_config.ini"
else:
    broker_api_config_path = "/usr/local/STAF/lib/python/secureCloud/managementAPI/sc_config.ini"

mapi_lib_IS_LOGGING = True
mapi_lib_LOG_TO_FILE = True

if os_type == "Windows":
    mapi_lib_XML_LOG_PATH = "C:\\STAF\\lib\\python\\chef\\result\\"
else:
    mapi_lib_XML_LOG_PATH = "/usr/local/STAF/lib/python/chef/result/"
mapi_lib_LOG_PATH = ""
mapi_lib_IS_SHOW = True



simulator_work_path = "c:\\mapi_temp\\"
simulator_clear_log = False
simulator_path = "AgentCmd.exe "

account_lib_path = "secureCloud.managementAPI.account_user_RAT"
administration_lib_path = "secureCloud.managementAPI.administration_RAT"
inventory_lib_path = "secureCloud.managementAPI.inventory_RAT"
instance_lib_path = "secureCloud.managementAPI.instance_RAT"
policy_lib_path = "secureCloud.managementAPI.policy_RAT"
log_lib_path = "secureCloud.managementAPI.log_RAT"
notify_lib_path = "secureCloud.managementAPI.notify_RAT"
report_lib_path = "secureCloud.managementAPI.report_RAT"
status_lib_path = "secureCloud.managementAPI.status_RAT"
license_lib_path = "secureCloud.managementAPI.license_RAT"

policy_test_case_path = "secureCloud.managementAPI.policy_test_case"
inventory_test_case_path = "secureCloud.managementAPI.inventory_test_case"
instance_test_case_path = "secureCloud.managementAPI.instance_test_case"
account_test_case_path = "secureCloud.managementAPI.account_user_test_case"

rule_mapping ={"Device Access Type":"5d14057d-3277-4ab9-9d3e-e808acbb9c65",
              "Device Mount Point":"c91f0521-a6cc-4e78-bb37-4a41dc378d3c",
               "Key Request Date":"1338779b-2683-474b-a9a7-298176564a6f",
               "Request Source IP Address":"cc0e1bfb-c670-44d1-8b83-f44d351d5285",
               "Request Source IPv6 Address":"d6f008eb-a11b-4cb6-8cb0-63c056d27009",
               "Instance First Seen":"4b4390c1-af4e-4c37-9ad0-24b26be2366d",
               "Instance User Data":"e541d7c1-b681-4221-a2c0-68bfd87debaa",
               "Instance Location":"b1ad7471-cb8b-4a78-bb56-efcb235ef1ba",
               "OSSEC Version":"9c36a9d2-ff26-47c4-8cfa-180630c97efb",
               "Trend Micro softwares":"6fbc0f33-d430-4a46-9b03-1dbb172c6509",
               "Trend Micro Virus Scan Engine":"297d4d3b-c269-43d9-ad9e-6fef86fdfe5c",
               "Trend Micro Virus Scan Pattern":"ed30599c-13c3-4fb3-ac30-2a38c0b5e45c",
               "Guest OS Type":"e3e68188-b5b2-4e31-bcce-c4cb43d46a55",
               "Guest OS Architecture":"b2ee4872-631b-4f57-aaff-e222cfadf588",
               "Network Services":"0f938a58-cd0a-4dc0-b0ec-034fff98ec1a",
               "Deep Security Status":"964ed53f-dd7c-43c6-aec5-b64df1474ff3",
               "Deep Security Anti-Malware Status":"cfd65596-9071-4fd6-a7c5-da368d1bf3d8",
               "Deep Security Web Reputation Status":"9637d366-95e5-4dcf-ac0a-703439aec8e9",
               "Deep Security Firewall Status":"eaeadd52-f0a9-4f16-a293-647ef2ccd10e",
               "Deep Security DPI Status":"c63d23e3-d00f-4ea9-a932-00086c3cb5a1",
               "Deep Security Integrity Monitoring Status":"b64c389e-8cd9-401a-a149-28bf95154fd1",
               "Deep Security Log Inspection Status":"de6017a8-e3a1-4a42-93bd-6aa7e783a765"}

TimeZone_mapping ={
                    "Hawaiian Standard Time":"Hawaiian Standard Time",
                    "Singapore Standard Time":"Singapore Standard Time",
                    "Venezuela Standard Time":"Venezuela Standard Time",
                    "Ekaterinburg Standard Time":"Ekaterinburg Standard Time",
                    "Central Standard Time (Mexico)":"Central Standard Time (Mexico)",
                    "Mid-Atlantic Standard Time":"Mid-Atlantic Standard Time",
                    "GMT Standard Time":"GMT Standard Time",
                    "Pacific SA Standard Time":"Pacific SA Standard Time",
                    "Tokyo Standard Time":"Tokyo Standard Time",
                    "Jordan Standard Time":"Jordan Standard Time",
                    "US Eastern Standard Time":"US Eastern Standard Time",
                    "Middle East Standard Time":"Middle East Standard Time",
                    "Central America Standard Time":"Central America Standard Time",
                    "E. Australia Standard Time":"E. Australia Standard Time",
                    "New Zealand Standard Time":"New Zealand Standard Time",
                    "Dateline Standard Time":"Dateline Standard Time",
                    "Iran Standard Time":"Iran Standard Time",
                    "West Asia Standard Time":"West Asia Standard Time",
                    "Eastern Standard Time":"Eastern Standard Time",
                    "Sri Lanka Standard Time":"Sri Lanka Standard Time",
                    "AUS Central Standard Time":"AUS Central Standard Time",
                    "Yakutsk Standard Time":"Yakutsk Standard Time",
                    "Myanmar Standard Time":"Myanmar Standard Time",
                    "Afghanistan Standard Time":"Afghanistan Standard Time",
                    "Vladivostok Standard Time":"Vladivostok Standard Time",
                    "W. Australia Standard Time":"W. Australia Standard Time",
                    "Cape Verde Standard Time":"Cape Verde Standard Time",
                    "China Standard Time":"China Standard Time",
                    "Central Pacific Standard Time":"Central Pacific Standard Time",
                    "Greenland Standard Time":"Greenland Standard Time",
                    "Romance Standard Time":"Romance Standard Time",
                    "Central European Standard Time":"Central European Standard Time",
                    "Pacific Standard Time (Mexico)":"Pacific Standard Time (Mexico)",
                    "Canada Central Standard Time":"Canada Central Standard Time",
                    "US Mountain Standard Time":"US Mountain Standard Time",
                    "Korea Standard Time":"Korea Standard Time",
                    "Azerbaijan Standard Time":"Azerbaijan Standard Time",
                    "Newfoundland Standard Time":"Newfoundland Standard Time",
                    "Egypt Standard Time":"Egypt Standard Time",
                    "SA Pacific Standard Time":"SA Pacific Standard Time",
                    "Taipei Standard Time":"Taipei Standard Time",
                    "Mountain Standard Time":"Mountain Standard Time",
                    "Bangladesh Standard Time":"Bangladesh Standard Time",
                    "Pacific Standard Time":"Pacific Standard Time",
                    "Russian Standard Time":"Russian Standard Time",
                    "Nepal Standard Time":"Nepal Standard Time",
                    "Ulaanbaatar Standard Time":"Ulaanbaatar Standard Time",
                    "Mountain Standard Time (Mexico)":"Mountain Standard Time (Mexico)",
                    "Morocco Standard Time":"Morocco Standard Time",
                    "Israel Standard Time":"Israel Standard Time",
                    "Central Standard Time":"Central Standard Time",
                    "E. Africa Standard Time":"E. Africa Standard Time",
                    "Alaskan Standard Time":"Alaskan Standard Time",
                    "Tasmania Standard Time":"Tasmania Standard Time",
                    "Greenwich Standard Time":"Greenwich Standard Time",
                    "Montevideo Standard Time":"Montevideo Standard Time",
                    "SA Western Standard Time":"SA Western Standard Time",
                    "North Asia Standard Time":"North Asia Standard Time",
                    "Arabic Standard Time":"Arabic Standard Time",
                    "Arab Standard Time":"Arab Standard Time",
                    "AUS Eastern Standard Time":"AUS Eastern Standard Time",
                    "W. Central Africa Standard Time":"W. Central Africa Standard Time",
                    "N. Central Asia Standard Time":"N. Central Asia Standard Time",
                    "FLE Standard Time":"FLE Standard Time",
                    "Cen. Australia Standard Time":"Cen. Australia Standard Time",
                    "GTB Standard Time":"GTB Standard Time",
                    "E. Europe Standard Time":"E. Europe Standard Time",
                    "South Africa Standard Time":"South Africa Standard Time",
                    "Samoa Standard Time":"Samoa Standard Time",
                    "SE Asia Standard Time":"SE Asia Standard Time",
                    "Caucasus Standard Time":"Caucasus Standard Time",
                    "E. South America Standard Time":"E. South America Standard Time",
                    "Argentina Standard Time":"Argentina Standard Time",
                    "Azores Standard Time":"Azores Standard Time",
                    "Central Europe Standard Time":"Central Europe Standard Time",
                    "W. Europe Standard Time":"W. Europe Standard Time",
                    "West Pacific Standard Time":"West Pacific Standard Time",
                    "Arabian Standard Time":"Arabian Standard Time",
                    "Mauritius Standard Time":"Mauritius Standard Time",
                    "Namibia Standard Time":"Namibia Standard Time",
                    "Pakistan Standard Time":"Pakistan Standard Time",
                    "India Standard Time":"India Standard Time",
                    "Central Asia Standard Time":"Central Asia Standard Time",
                    "Georgian Standard Time":"Georgian Standard Time",
                    "Atlantic Standard Time":"Atlantic Standard Time",
                    "Fiji Standard Time":"Fiji Standard Time",
                    "Armenian Standard Time":"Armenian Standard Time"

                    }
