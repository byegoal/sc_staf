import os
import time
import logging
import subprocess
import secureCloud.agentBVT.staf

if os.path.exists(r"C:\Program Files (x86)"):
    BASE_COMMAND = """C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe -psc "C:\\Program Files (x86)\\VMware\\Infrastructure\\vSphere PowerCLI\\vim.psc1" """
else:
    BASE_COMMAND = """C:\\Windows\\System32\\WindowsPowerShell\\v1.0\\powershell.exe -psc "C:\\Program Files\\VMware\\Infrastructure\\vSphere PowerCLI\\vim.psc1" """


def deploy_vm(vcenter, user_name, user_pass, vm_name, vm_template_name, data_store, esx_host, vm_folder):

    #Connect-VIServer -Server 172.18.0.70 -User 'administrator' -Password 'SMTM@4704'
    #New-VM -Name 'danny_vsphere_api_test' -Template 'Win2008 R2 x64 test env ready' -Datastore 'Dell_1TB(QA-1)' -ResourcePool '172.18.0.16' -Location 'danny'
    #Start-VM -VM 'danny_vsphere_api_test'


    command = BASE_COMMAND + """ -command Connect-VIServer -Server '%s' -User '%s' -Password '%s' """ % (vcenter, user_name, user_pass)
    command += """ ; New-VM -Name '%s' -Template '%s' -Datastore '%s' -ResourcePool '%s' -Location '%s' """ % (vm_name, vm_template_name, data_store, esx_host, vm_folder)
    logging.info("Vsphere deploy command:" + command)

    return_code = subprocess.call(command, shell=True)
    logging.info("return code:%s" % str(return_code))

    return return_code


def revert_snapshot(vcenter, user_name, user_pass, vm_name, snapshot_name):
    """
    Set-VM -VM $vm -Snapshot $snapshot
    """

    command = BASE_COMMAND + """ -command Connect-VIServer -Server '%s' -User '%s' -Password '%s' """ % (vcenter, user_name, user_pass)
    command += """ ; Set-VM -VM %s -Snapshot %s -Confirm:$false """ % (vm_name, snapshot_name)
    return_code = subprocess.call(command, shell=True)
    logging.info("return code:%s" % str(return_code))

    return return_code


def power_on_vm(vcenter, user_name, user_pass, vm_name, vm_ip):
    """
    Start-VM -VM $vm
    """

    command = BASE_COMMAND + """ -command Connect-VIServer -Server '%s' -User '%s' -Password '%s' """ % (vcenter, user_name, user_pass)
    command += """ ; Start-VM -VM '%s' -Confirm:$false """ % (vm_name)
    return_code = subprocess.call(command, shell=True)
    logging.info("return code:%s" % str(return_code))

    logging.info("start to wait staf ...")
    secureCloud.agentBVT.staf.wait_ready(vm_ip, 10)

    return return_code


def add_disk(vcenter, user_name, user_pass, vm_name, disk_size):

    command = BASE_COMMAND + """ -command Connect-VIServer -Server '%s' -User '%s' -Password '%s' """ % (vcenter, user_name, user_pass)
    command += """ ; New-HardDisk -VM '%s' -CapacityGB %s -Persistence persistent """ % (vm_name, disk_size)
    return_code = subprocess.call(command, shell=True)
    logging.info("return code:%s" % str(return_code))
    time.sleep(3)

    return return_code


# def delete_disk(vcenter, user_name, user_pass, datastore, datastore_path):
def delete_disk(vcenter, user_name, user_pass, vm_name):
    command = BASE_COMMAND + """ -command Connect-VIServer -Server '%s' -User '%s' -Password '%s' """ % (vcenter, user_name, user_pass)
    command += """ ; "Get-Harddisk -vm '%s' | where {$_.Filename -match \\"_\d+\.vmdk\\"} | Remove-HardDisk -DeletePermanently -Confirm:$false" """ % (vm_name)
    logging.debug("Delete command:" + command)
    return_code = subprocess.call(command, shell=True)
    logging.info("return code:%s" % str(return_code))

    return return_code


def power_off_vm(vcenter, user_name, user_pass, vm_name):

    command = BASE_COMMAND + """ -command Connect-VIServer -Server '%s' -User '%s' -Password '%s' """ % (vcenter, user_name, user_pass)
    command += """ ; Stop-VM -VM '%s' -Confirm:$false """ % (vm_name)

    return_code = subprocess.call(command, shell=True)
    logging.info("return code:%s" % str(return_code))

    return return_code


def shutdown_guest(vcenter, user_name, user_pass, vm_name):
    """
    Shutdown-VMGuest -VM $vm
    """
    command = BASE_COMMAND + """ -command Connect-VIServer -Server '%s' -User '%s' -Password '%s' """ % (vcenter,
                                                                                                         user_name, user_pass)
    command += """ ; Shutdown-VMGuest -VM '%s' -Confirm:$false """ % (vm_name)

    return_code = subprocess.call(command, shell=True)
    logging.info("return code:%s" % str(return_code))

    return return_code

def reserve_all_guest_meory(vcenter, user_name, user_pass, vm_name):
    """
    """
    command = BASE_COMMAND + """ -command Connect-VIServer -Server '%s' -User '%s' -Password '%s' """ % (vcenter,
                                                                                                         user_name, user_pass)
    command += """ ; $spec = New-Object VMware.Vim.VirtualMachineConfigSpec; $spec.memoryReservationLockedToMax = $true; (Get-VM %s).ExtensionData.ReconfigVM_Task($spec) """ % (vm_name)

    logging.debug("reserve_all_quest_memory_command: %s" % command)
    return_code = subprocess.call(command, shell=True)
    logging.info("return code:%s" % str(return_code))

    return return_code

def delete_vm(vcenter, user_name, user_pass, vm_name):

    command = BASE_COMMAND + """ -command Connect-VIServer -Server '%s' -User '%s' -Password '%s' """ % (vcenter, user_name, user_pass)
    command += """ ; Remove-VM '%s' -DeletePermanently -RunAsync -Confirm:$false """ % (vm_name)

    return_code = subprocess.call(command, shell=True)
    logging.info("return code:%s" % str(return_code))

    return return_code


# if __name__ == '__main__':
    # logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(message)s')
