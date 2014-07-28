import os
import logging
import crossPlatform.misc
import crossPlatform.winProcessUtil
import crossPlatform.callStafService as callStafService

if crossPlatform.misc.isWin64:
    VM_RUN_TOOL = os.path.join(
        r'C:\Program Files (x86)\VMware\VMware Workstation', 'vmrun.exe')
else:
    VM_RUN_TOOL = os.path.join(
        r'C:\Program Files\VMware\VMware Workstation', 'vmrun.exe')


def revertVmByStaf(strHostIp, strImagePath, strSnapshotName, intRetry=3):
    """
    Restore remote host's image
    """
    objStafService = callStafService.StafService()
    logging.info("Restore VM client")

    while intRetry > 0:
        #revert vm
        cmd = '-T ws revertToSnapshot \\\"' + strImagePath + \
            '\\\" \"' + strSnapshotName + '\"'
        cmd = 'START COMMAND ' + VM_RUN_TOOL + ' PARMS "' + cmd + \
            '" WAIT RETURNSTDOUT STDERRTOSTDOUT'
        logging.info("vm revert cmd:%s", cmd)
        ret = objStafService.callStafService(strHostIp, "PROCESS", cmd)
        if ret != 0:
            logging.error("revertVmByStaf revert fail, host=%s cmd=%s",
                          strHostIp, cmd)
            intRetry = intRetry - 1
            continue

        #resume vm
        logging.info("Power on VM client")
        cmd = '-T ws start \\\"' + strImagePath + '\\\"'
        cmd = 'START COMMAND ' + VM_RUN_TOOL + ' PARMS "' + cmd + \
            '" WAIT RETURNSTDOUT STDERRTOSTDOUT'
        logging.info("vm revert cmd:%s", cmd)
        ret = objStafService.callStafService(strHostIp, "PROCESS", cmd)
        if ret != 0:
            logging.error("revertVmByStaf resume fail, host=%s cmd=%s",
                          strHostIp, cmd)
            intRetry = intRetry - 1
            continue

        return 0
    #retry too much times
    return 1

if __name__ == '__main__':
    revertVmByStaf("local",
                   r"D:\\VM_IMAGE\\SP2\\Windows XP Professional.vmx", "clean")
