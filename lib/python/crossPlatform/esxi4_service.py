import os
import subprocess
import logging
from crossPlatform.errorCode import ErrorautoServerMain as errASM


def funcRevertESXi4(strHostName, strEsxiServer, strUser, strPassword, strSnapshotName):
    """
    revert ESXi VM through  command
    @param strHostName: ESXI VM Client Name on ESXi Server
    @param strEsxiServer: ESXi Server IP
    @param strUser: ESXi Server Login account
    @param strPassword: ESXi Server Login password
    @param strSnapshotName: snapshot Name on ESXi Client which would like to revert
    @return:
        True : means revert ESXi VM Client OK
        False :revert ESXi VM Client Failed , please check error log

    """

    strEsxi4Template = '''$vmserver="%s"
$vmuser= "%s"
$vmpassword="%s"
connect-VIServer -server $vmserver -user $vmuser -password $vmpassword
set-vm $Args[0] -Confirm:$false -snapshot (get-snapshot -vm $Args[0] -name $Args[1])
disconnect-VIServer -Confirm:$false
    '''
    strFileName = "revert.ps1"
    strEsxi4Cmd = str(strEsxi4Template % (strEsxiServer, strUser, strPassword))
    #print strPassword
    f = open(strFileName, 'w')
    f.write(strEsxi4Cmd)
    f.close()

    strCurrPath = os.getcwd()
    strRevertScriptPath = os.path.sep.join([strCurrPath, strFileName])
    strRevertScriptPath += r' '
    strRevertCmd = r'C:\WINDOWS\system32\windowspowershell\v1.0\powershell.exe -psc "C:\Program Files\VMware\Infrastructure\vSphere PowerCLI\vim.psc1" -c ' + strRevertScriptPath + strHostName + r" " + strSnapshotName
    print strRevertCmd
    #os.system(strRevertCmd)
     # execute command and record the message to stdout after Revert execute
    p = subprocess.Popen(strRevertCmd, shell=False, stdout=subprocess.PIPE)
    (stdout, stderr) = p.communicate()
    #set 'PoweredOn' keyword to judge the revert success or not
    if 'PoweredOn' in stdout:
        revertStatus = errASM.SUCCESS
        logging.info(str("Revert ESXi VM Success! [EsxiServer] : %s , [Client VM Host Name]: %s , [Snapshot Name]: %s , [Error Message]: %s " % (strEsxiServer, strHostName, strSnapshotName, stdout)))
    else:
        revertStatus = errASM.FAIL
        logging.error(str("Revert ESXi VM Fail! [EsxiServer] : %s , [Client VM Host Name]: %s , [Snapshot Name]: %s , [Error Message]: %s " % (strEsxiServer, strHostName, strSnapshotName, stdout)))

    return revertStatus

if __name__ == '__main__':
    funcRevertESXi4(
        'winxp_sp3_en', '10.204.211.1', "root", '12345678', 'tmstaf')
