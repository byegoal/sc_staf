#!/usr/bin/env python
#***********************************************************************************#
# Created by => Alex Chnag                                                          #
#***********************************************************************************#
import socket, sys, os, platform, time, subprocess, re, datetime, getopt, logging
import urllib2, urllib, xml.dom.minidom, base64
from tomcrypt import rsa
from xml.dom.minidom import parseString

COMMENT_CHAR = '#'
OPTION_CHAR =  '='

def init_global_vaiable():    
    global certificate
    certificate = None
    global pubkey
    pubkey = None
    global s_token  
    s_token = None
    global retire_image_id
    retire_image_id = []
    global kms
    kms = []
    global err    
    err = None
    global updatetype
    updatetype = None
    
    
    par_result = None    
    par_result = parse_config('config.ini')
    if (par_result[0] == True):
        #logging.info('AFT : %s' %kms)
        return(True,kms)
    else:
        return(False,par_result[1])  
    
def parse_config(filename):    

    line = None
    key = None
    value = None
    xx = 0
    dd = 0

    try :
        f = open(filename)
    except IOError,err:
        logging.info('Read configure file error, message: %s' %err)
        return (False,err)

    for line in f:
        # First, remove comments:
        if not line.strip():
            continue

        if COMMENT_CHAR in line:
            line, comment = line.split(COMMENT_CHAR, 1)
            #logging.info('Line %d => %s' %(xx,line.strip()))
            #xx += 1
            continue
        if OPTION_CHAR in line:        
            key, value = line.split(OPTION_CHAR, 1)
            #logging.info("Line %d Parse confing => %s = %s" %(xx,key.strip(),value.strip()))        
            kms.insert(dd,value.replace('"','').strip())
            #xx += 1
            dd += 1
            line = None
            key = None
            value = None	

    f.close()
	#logging.info('BEF : %s' %kms)
    return(True,kms)

def getText(node):
    rc = ""
    if node.nodeType == node.ELEMENT_NODE:
       if node.hasChildNodes():
          nodelist = node.childNodes
          for node in nodelist:
              if node.nodeType == node.TEXT_NODE:
                  rc = rc + node.data
    elif node.hasChildNodes():
        nodelist = node.childNodes
        for node in nodelist:
            if node.nodeType == node.TEXT_NODE:
                rc = rc + node.data
    return rc

def chk_con(kms):
    #parse kms
    hostname = None
    port = None
    result = None
    ip = None
    ipaddr = None    
    hostname = re.search('https://(.*?):',kms[0],flags=0).group(1)
    logging.info('KMS FQDN : %s' %hostname)
    port = re.search('https://.*:(.*)/',kms[0],flags=0).group(1)
    logging.info ('KMS WebAPI Port : %s' %port)
    #DNS resolve
    try:
        socket.gethostbyname(hostname)
    except :
        logging.error('DNS resolve problem for this KMS server FQDN : %s' %hostname)
        print '!!! DNS resolve issue for FQDN : %s!!!' %hostname
        return (False)
    else :
        result = socket.gethostbyaddr(hostname)
        ip = result[2]        
        ipaddr = ip[0]
        logging.info('KMS IP address : %s' %ipaddr)
    #TCP connect
    socket.timeout(30)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((ipaddr,int(port)))        
    except Exception, e:
        logging.exception('TCP connection error with %s:%d. Exception type is %s' % (ipaddr, int(port), `e`))
        print 'TCP connection error with KMS server %s port %d. Error type %s'% (ipaddr, int(port), `e`)
        return (False)
    else :
        s.shutdown(1)
        s.close()
        return(True)

def get_hostname():
    host1 = socket.gethostname() #Hontname only
    host2 = socket.getfqdn(host1) #FQDN name
    logging.info("Hostname : %s" % host1)
    logging.info("FQDN     : %s" % host2)
    return (True)

def get_osinfo():
    osname1 = platform.platform(aliased=0,terse=0)
    osname2 = os.name   
    logging.info("Platform name    : %s" %osname1)    
    logging.info("OS name          : %s" %osname2)
    logging.info("Python version   : %s" %str(sys.version_info[:3]))
    if (platform.system() == 'Linux'):
        cmd = 'lsb_release -a'
        result = subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,close_fds=True).stdout
        while 1:
                info = result.readline()
                if not info :
                         break
                else :
                        if info != '\n':    
                            logging.info("%s" % info.strip())
        return (True)
    elif (platform.system() == "Windows"):
        return (True)
    else:
        logging.error('The target OS = %s does not support !!!' %platform.system())
        print 'OS not support yet'
    return (False)    

def get_policy_guid(kms,ut):
    auth_url = None
    rep = None
    xmldata = None
    security_list = None
    security_group = None
    tSecid = None
    _sid = None
    tPolicy_id = None
    tPolicy_href = None
    xx = 0    
    
    auth_url = kms[1]+"SecurityGroup/"
    rep = comm_request(kms,auth_url,None,"GET")
    if (rep[0]!= True):
        return (False,rep[1])
    xmldata = xml.dom.minidom.parseString(rep[1])
    security_list = xmldata.getElementsByTagName("securityGroupList")[0]
    security_group = security_list.getElementsByTagName("securityGroup")    
    #logging.info("Update Type : %s" % ut)
    if (ut == "Add"):
    #logging.info("Security ID : %s" % kms[7])
        _sid = kms[7]
    if (ut == "Remove"):
    #logging.info("Security ID : %s" % kms[8])
        _sid = kms[8]
    logging.info("Security ID : %s" % _sid)    
    for tSecid in security_group:
        tPolicy_name = tSecid.attributes["name"].value.strip()
        if (_sid != tPolicy_name):
            continue
        else :
            tPolicy_id = tSecid.attributes["id"].value.strip()
            tPolicy_href =  tSecid.attributes["href"].value.strip()
            kms.insert(11,tPolicy_id) # Add target poliy ID to KMS
            kms.insert(12,tPolicy_href) # Add WebAPI herf to KMS
            logging.info("Policy ID : %s" % tPolicy_id)
            logging.info("Policy link : %s" % tPolicy_href)
        xx += 1
       
    if (xx == 0):
        return(False)
    else :
        return(True)

   
