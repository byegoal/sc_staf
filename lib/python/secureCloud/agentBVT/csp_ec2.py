
import boto.ec2
import time, os, sys
from pprint import pprint
import logging
from ConfigParser import SafeConfigParser

def add_staf_lib():
	staf_lib_path = "\\".join(os.path.dirname(__file__).split("\\")[:-2])
	pystaf_path = r"c:\staf\bin"
	sys.path.insert(0, pystaf_path)

	if staf_lib_path not in sys.path:
		sys.path.insert(0, staf_lib_path)
		print "Add staf lib path %s into sys.path" % staf_lib_path

add_staf_lib()

from secureCloud.agentBVT.staf import wait_ready
from ConfigParser import SafeConfigParser

logging.basicConfig(filename="csp_ec2.log", level=logging.INFO)

def get_os_env():
	logging.info(os.environ)

def read_conf_product_ini():
	config = SafeConfigParser()
	#TODO: fix hardcode

def get_current_spot_price():
	pass

def ec2_pricing(conn, instance_type, image_id):
	print "DEBUG: conn in ec2_pricing: %s " % conn
	image_info = conn.get_image(image_id)

	##TODO: support other regions
	if image_info.region.name == "ap-southeast-1":
		if image_info.platform == None:
			price = {'t1.micro':'0.02', 'm1.small':'0.085', 'm1.medium':'0.17', 'm1.large':'0.34', 'm1.xlarge':'0.68'}

		elif image_info.platform == "windows":
			price = {'t1.micro':'0.02','m1.small':'0.115', 'm1.medium':'0.23', 'm1.large':'0.46', 'm1.xlarge':'0.92'}

		result = price[instance_type]
		print "price query for %s %s: %s" % (image_info.region.name, instance_type, price)
		return result

	else:
		return None

def get_ec2_conn(region, aws_access_key_id, aws_secret_access_key):
	try:
		conn = boto.ec2.connect_to_region(region, aws_access_key_id=aws_access_key_id, aws_secret_access_key=aws_secret_access_key)
		print "MYLOG: created conn is: %s" % conn

	except Exception, e:
		print "boto create connection fail: %s" % e

	return conn

def run_instance(conn, image_id, key_name, security_groups, instance_type, sctm_env_name, strInstanceInfoPath, spot=True):
	#Lauch spot instance
	if spot == True:
		price = ec2_pricing(conn, instance_type, image_id)

		spot_request = conn.request_spot_instances(
			price = price,
			image_id = image_id,
			key_name = key_name,
			security_groups = [security_groups],
			instance_type = instance_type)

		print "spot_request_id: %s" % spot_request[0].id

		i = 0
		last_state = ""
		while not spot_request[0].state == "active":
			if i == 0:
				print "wait for request to be fullfiled"

			if last_state != spot_request[0].state:
				print "spot request state: %s" % spot_request[0].state
			i = i+1
			sys.stdout.write(".")
			time.sleep(5)
			last_state = spot_request[0].state
			spot_request = conn.get_all_spot_instance_requests([spot_request[0].id])
			if spot_request[0].state == "cancelled":
				print "request cancelled."
				exit()

		print "\n"
		print "spot request actived! instance_id: %s" % spot_request[0].instance_id

		try:
			#protect instance_id not found
			conn.create_tags([spot_request[0].instance_id], dict({'Name':sctm_env_name}))
		except Exception, e:
			logging.debug("create tag for instance fail: %s" % e)
			retry_limit = 10
			count = 0
			while count < retry_limit:
				logging.debug("create tag for instance_id: %s fail, wait loop %s/%s" % (spot_request[0].instance_id, count, retry_limit))
				time.sleep(5)
				conn.create_tags([spot_request[0].instance_id], dict({'Name':sctm_env_name}))
				count = count + 1

		instance_info = wait_for_instance_running(conn, spot_request[0].instance_id)
		instance_info['ec2_id'] = spot_request[0].instance_id

		wait_ready(instance_info['ip'], intTimes=6)	#sleep 5sec per retry staf ping
		"""
		Save info to TS_TMP\ec2_instance_info.ini as:
			[InstanceInfo]
			SCTM_ENV_NAME: ip, availbility_zone
		"""
		val = "%s, %s, %s" % (instance_info['ip'], instance_info['az'], instance_info['ec2_id'])
		update_config(strInstanceInfoPath, sctm_env_name, val)

	return instance_info

def wait_for_instance_running(conn, instance_id):
	reservation = conn.get_all_instances([instance_id])
	instance = reservation[0].instances

	i = 0
	last_state = ""
	while not instance[0]._state.name == "running":
		if i == 0:
			print "wait for instance state running"
		if last_state != instance[0]._state.name:
			print "current state: %s" % instance[0]._state
		last_state = instance[0]._state.name
		i = i+1
		sys.stdout.write(".")
		time.sleep(5)
		instance[0].update()

	print "\n"
	status_check = dict({
		'instance_status':conn.get_all_instance_status([instance_id])[0].instance_status.status,
		'system_status'  :conn.get_all_instance_status([instance_id])[0].system_status.status
		})
	#print status_check

	i = 0
	while not (status_check['instance_status'] == "ok" and status_check['system_status'] == "ok"):
		if i == 0:
			print "wait for instance status check result"
		i = i+1
		sys.stdout.write(".")
		time.sleep(5)
		status_check['instance_status'] = conn.get_all_instance_status([instance_id])[0].instance_status.status
		status_check['system_status'] = conn.get_all_instance_status([instance_id])[0].system_status.status

	print "\n"
	print "instance ip: %s" % instance[0].ip_address
	print "instance AZ: %s" % instance[0]._placement
	return dict({'id': instance_id, 'ip': instance[0].ip_address, 'az': instance[0]._placement.zone, 'conn': conn})

