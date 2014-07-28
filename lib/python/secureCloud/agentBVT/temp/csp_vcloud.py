import os
import time
import logging
import subprocess
import secureCloud.agentBVT.staf

BASE_COMMAND = """C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe -psc "C:\\Program Files\\VMware\\Infrastructure\\vSphere PowerCLI\\vim.psc1" """

# with CI and snapshot support
BASE_COMMAND_VAPP = """C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe -psc "C:\\Program Files\\VMware\\Infrastructure\\vSphere PowerCLI\\vim.psc1" -c ". 'C:\\Program Files\\VMware\\Infrastructure\\vSphere PowerCLI\\Scripts\\Initialize-PowerCLIEnvironment.ps1' """


SNAPSHOT_MODULE_PATH = "c:\\temp\\vCloudSnapshots.psm1"

def revert_snapshot(vcloud_server, user_name, user_pass, org, civm_name, snapshot_module=SNAPSHOT_MODULE_PATH):
    """
    Import-Module c:\temp\vCloudSnapshots.psm1
    Get-CIVapp "danny_test" | Set-CISnapshot -Confirm:$false
    """
    
    command = BASE_COMMAND_VAPP + """ ; . Connect-CIServer -Server '%s' -User '%s' -Password '%s' -Org '%s' """ % (vcloud_server, user_name, user_pass, org)
    command += """ ; . Import-Module '%s' """ % (snapshot_module)
    command += """ ; . Get-CIVM '%s' | Set-CISnapshot -Confirm:$false """ % (civm_name)
    command += "\""
    logging.info("revert command:%s" % command)
    return_code = subprocess.call(command, shell=True)
    logging.info("return code:%s" % str(return_code))
    
    return return_code


def power_on_vapp(vcloud_server, user_name, user_pass, org, civm_name, vm_ip, retry=50):
    """
    Start-CIVApp "danny_test" -Confirm:$false
    """
    count = 0
    command = BASE_COMMAND_VAPP + """ ; . Connect-CIServer -Server '%s' -User '%s' -Password '%s' -Org '%s' """ % (vcloud_server, user_name, user_pass, org)
    command += """ ; . Start-CIVM '%s' -Confirm:$false """ % (civm_name)
    command += "\""
    logging.info("power-on vapp command:%s" % command)

    while count < retry:

        return_code = subprocess.call(command, shell=True)
        logging.info("start CIVM, try:%s, return code:%s" % (str(count), str(return_code)))

        if return_code == 0:
            break

        count += 1

    logging.info("start to wait staf ...")
    secureCloud.agentBVT.staf.wait_ready(vm_ip, 10)
    
    return return_code


def power_off_vapp(vcloud_server, user_name, user_pass, org, civm_name, retry=50):
    """
    Stop-CIVApp "danny_test" -Confirm:$false
    """

    count = 0
    command = BASE_COMMAND_VAPP + """ ; . Connect-CIServer -Server '%s' -User '%s' -Password '%s' -Org '%s' """ % (vcloud_server, user_name, user_pass, org)
    command += """ ; . Stop-CIVM '%s' -Confirm:$false """ % (civm_name)
    command += "\""
    logging.debug("power-off vapp command:" + command)

    while count < retry:

        return_code = subprocess.call(command, shell=True)
        logging.info("power-off CIVM, try:%s, return code:%s" % (str(count), str(return_code)))

        if return_code == 0:
            break

        count += 1

    return return_code


def add_disk(vcenter, user_name, user_pass, vm_name, disk_size):
    command = BASE_COMMAND + """ -command Connect-VIServer -Server '%s' -User '%s' -Password '%s' """ % (vcenter, user_name, user_pass)
    #command += """ ; New-HardDisk -VM '%s' -CapacityGB %s -Persistence persistent -StorageFormat Thin """ % (vm_name, disk_size)
    command += """ ; New-HardDisk -VM '%s' -CapacityGB %s -Persistence persistent """ % (vm_name, disk_size)
    return_code = subprocess.call(command, shell=True)
    logging.info("return code:%s" % str(return_code))
    time.sleep(3)

    return return_code


def delete_disk(vcenter, user_name, user_pass, vm_name):
    command = BASE_COMMAND + """ -command Connect-VIServer -Server '%s' -User '%s' -Password '%s' """ % (vcenter, user_name, user_pass)
    command += """ ; "Get-Harddisk -vm '%s' | where {$_.Filename -match \\"_\d+\.vmdk\\"} | Remove-HardDisk -DeletePermanently -Confirm:$false" """ % (vm_name)
    logging.debug("Delete command:" + command)
    return_code = subprocess.call(command, shell=True)
    logging.info("return code:%s" % str(return_code))

    return return_code

  

#if __name__ == '__main__':
    #logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')