def modify_security_policy(kms,tImage):
    auth_url = None
    rep = None    
    rep2 = None
    retire_policy_list = None
    req_xml = None
    retire_policy = None
    retire_image_list = None
    retire_images = None
    image = None
    current_image_id = None
    retire_images_pnode = None
    remove_image_cnode = None
    
    #Get extactly Policy data
    auth_url = kms[12]    
    rep = comm_request(kms,auth_url,None,"GET")
    if (rep[0]!= True):
        return (False,rep[1])
    #logging.debug('Dump_0 : %s' %rep[1])
    retire_policy_doc = xml.dom.minidom.parseString(rep[1]) #return document
    retire_policy = retire_policy_doc.getElementsByTagName("securityGroup")[0] #return list
    #print retire_policy_doc.toxml()   
    #is_existing_image = False    
    try :
	retire_image_list = retire_policy.getElementsByTagName("imageList")[0] #return list
    except Exception,err:
        logging.error("Node imageList not found, error message : %s" %err)
	return (False)		
	#print retire_policy.toxml() 	
    else : # Remove image dato directly
	retire_images = retire_policy.getElementsByTagName("image") # Get image	
	for image in retire_images:
	    current_image_id = image.attributes["id"].value.strip()
	    #logging.info("current_image_id:%s" % current_image_id)
	    if current_image_id == tImage:		
		retire_image_list.removeChild(image)    
    req_data = retire_policy.toxml() # return xml     
    #logging.info('After added imageList and image : %s' %req_data)
    rep2 = comm_request(kms,auth_url,req_data,"POST")
    if (rep2[0] == True):    
        return(True,rep2[1])
    else :
        return(False,rep2[1])

def main(argv):

    # check python version
    if (sys.version_info < (2,7,0)):
        print 'You need python version 2.7 or above to execute this script\n'
        return (False)

    logger = logging.basicConfig(filename='webapi.log',level=logging.DEBUG,format='%(asctime)s %(levelname)s : %(message)s -- @(%(lineno)d)')
    sver = "0.2"	
    try:
        options, args = getopt.getopt(sys.argv[1:],"hHvVt:",["para1="])
    except getopt.GetoptError:
        print 'webapi.py -t "vm1.singapore.gov,VM2,localhost"'
        sys.exit(2)        
    para1 = None
    targetvm = None
    cer = None
    token = None

    # process options        
    for opt, arg in options:
        if ((opt == '-h') or (opt == '-H')):
            print 'Usage for Activation on Windows : webapi.py -t "VM1,VM2,VM3"'               
            print '-t option, input the hostname that will remove from default policy to retire one'
            sys.exit()            
        if ((opt == '-v') or (opt == '-V')):                
            print 'Version:'+sver+' Author by: Trend Micro'                
            sys.exit()            
        elif opt in ("-t","--para1"):
            targetvm = arg
        else:
            return(False, "unhandled option")

    logging.info('****** Start Move VMs and Devices to Retire policy @ version %s ******' % sver)
    ini_ret = init_global_vaiable()
    if (ini_ret[0] != True):
        print "Faile to initial Global variable error message : %s" %ini_ret[1]
        return (False)

    t1 = datetime.datetime.now()	
    get_hostname()
    get_osinfo()             

    logging.info("==> Step 0: Start connection checking...")	

    config = ConfigParser.SafeConfigParser()
    DEFAULT_TEST_CONFIG_FILE = os.path.join(os.path.dirname(os.path.abspath(tests.__file__ )), "unit/test.cfg")
    config.read(DEFAULT_TEST_CONFIG_FILE)

    logging.info("<== Step 0: Complete connection checking...")
    logging.info("==> Step 1: Start Authentication query...")

    connection = SCConnectionFilter( config.get('connection', 'MS_HOST'),
                                    config.get('connection', 'MS_BROKER_NAME'), 
                                    config.get('connection', 'MS_BROKER_PASSPHASE'),
                                    result_path=self.result_path)
  
    logging.info("<== Step 2: Get Session token...")
    logging.info("==> Step 3: Start VM ID query...")	

    vm = connection.getVM(targetvm)
    if not vm:
        print "!!! No match VM found"
        return (False)

    logging.info("<== Step 3: Get VM ID information ...")
    logging.info("==> Step 4: Uplodate Security Policy...")
    updatetype = "Add" #Add target VM and Device to target Security Policy
    if (get_device_info(kms,tImage[1],updatetype) != True):         
        print "!!! Failed to add VMs or Devices into Security Policy"
        return (False)
    else :
        updatetype = "Remove" #Remove VM from default Policy
        if (get_device_info(kms,tImage[1],updatetype) != True):         
            print "!!! Failed to remove VMs from Default Security Policy"
            return (False)
        else :	    	
            logging.info("<== Step 4: Complete Security Polocy update...")

    t2 = datetime.datetime.now()
    logging.info("Total process time :%s" %str(t2-t1))
    logging.info('====== Move VMs and Devices to Retire policy ======')
    print 'Move to Retire policy successful'
    return (True)

if __name__ == '__main__':
    main(sys.argv[1:])  
