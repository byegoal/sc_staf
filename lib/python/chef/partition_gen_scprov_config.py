
import logging
import logging.handlers
import optparse
import os
import sys
import time
import re
import cPickle
import shutil
import platform
from cookielib import logger
from optparse import OptionParser, OptionGroup

MODULE_PATH = os.path.dirname(__file__) or os.getcwd()
TMSTAF_PID_FILE = os.path.join(MODULE_PATH, 'tmstaf.pid')


def addTmstafLibPath():
    sys.path.insert(0, os.path.dirname(MODULE_PATH))


def addStafLibPath():
    #Todo: we should not hardcode this path! 2009-10-14 camge
    if os.name == 'nt':
        sys.path.insert(0, r'C:\staf\bin')
    else:
        sys.path.insert(0, r'/usr/local/STAF/bin')

addStafLibPath()
addTmstafLibPath()


import tmstaf.processUtil
import secureCloud.agentBVT.testingClient
import secureCloud.agentBVT.util
import secureCloud.agentBVT.partition_format_tool
import secureCloud.scAgent.Agent
from tmstaf.testwareConfig import TestwareConfig
from tmstaf.productSetting import ProductSetting
from tmstaf.testRunner import BaseTestRunner
from tmstaf.util import getException
import threading
VERSION = 'v2.1.0'

import secureCloud.config.result_config
import secureCloud.scAgent.file
log_path = secureCloud.config.result_config.result_path
chefLogger = secureCloud.config.result_config.chefLogger
stafLogger = secureCloud.config.result_config.stafLogger
errorLogger = secureCloud.config.result_config.errorLogger
class TmstafMain:
    strVersion = VERSION
    strResumeDataFileName = 'resume.dat'
    strResumeDataFile = os.path.join(os.getcwd(), strResumeDataFileName)
    _dicLevel = {'critical': logging.CRITICAL,
                 'error': logging.ERROR,
                 'warning': logging.WARNING,
                 'info': logging.INFO,
                 'debug': logging.DEBUG}

    def __init__(self, intLogLevel=None):
        # set root logger's level to DEBUG
        self.resumed = False
        if intLogLevel:
            logging.getLogger().setLevel(intLogLevel)
        self.strCmdLine = ' '.join(sys.argv)

        

