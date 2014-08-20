#!/usr/bin/python
# -*- coding: utf-8 -*-

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

DEFAULT_FS_WIN = 'ntfs'
DEFAULT_MOUNT_POINT_WIN = 'E:'

DEFAULT_FS_LINUX = 'ext3'
DEFAULT_MOUNT_POINT_LINUX = '/secure_disk1'

# use for checking if device is encrypted (do not modify)
MA_SIGNATURE = '\xef\xbe\xed\xfe'
MA_SIG_OFFSET = 32
MA_SIG_LENGTH = 4
SECTOR_SIZE = 512

def getstatusoutput(cmd):
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    output = proc.communicate()[0]

    return output

class command_helper(object):
    def exec_cmd(self, command, shell=True):
        
        try:
            logging.info('Executing command: %s' %command)
            ret_code = subprocess.call(command, shell=shell)
        except Exception, ex:            
            logging.error('execute command exception: %s' %str(ex))
            ret_code = -1
        return ret_code

    def get_sc_root(self):
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

class Device(object):
    def __init__(self, name):
        self.disk_name = name

    def _is_da_sector(self, sector):
        try:
            return sector[MA_SIG_OFFSET : MA_SIG_OFFSET+MA_SIG_LENGTH] == MA_SIGNATURE
        except:
            return False

    def is_encrypted(self):
        disk_name = self.disk_name
        if os.name == 'nt':
            disk_name = '\\\\.\\PHYSICALDRIVE' + str(disk_name)

        if os.name != 'nt' and not os.path.exists(disk_name):
            return

        disk = open(disk_name, 'rb')
        is_encrypted = False
        try:
            content = disk.read(SECTOR_SIZE)
            if self._is_da_sector(content):
                logging.debug('%s has MA signature on sector 0. Might be an encrypted disk by 1.2/2.0/3.0 Linux SC Agent.' % disk_name)
                is_encrypted = True

            content = disk.read(SECTOR_SIZE)
            if self._is_da_sector(content):
                logging.debug('%s has MA signature on sector 1. Might be an encrypted disk by 3.5 Linux SC Agent or any version of Windows SC Agent.' % disk_name)
                is_encrypted = True
        except:
            logging.error('Fail to read disk %s' % disk_name)
        
        return is_encrypted

    def _has_partition(self):
        raise NotImplementedError('has partition')
    def _has_filesystem(self):
        raise NotImplementedError('has filesystem')
    def is_boot_device(self):
        raise NotImplementedError('is_boot_device')
    def is_raw_device(self):
        if self.is_encrypted():
            logging.warning('the device %s has been encrypted by SecureCloud' %self.disk_name)
            return False
        if self._has_partition():
            logging.warning('the device %s has partition table inside' %self.disk_name)
            return False
        if self._has_filesystem():
            logging.warning('the device %s has filesystem, may have data in it' %self.disk_name)
            return False        
        return True

class DeviceWin(Device):
    def __init__(self, name):
        super(DeviceWin, self).__init__(name)
        self._partition_count = 0

    def _has_partition(self):
        partition_script = "select disk %s \r\n" % self.disk_name
        partition_script += "list partition \r\n"

        logging.debug('[DeviceWin - _has_partition] partition_script = \n%s' %partition_script)

        tmp_path = tempfile.mkdtemp()
        partition_script_path = os.path.join(tmp_path, "partition_script.txt")
        logging.info('[DeviceWin - _has_partition] Use partition script at %s' %partition_script_path)
        # create the empty file
        f = open(partition_script_path, 'w')
        f.write(partition_script)
        f.close()

        cmd = 'diskpart /s "%s"' %(partition_script_path)
        output = getstatusoutput(cmd).split('\n')
        has_partition = False
        partition_count = -1
        for line in output:
            line = line.lstrip()
            if line.startswith('Partition'):
                has_partition = True
                partition_count += 1

        self._partition_count = partition_count
        os.unlink(partition_script_path)
        shutil.rmtree(tmp_path)
        return has_partition

    def _has_filesystem(self):
        # Windows cannot assign a filesystem to whole device without partition
        return False

    def is_boot_device(self):
        partition_script = "select disk %s\r\n" %self.disk_name
        partition_script += "list partition \r\n"

        logging.debug('[DeviceWin - is_boot_device] partition_script = \n%s' %partition_script)

        tmp_path = tempfile.mkdtemp()
        partition_script_path = os.path.join(tmp_path, "partition_script.txt")
        logging.info('[DeviceWin - is_boot_device] Use partition script at %s' %partition_script_path)
        # create the empty file
        f = open(partition_script_path, 'w')
        f.write(partition_script)
        f.close()

        cmd = 'diskpart /s "%s"' %(partition_script_path)
        output = getstatusoutput(cmd).split('\n')
        partition_list = list()
        for line in output:
            line = line.lstrip()
            if line.startswith('Partition'):
                partition_info = line.split()
                try:
                    partition_list.append(str(int(partition_info[1])))
                except ValueError:
                    # not integer (Partition ###)
                    pass

        os.unlink(partition_script_path)

        partition_script = "select disk %s\r\n" %self.disk_name
        partition_script += "list partition \r\n"
        for partition in partition_list:
            partition_script += "select partition %s\r\n" %partition
            partition_script += "detail partition \r\n"

        logging.debug('[DeviceWin - is_boot_device] partition_script = \n%s' %partition_script)

        partition_script_path = os.path.join(tmp_path, "partition_script.txt")
        logging.info('[DeviceWin - is_boot_device] Use partition script at %s' %partition_script_path)
        # create the empty file
        f = open(partition_script_path, 'w')
        f.write(partition_script)
        f.close()

        cmd = 'diskpart /s "%s"' %(partition_script_path)
        output = getstatusoutput(cmd).split('\n')
        active_flag = False
        for line in output:
            line = line.lstrip()
            if line.startswith('Active'):
                if line.split()[1] == 'Yes':
                    active_flag = True

        os.unlink(partition_script_path)
        shutil.rmtree(tmp_path)

        return active_flag