def add_disk(conn, size, az):
	print "MYLOG: conn is: %s" % conn
	vol = conn.create_volume(size, az)
	#logging.info("volume created: %s") % volume_id
	return vol.id

def create_tag(conn, lstVolumeId, tag):
	conn.create_tags(lstVolumeId, dict({'Name':tag}))
	return 0

def attach_volume(conn, lstVolumeId, instance_id):
	# maximum 26-3 disks for each instance
	disk_char_list = list('defghijklmnopqrstuvwxyz'[::-1])

	for vol in lstVolumeId:
		c = disk_char_list.pop()
		print "dev_node for volume is: /dev/sd%s" % c
		print "attach vol %s to instance %s" % (vol, instance_id)
		try:
			res = conn.attach_volume(vol, instance_id, "/dev/sd%s" % c)
			logging.info("attach disk %s to %s success" % (vol, instance_id))
		except Exception, e:

			logging.error("attach disk %s to %s failed" % (vol, instance_id))
			return 1

	#TODO: Add attached vol into instance_into.txt


def update_config(strInstanceInfoPath, key, value):
	"""
	Save instance information(ip, zone, instance-id) to file.
	TODO: if we can save the information in testStep object, we can avoid saving information to file.
	"""
	config = SafeConfigParser(allow_no_value=True)
	if not os.path.exists(strInstanceInfoPath):
		print "create file"
		f = open(strInstanceInfoPath, "w")
		f.write("[InstanceInfo]\n")
		f.close()

	config.read(strInstanceInfoPath)
	if not config.has_section("InstanceInfo"):
		config.add_section("InstanceInfo")
	config.set("InstanceInfo", key, value)

	with open(strInstanceInfoPath, "r+") as f:
		config.write(f)

def get_instance_info(strInstanceInfoPath, sctm_env_name):
	# ip, az, ec2_id, vol_list
	config = SafeConfigParser(allow_no_value=True)
	config.read(strInstanceInfoPath)
	info = config.get("InstanceInfo", sctm_env_name).split(",")
	instance_info = dict({'ip': info[0].strip(), 'az':info[1].strip(), 'ec2_id':info[2].strip()})

	if len(info) == 4:
		instance_info['vol_list'] = info[3].strip()

	return instance_info

def check_running_instance(conn, strInstanceInfoPath, sctm_env_name):
	config = SafeConfigParser(allow_no_value=True)
	if os.path.exists(strInstanceInfoPath):
		config.read(strInstanceInfoPath)
		if config.has_section("InstanceInfo"):
			if config.has_option("InstanceInfo", sctm_env_name):
				info = config.get("InstanceInfo", sctm_env_name)
				logging.info("MYLOG: instance info read from ini is: %s" % info)
				if info != "":
					instance_id = info.split(",")[2].strip()
					logging.info("MYLOG: reuse instance id is: %s" % type(instance_id))

					#TODO: check if instance exist in response or not
					all_res = conn.get_all_instances()
					instances = [i for r in all_res for i in r.instances]
					instance_id_list = []
					for i in instances:
						if i._state.name == "running":
							instance_id_list.append(i.id)
					logging.info("MYLOG: instance_id_list is: %s" % instance_id_list)
					if instance_id in instance_id_list:
						logging.info("MYLOG: instance_id: %s is in instance_id_list" % instance_id )
						return True
	else:
		return False

if __name__ == "__main__":

	aws_key_id = "AKIAJC3LSM7FROQ5WZBQ"
	aws_access_key  = "Q6ljwBecM4hnZs+ZjfuAYiXPkgdlwBxeoTrrOjC0"
	region = "ap-southeast-1"
	#image_id = "ami-ff7133ad" #ebs win
	#image_id = "ami-d2225c80" #amazone linux S3
	#image_id = "ami-4df28d1f" # ubuntu
	image_id = "ami-7c4a0b2e" #windows2008-sp2-x64-agentBVT
	key_name = "default-AWS-AP-Singapore"
	security_groups = ["default"]

	conn = boto.ec2.connect_to_region(region, aws_access_key_id=aws_key_id, aws_secret_access_key=aws_access_key)
	print conn
	try:
		#sid = run_instance(conn, image_id, key_name, security_groups, instance_type="t1.micro", spot=True)
		#print "sid: %s" % sid
		#wait_for_instance_running(conn, "i-c5228292")
		all_ins = conn.get_all_instances()
		print all_ins

	except Exception, e:
		print e
		print "something wrong..."
		#conn.cancel_spot_instance_requests([spot_request_id])