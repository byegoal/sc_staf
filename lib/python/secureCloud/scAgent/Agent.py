import sys
import os
import platform
import subprocess
import json
import logging
import ConfigParser
import tempfile
import shutil
from optparse import OptionParser, OptionGroup


def get_sc_root():
        #read registry for windows
        if platform.system() == "Windows":
            if 'CLOUD_ROOT' in os.environ:
                root_dir = os.environ['CLOUD_ROOT']

            if root_dir is None:
                import _winreg
                try:
                    c9_key = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,
                                    "SOFTWARE\\TrendMicro\\SecureCloud\\Agent")
                    root_dir, reg_type = _winreg.QueryValueEx(c9_key,
                                    "InstallDirectory")
                    _winreg.CloseKey(c9_key)
                except:
                    root_dir = os.getcwd()
            if root_dir[len(root_dir)-1] == '/' or \
                            root_dir[len(root_dir)-1] == '\\':
                root_dir = root_dir[:len(root_dir)-1]

            return root_dir
        else:
            return '/var/lib/securecloud/'

            
def get_scconfig_path():
    sc_path = get_sc_root()
    if platform.system() == "Windows":
        scconfig_path = sc_path+'scconfig.exe'
    else:
        scconfig_path = sc_path+'scconfig.sh'

def getGenScprovConfig(device_no,device_name,encrypt_type,partition_format_list,msg):
            os_name = platform.system()
            if os_name == 'Windows':
                msg =gen_scprov_Win(device_no,device_name,encrypt_type,partition_format_list,msg)
            elif os_name == 'Linux':
                msg =gen_scprov_Linux(device_no,device_name,encrypt_type,partition_format_list,msg)
                
            return msg
    
def gen_scprov_Win(device_no,device_name,encrypt_type,partition_format_list,msg):
        device_name=('harddisk%s' %device_name)
        msg+='DEVICE_NAME=harddisk%s\n' %device_name
        return 1
def gen_scprov_Linux(device_no,device_name,encrypt_type,partition_format_list,msg):
        
        if encrypt_type=='erase':
            msg+='[%s]\n' %device_no #DeviceNo
            msg+='DEVICE_NAME=%s\n' %device_name
            msg+='EXISTING_DATA=%s\n' %encrypt_type
            msg+='MOUNT_POINT=/Auto/d0%s\n'% device_no[6:]
            if partition_format_list[0]=='': #set default format
             partition_format = 'ext3'
            else:
             partition_format = partition_format_list[0]  #if two partition format in a disk, use first one
            msg+='FILESYSTEM=%s\n' %partition_format
        else:
            msg+='[%s]\n' %device_no #DeviceNo
            msg+='DEVICE_NAME=%s\n' %device_name
            msg+='EXISTING_DATA=%s\n' %encrypt_type
        return msg
            