class DeviceLinux(Device):
    def _has_partition(self):
        disk_info = getstatusoutput('fdisk -l %s' % self.disk_name).split('\n')
        for line in disk_info:
            if line.startswith('/dev/'):
                return True
        return False

    def _has_filesystem(self):
        fs_type_out = getstatusoutput('blkid %s' % self.disk_name).split()
        for fs_line in fs_type_out:
            if fs_line.startswith('TYPE='):
                return True
        return False

    def is_boot_device(self):
        disk_info = getstatusoutput('fdisk -l %s' % self.disk_name).split('\n')
        for line in disk_info:
            if line.startswith('/dev/'):
                if line.split()[1] == '*':
                    return True
        return False

class DeviceManagerBase(command_helper):
    def __init__(self):
        self.device_list = list()
        self._new_devices_list = list()
        self.get_local_devices()

    def find_new_devices(self):
        if not self._new_devices_list:
            device_list = self.get_local_devices()
            device_list = self._remove_discovered_and_save(device_list)
            self._new_devices_list = device_list

        return self._new_devices_list

    def _remove_discovered_and_save(self, device_list):
        new_device_list = list()
        device_file_path = os.path.join(self.get_sc_root(), 'device.json')
        # read device file as a list
        try:
            f = open(device_file_path, "r")
            fcontent = f.read()
            f.close()
            discovered_disks = json.loads(fcontent)
        except IOError:
            # file is not exist
            discovered_disks = list()
            pass

        p_list = list()
        # remove discovered disks
        for device in device_list:
            p_list.append(device.disk_name)
            if not device.disk_name in discovered_disks:
                new_device_list.append(device)

        # save the new list
        f = open(device_file_path, "w")
        json.dump(p_list, f)
        f.close()

        return new_device_list

    def get_device_by_name(self, disk_name):
        for device in self.device_list:
            if device.disk_name == disk_name:
                return device

        logging.error('[DeviceManagerWin - get_device_by_name] cannot find device by name %s' %disk_name)
        return None

    def get_local_devices(self):
        raise NotImplementedError('get local devices')

    def find_next_mp(self, mp_base):
        raise NotImplementedError('find next mp')

class DeviceManagerWin(DeviceManagerBase):
    def _get_mount_point_list(self):
        mount_point_list = list()
        output = getstatusoutput('wmic logicaldisk get caption').split('\n')
        for line in output:
            line.strip()
            if line.startswith('Caption'):
                continue
            if ':' in line:
                mount_point_list.append(line.split(':')[0] + ':')
        
        return mount_point_list

    def get_local_devices(self):
        partition_script = "rescan \r\n"
        partition_script += "list disk \r\n"

        logging.debug('[DeviceManagerWin - get_local_devices] partition_script = \n%s' %partition_script)

        tmp_path = tempfile.mkdtemp()
        partition_script_path = os.path.join(tmp_path, "partition_script.txt")
        logging.info('[DeviceManagerWin - get_local_devices] Use partition script at %s' %partition_script_path)
        # create the empty file
        f = open(partition_script_path, 'w')
        f.write(partition_script)
        f.close()

        cmd = 'diskpart /s "%s"' %(partition_script_path)
        output = getstatusoutput(cmd).split('\n')
        device_list = list()
        for line in output:
            line = line.lstrip()
            if line.startswith('Disk'):
                disk_info = line.split()
                try:
                    dev = DeviceWin(str(int(disk_info[1])))
                    device_list.append(dev)
                except ValueError:
                    # not integer (DISK #)
                    pass

        os.unlink(partition_script_path)
        shutil.rmtree(tmp_path)

        self.device_list = device_list
        return device_list

    def _get_next_mp(self, mp):
        CHAR_Z = 90 #ASCII
        next_mp = ord(mp) + 1
        if next_mp <= CHAR_Z:
            return chr(next_mp)
        else:
            logging.error('Ran out of mountpoint')
            raise Exception('Ran out of mountpoint')

    def find_next_mp(self, mp_base):
        mount_point_list = self._get_mount_point_list()

        logging.debug('[DeviceManagerWin - _find_next_mount_point] %s' %str(mount_point_list))
        # find the index to be increased
        mount_point_base = mp_base
        if mount_point_base[-1] == '\\': #E:\
            mount_point_base = mount_point_base[:-1] #E:
        if mount_point_base[-1] == ':': #E:
            mount_point_base = mount_point_base[:-1] #E

        last_bit = mount_point_base #last_bit = E
        
        # check if the mount point is already used
        mount_point = last_bit + ":"
        while mount_point in mount_point_list:
            last_bit = self._get_next_mp(last_bit)
            mount_point = last_bit + ":"

        logging.debug('[DeviceManagerWin - _find_next_mount_point] next available is : %s' %mount_point)
        return mount_point

