import os
import time
import logging
import subprocess
import sys


def windows_partition_disk(temp_folder, disk_number, disk_type, partition_type, drive_letter):

    """
    select disk %s
    attribute disk clear readonly noerr
    online disk noerr
    convert dynamic noerr
    create volume simple
    assign letter=%s
    """

    # sleep for windows detect the new disk
    time.sleep(60)

    partition_script = """select disk %s \r\n""" % (disk_number)
    partition_script += """clean \r\n"""

    windows_info = sys.getwindowsversion()
    windows_version = windows_info[0]

    """
    2003=5
    2008=6
    """
    
    if windows_version > 5:
        partition_script += """attribute disk clear readonly noerr \r\nonline disk noerr \r\n"""

    if disk_type == "dynamic":
        partition_script += """convert dynamic noerr \r\n create volume %s \r\n""" % (partition_type)
    elif disk_type == "basic":
        partition_script += """create partition %s \r\n""" % (partition_type)
        
    partition_script += """assign letter=%s""" % (drive_letter)
    logging.info("partition script:" + partition_script)

    partition_script_path = temp_folder + "partition_script.txt"
    f = open(partition_script_path , "w")
    f.write(partition_script)
    f.close()

    command = """diskpart /s %s""" % (partition_script_path)
    logging.info("partition command:" + command)
    return_code = subprocess.call(command, shell=True)
    logging.info("return code:%s" % str(return_code))

    return return_code


def windows_format_partition(drive_letter, file_system):
    command = """ echo Y | format %s: /q /fs:%s """ % (drive_letter, file_system)
    logging.info("format command:" + command)
    return_code = subprocess.call(command, shell=True)
    logging.info("return code:%s" % str(return_code))

    return return_code

def linux_partprobe():
    command = """partprobe """
    return_code = subprocess.call(command, shell=True)
    logging.info("return code:%s" % str(return_code))
    return return_code

def linux_partition_disk(partition_type, partition_number, partition_size, device_name, retry=60):

    # (echo n; echo p; echo 1; echo ; echo ; echo w) | fdisk /dev/sdb
    # n=create patition
    # p=primary
    # 1=first partition
    # echo=default start
    # echo=default end
    # w=write to partition table

    #command = """(echo c; echo u; echo n; echo %s; echo %s; echo ; echo %s; echo w) | fdisk %s """ % (partition_type, partition_number, partition_size, device_name)
    command = """(echo u; echo n; echo %s; echo %s; echo ; echo %s; echo w) | fdisk %s """ % (partition_type, partition_number, partition_size, device_name)
    logging.info("partition command:" + command)
    return_code = subprocess.call(command, shell=True)
    logging.info("return code:%s" % str(return_code))
    count = 0
    while return_code != 0 and count < retry:
        return_code = subprocess.call(command, shell=True)
        logging.info("return code:%s" % str(return_code))
        count += 1
        time.sleep(10)

    return return_code

def linux_format_partition(device_name, file_system):
    import platform
    import re
    current_platform = platform.platform()
    m = re.search(r"redhat-5.", current_platform)

    # it's centos or rhel 5, does not support ext4, so format as ext3
    if m and file_system == "ext4":
        command = """ mkfs -t %s %s """ % ("ext3", device_name)
    else:
        command = """ mkfs -t %s %s """ % (file_system, device_name)
        
    logging.info("format command:" + command)
    return_code = subprocess.call(command, shell=True)
    logging.info("return code:%s" % str(return_code))
    return return_code

	
def linux_mount_partition(partition_path, mount_path):
    if not os.path.exists(mount_path):
        os.makedirs(mount_path)

    command = """ mount %s %s """ % (partition_path, mount_path)
    logging.info("mount command:" + command)
    return_code = subprocess.call(command, shell=True)
    logging.info("return code:%s" % str(return_code))

    return return_code


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')