def main(options):
    retval = 0
    GLOBAL_SETTING = secureCloud.agentBVT.util.config("%s/product.ini" % MODULE_PATH)
    sc_path = secureCloud.scAgent.Agent.get_sc_root()
    partition_array = options.partition_array.split(';')
    #partition_array = "Device1,ext3|ext4".split(';')
    #device_str = "/dev/xvdi,/dev/xvdj"
    device_str=secureCloud.agentBVT.util.get_file_first_line(r'%s/new_device.txt'%sc_path)
    stafLogger.debug('New Devices:%s'%device_str)
    device_list = device_str.split(', ')
   
   
    config_file_name = os.path.join(sc_path, 'scprov.ini')
    config_msg =str()
    tmp_string =str()     
    idy = 0
    if device_list=="":
        errorLogger.error('NO new devices in new_device.txt')   
        retval==1
    else:            
     for device_name in device_list:
           if idy<len(partition_array):
               partition_list = partition_array[idy].split(',')
               # generate scprov.ini 
               device_no = partition_list[0]
               device_name = device_list[idy]
               encrypt_type = options.encrypt_type

               partition_format_list=[]
               partition_format_list=partition_list[1].split('.')
               config_msg= secureCloud.scAgent.Agent.getGenScprovConfig(device_no,device_name,encrypt_type,partition_format_list,config_msg)
               chefLogger.info(config_msg)
               secureCloud.agentBVT.util.gen_config_file(config_file_name,config_msg)
               if not partition_format_list[0] == '':
                   partition_number=0
                   for partition_format in partition_format_list:
                 #do partition
                     partition_return_code = secureCloud.agentBVT.partition_format_tool.linux_partition_disk('p',(partition_number+1),'+20M',device_name,0)             
                 #sync partition table
                     partprobe_return_code = secureCloud.agentBVT.partition_format_tool.linux_partprobe()
                     stafLogger.debug('partition number=%s, partprobe_return_code= %s'%(partition_number+1,partprobe_return_code))   
                     partition_number+= 1
                   format_number=0          
                   for partition_format in partition_format_list:
                       #sync partition table
                     partprobe_return_code = secureCloud.agentBVT.partition_format_tool.linux_partprobe()
                     stafLogger.debug('partition number=%s, partprobe_return_code= %s'%(format_number+1,partprobe_return_code)) 
                 #do format
                     partition_device_name = '%s%s'%(device_name,format_number+1)
                     if partition_format==None:
                        partition_format='ext3'
                     format_return_code = secureCloud.agentBVT.partition_format_tool.linux_format_partition(partition_device_name,partition_format)
                     stafLogger.debug('partition number=%s, format_return_code= %s'%(format_number+1,format_return_code))          
                     if not format_return_code==0:
                       retval = format_return_code
                       errorLogger.error('device format error, partition number=%s,return_code = %s'%(format_number+1,format_return_code))
                       return retval
                     partition_mount_point='/Auto/d0%s0%s'% (device_no[6:],str(format_number+1))
                 #do mount
                     mount_return_code = secureCloud.agentBVT.partition_format_tool.linux_mount_partition(partition_device_name,partition_mount_point)
                     if not mount_return_code==0:
                        retval = mount_return_code
                        errorLogger.error('device mount error, return_code = %s'%mount_return_code)
                        return retval 
                     format_number+= 1
           idy += 1             
    if retval==0:
        stafLogger.critical('pass: %s partition,format,mount and generate scprov.ini success'%device_str)
        stafLogger.debug('partition.ini file path: %s\n' % config_file_name)
        stafLogger.debug('scprov.ini---------\n%s' %config_msg)
    else:
        stafLogger.critical('FAIL: %s partition,format,mount and generate scprov.ini FAIL'%device_str )
        errorLogger.error('FAIL: %s partition,format,mount and generate scprov.ini FAIL'%device_str)
    secureCloud.scAgent.file.write_sctm_report(log_path,"Device partition,format,mount and Generate scprov.ini",retval)
    return retval

def _handle_options(argv):
    usage_win = 'activate.py [action [parameters]]'
    usage_linux = 'python activate.py [action [parameters]]'
    if os.name == "nt":
        usage = usage_win
    else:
        usage = usage_linux

    parser = OptionParser(usage=usage)

    action_group = OptionGroup(parser, "Actions", "")
    action_group.add_option('-f', '--partition-array', type='string', dest='partition_array',
                    default=False, metavar= 'device_array',
                    help='Device number,partition format to be encrypted (Device1,ext3.ext4;Device2,ext3;Device3,)')
    action_group.add_option('-t', '--encrypt-type', type='choice', dest='encrypt_type',
                    default=False, metavar= 'encrypt_type',choices=['erase', 'preserve'], 
                    help='Type to be encrypted (erase | preserve)')
    action_group.add_option('-p', '--gen-config-path', type='string', dest='gen_config_path',
                    default=False, metavar= 'gen_config_path' ,
                    help='path for gen scprov config file')
    parser.add_option_group(action_group)

    (options, args) = parser.parse_args(argv)
    
    return options

if __name__ == "__main__":  
    __retval__ = 0
    stafLogger.critical('*** START Partition,format,mount and generate scprov.ini ***\n') 
    if __retval__ == 0:
        __options__ = _handle_options(sys.argv[1:])
        __retval__ = main(__options__)
    stafLogger.critical('*** EXIT WITH (%s) ***\n' %str(__retval__))
    sys.exit(__retval__)