class DeviceManagerLinux(DeviceManagerBase):
    def get_local_devices(self):
        output = getstatusoutput('ls /dev/sd*[a-z] /dev/vd*[a-z0-9] /dev/xvd*[a-z0-9]')
        tmp_device_list = output.split()

        # check if cd/cdrw/dvd/dvdrw devices has been incorrectly found
        output = getstatusoutput('ls /dev/cd* /dev/dvd*').split()
        cd_dev_list = list()
        for cd_dev in output:
            real_name = getstatusoutput('readlink -e %s' % cd_dev)
            if 'sr' not in real_name and real_name not in cd_dev_list:
                cd_dev_list.append(real_name)
                for dev in tmp_device_list:
                    if dev == real_name:
                        logging.debug('Device %s is cd/dvd device. Skip.' % dev)
                        tmp_device_list.remove(dev)
                        break

        device_list = list()
        for dev in tmp_device_list:
            real_name = getstatusoutput('readlink -e %s' % dev)
            if real_name.strip() == dev.strip():
                tmp_dev = DeviceLinux(dev)
                print(tmp_dev)
                device_list.append(tmp_dev)

        self.device_list = device_list
        return device_list

    def find_next_mp(self, mp_base):
        mount_point_list = list()
        output = getstatusoutput('mount | awk \'{ print $3 }\'')
        logging.debug('Used mountpoint:\n %s' %output)
        mount_point_list = output.split('\n')

        # find the index to be increased
        mount_point_base = mp_base
        if mount_point_base[-1] == '/': #/secure_disk1/
            mount_point_base = mount_point_base[:-1] #/secure_disk1
        
        last_bit = mount_point_base[-1] #last_bit = 1
        
        try:
            idx = int(last_bit)
            mount_point_base = mount_point_base[:-1]
        except ValueError: #is not integer
            idx = 1
        
        # check if the mount point is already used
        mount_point = mount_point_base + str(idx)
        while mount_point in mount_point_list:
            idx = idx + 1
            mount_point = mount_point_base + str(idx)

        return mount_point

class DeviceManagerFactory:
    __instance = None
    @staticmethod
    def getDeviceManager():
        if not DeviceManagerFactory.__instance:
            os_name = platform.system()
            if os_name == 'Windows':
                DeviceManagerFactory.__instance = DeviceManagerWin()
            elif os_name == 'Linux':
                DeviceManagerFactory.__instance = DeviceManagerLinux()
        return DeviceManagerFactory.__instance

def main(options):
    retval = 0

    if options.list_devices:
        device_mgr = DeviceManagerFactory.getDeviceManager()

        # save the new device list
        device_file_path = os.path.join(device_mgr.get_sc_root(), 'new_device.txt')
        f = open(device_file_path, "w")

        device_str = str()
        idx = 0
        for device in device_mgr.find_new_devices():
            if idx != 0:
                device_str += ', '

            device_str += device.disk_name
            idx += 1

        f.write(device_str)
        f.close()

        print device_str

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
    action_group.add_option('-l', '--list-devices', action='store_true', dest='list_devices',
                    default=False,
                    help='Set this to get new devices')

    parser.add_option_group(action_group)

    (options, args) = parser.parse_args(argv)
    
    return options


if __name__ == "__main__":
    logger = logging.basicConfig(filename='script.log',
                                 level=logging.DEBUG,
                                 format='%(asctime)s %(levelname)s : %(message)s -- @(%(lineno)d)'
                                 )
    logging.critical('*** START SCRIPT ***')
    __retval__ = 0

    if os.name == 'posix':
        if os.geteuid() != 0:
            print 'this script must be run as root'
            __retval__ = 1

    if __retval__ == 0:
        __options__ = _handle_options(sys.argv[1:])
        __retval__ = main(__options__)

    logging.critical('*** EXIT WITH (%s) ***' %str(__retval__))
    sys.exit(__retval__)
