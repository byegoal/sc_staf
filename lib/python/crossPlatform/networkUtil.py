import logging
import subprocess
import os
import sys
import socket
import processUtil


def mountNetworkDriveForWin(strDeviceName, strUncPath, strUserName, strPassword):
    if not strPassword:
        strPassword = '""'
    strMountCommand = 'net use %s %s %s' % (
        strDeviceName, strUncPath, strPassword)
    if strUserName:
        strMountCommand += " /u:%s" % strUserName
    objProcess = subprocess.Popen(strMountCommand, stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    strStdout = objProcess.stdout.read()
    intReturnCode = objProcess.wait()
    if intReturnCode != 0:
        if not strStdout or strStdout.find(' 85') < 0:
            logging.error("mount %s on %s failed. ErrorCode: %s",
                          strUncPath, strDeviceName, intReturnCode)
            logging.error("stdout:\n%s", strStdout)
            return 2
    strStdout = os.popen('net use %s' % strDeviceName).read()
    if strStdout.find(strUncPath) < 0:
        logging.error('mount %s on %s failed. %s already mounted:\n%s', strUncPath, strDeviceName, strDeviceName, strStdout.strip())
        return 2
    try:
        os.listdir(strDeviceName + "/")
    except:
        logging.error("mount %s on %s failed. %s", strUncPath,
                      strDeviceName, sys.exc_info()[1])
        logging.error('mount command: "%s"', strMountCommand)
        unmountNetworkDrive(strDeviceName)
        return 2
    logging.info("mount %s on %s successfully.", strUncPath, strDeviceName)
    return 0


def unmountNetworkDriveForWin(strDeviceName):
    strUnmountCommand = "net use %s /delete /yes" % strDeviceName
    objProcess = subprocess.Popen(strUnmountCommand, stdin=subprocess.PIPE,
                                  stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    strStdout = objProcess.stdout.read()
    intReturnCode = objProcess.wait()
    if intReturnCode == 0:
        logging.info("unmount %s successfully.", strDeviceName)
        return 0
    else:
        logging.error("unmount %s failed. ErrorCode: %s",
                      strDeviceName, intReturnCode)
        logging.error("stdout:\n%s", strStdout)
        return 2


def mountNetworkDriveForLinux(strMountPoint, strUncPath, strUserName, strPassword="", strReadOnly="0"):
    '''
        @param strMountPoint: Ex. /Volumes/samples
        @param strUncPath: Ex. //10.2.202.91/samples
        @param strUserName: Ex. administrator
        @param strPassword: Ex. trend123
        @param strReadOnly: 0 is disable read-only and 1 is enable read-only function
        @return: 0 means success; otherwise return 2.
    '''

    if not os.path.exists(strMountPoint):
        os.makedirs(strMountPoint)
    else:
        #//WORKGROUP;ADMINISTRATOR@10.2.203.200/MPM on /Volumes/build (nodev, nosuid, read-only, mounted by mpm)
        objP = processUtil.TmProcess(['mount', '-t', 'smbfs'])
        lstBuf = objP.readStdout().split('\n')
        for s in lstBuf:
            if s.find(strMountPoint) >= 0 and s.find(strUncPath[2:]) >= 0:
                logging.info('"%s" already mount on "%s".',
                             strUncPath, strMountPoint)
                return 0

    strUncPath = strUncPath.strip('//')
    if strReadOnly == "1":
        strCommandType = "mount -r -t smbfs //"
    else:
        strCommandType = "mount -t smbfs //"

    if not strPassword:
        strMountCommand = strCommandType + "%s@%s %s" % (
            strUserName, strUncPath, strMountPoint)
    else:
        strMountCommand = strCommandType + "%s:%s@%s %s" % (
            strUserName, strPassword, strUncPath, strMountPoint)
    logging.debug(strMountCommand)
    objProcess = processUtil.TmProcess(strMountCommand, shell=True)
    strStdout = objProcess.readStdout()
    intReturnCode = objProcess.wait()
    if intReturnCode != 0:
        logging.error("mount %s failed. ErrorCode: %s",
                      strMountPoint, intReturnCode)
        logging.error("stdout:\n%s", strStdout)
        return 2

    try:
        os.listdir(strMountPoint)
    except:
        logging.error("mount %s on %s failed. %s", strUncPath,
                      strMountPoint, sys.exc_info()[1])
        logging.error('mount command: "%s"', strMountCommand)
        unmountNetworkDrive(strMountPoint)
        return 2
    logging.info("mount %s on %s successfully.", strUncPath, strMountPoint)

    return 0


def unmountNetworkDriveForLinux(strMountPoint):
    strUnmountCommand = "umount " + strMountPoint
    objProcess = processUtil.TmProcess(strUnmountCommand, shell=True)
    strStdout = objProcess.readStdout()
    intReturnCode = objProcess.wait()
    if intReturnCode == 0:
        logging.info("unmount %s successfully.", strMountPoint)
        return 0
    else:
        logging.error("unmount %s failed. ErrorCode: %s",
                      strMountPoint, intReturnCode)
        logging.error("stdout:\n%s", strStdout)
        return 2
    return 0

if os.name == 'nt':
    mountNetworkDrive = mountNetworkDriveForWin
    unmountNetworkDrive = unmountNetworkDriveForWin
elif os.name == 'posix':
    #Todo: implement samba mount for linux platform
    mountNetworkDrive = mountNetworkDriveForLinux
    unmountNetworkDrive = unmountNetworkDriveForLinux


def getIpList():
    try:
        hostname, aliaslist, ipaddrlist = socket.gethostbyname_ex(
            socket.gethostname())
        return ipaddrlist
    except:
        return ['']


def setNetworkHost(strHostName, strIP):
    '''
    update windows' host file
    @require:
    Windows
    @param strHostName: Ex. localhost
    @param strIP: Ex. 127.0.0.1
    @return:
        0 - success
        1 - fail
    '''
    #get WINDOWS\system32\drivers\etc folder and combine host file path
    import fileinput
    strHostFile = os.path.join(
        os.getenv("Windir"), "system32\drivers\etc\hosts")
    if os.path.exists(strHostFile) == False:
        logging.error("Can't find hosts file: %s", strHostFile)
        return 1

    boolExist = 0
    for line in fileinput.input(strHostFile, inplace=1):
        stripline = line.rstrip("\n").split(" ")[-1]
        if strHostName == stripline:
            #host is alreay existing, update it
            print strIP + "  " + strHostName
            boolExist = 1
        else:
            print line
    fileinput.close()

    if boolExist == 0:
        #host does not exist, add it
        f = open(strHostFile, "a")
        f.write(strIP + "  " + strHostName)
        f.close()

    return 0


def main():
    logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    strUsage = '\nUsage: networkUtil.py mount MountPoint UncPath UserName [Password] [ReadOnly Flag]  \nUsage: networkUtil.py unmount MountPoint'

    args = sys.argv[1:]
    if len(args) == 0:
        logging.info(strUsage)
        return
    if args[0] == "mount":
        if len(args) == 4:
            intResult = mountNetworkDrive(args[1], args[2], args[3])
            logging.debug("return code: %s", intResult)
        elif len(args) == 5:
            intResult = mountNetworkDrive(args[1], args[2], args[3], args[4])
            logging.debug("return code: %s", intResult)
        elif len(args) == 6:
            intResult = mountNetworkDrive(
                args[1], args[2], args[3], args[4], args[5])
            logging.debug("return code: %s", intResult)
        else:
            logging.info(strUsage)
    elif args[0] == "unmount":
        if len(args) == 2:
            intResult = unmountNetworkDrive(args[1])
            logging.debug("return code: %s", intResult)
        else:
            logging.info(strUsage)
    else:
        logging.info(strUsage)

if __name__ == '__main__':
    #main()
    setNetworkHost("123.com", "10.10.10.4")
