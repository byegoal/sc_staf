import time
import sys
import random
import string
import shutil
import glob
import getopt
from xml.dom.minidom import parse, parseString
import logging
import getopt
import subprocess
import cgi


#SPECIAL_CHARS = re.escape("""(~!@#$%^&*()_+=-`][}{":';?><,./)""")
SPECIAL_CHARS = cgi.escape("""(~!@#$%^&*()_+=-`][}{":';?><,./)\|""")
MAX_INT = "2147483647"
MAX_INT_PLUS_1 = "2147483648"

def getText(node):
	#print "node type:"+str(node.nodeType)
	#print "node name:"+str(node.nodeName)
	#print "has child nodes:"+str(node.hasChildNodes())

	rc = ""

	if node.nodeType == node.ELEMENT_NODE:
		print 'Element name: %s' % node.nodeName
		print "has child nodes:"+str(node.hasChildNodes())
		print "has attributes:"+str(node.hasAttributes())

		if node.hasChildNodes():
			nodelist = node.childNodes
			for node in nodelist:
				print "current_nodetype:" + str(node.nodeType)
				if node.nodeType == node.TEXT_NODE:
					print "it's text node"
					rc = rc + node.data
				else:
					print "not text node, node type is:"
					print node.nodeType

				#print "element node is:" + str(node.ELEMENT_NODE)

				#for (name, value) in node.attributes.items():
					#print '    Attr -- Name: %s  Value: %s' % (name, value)

	elif node.hasChildNodes():
		nodelist = node.childNodes
		for node in nodelist:
			print "current_nodetype:" + node.nodeType
			if node.nodeType == node.TEXT_NODE:
				rc = rc + node.data

			#print "element node is:" + str(node.ELEMENT_NODE)


	return rc

"""
def do_remote_SQL(sql_command):

result = self.addTest(ExternalProgram(pstool_path),["\\\\172.18.0.39", "-u", "administrator", "-p", "P@ssw0rd@123", "-d", "C:\deep_security\ds_script2.bat"])

sqlcmd -E -S ' & $db_server & ' -d "' & $db_name & '" -i "' & $sql & '" >> "' & $build_extract_folder & '\db.log"')
"""








def get_time(time_format, given_time=None):

    if time_format == 1:
        ISOTIMEFORMAT="%Y-%m-%d %H:%M:%S"
    elif time_format == 2:
        ISOTIMEFORMAT="%Y-%m-%d-%H-%M-%S"

    if given_time:
        return time.strftime(ISOTIMEFORMAT, time.localtime(given_time))
    else:
        start_time = time.time()
        #print "start time:" + time.strftime(ISOTIMEFORMAT, time.localtime(start_time))
        return time.strftime(ISOTIMEFORMAT, time.localtime(start_time))


def call_cmd(command, log_file, action):

    start_time = time.time()
    log_file.write("START - " + action + " : " + get_time(1, start_time) + "\r\n")

    proc = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout_value, stderr_value = proc.communicate()

    #if has_error:
    if stderr_value:
        print stderr_value
        log_file.write(stderr_value + "\r\n")

    if stdout_value:
        print stdout_value
        log_file.write(stdout_value + "\r\n")
     
    end_time = time.time()
    spent_time = end_time - start_time

    log_file.write("End - " + action + " : " + get_time(1, end_time) + "\r\n")
    log_file.write("Time Taken:" + str(spent_time) + "\r\n")


def get_random(num_digits):
    return string.join(random.sample(['a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t','u','v','w','x','y','z','1','2','3','4','5','6','7','8','9'], num_digits)).replace(" ","")

def random_str(size=6, chars=string.letters + string.digits):
	return ''.join(random.choice(chars) for x in range(size))

if __name__ == '__main__':

	print id_generator(1000)
