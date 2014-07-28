import time
import subprocess
import os
import sys
import shutil
import glob
import logging


class CrossPlatformException:
    pass


def copy_file_remote(strSrcPath, strDestPath, strUserName, strPassword, strImage, **option):
    ''' Copy file to or from remote machine through network drive
        [Input]
        strSrcPath - The path to the source folder
        strDestPath - The path to the destination folder
        strUserName - The username for login to remote machine
        strPassword - The password for login to remote machine
        strImage - The specific driver (Ex: C:, D:) for network construction
        option - remote = 'src' | 'dest'. Specify which one is the remote machine. Default is src.
        pathlist = A list contains paths. Paths could be directory. The path would be append to strSrcPath
        fileName = A string means specific file name.The name would be append to strSrcPath
        [Return]
        0 - Success
        -1 - Failed
    '''
    import networkUtil
    print '----copy_file_remote()----'
    # Unmount network drive
    #networkUtil.unmountNetworkDrive(strImage)

    if(None == strSrcPath or None == strDestPath):
        print '[copy_file_remote()][Error] Invalid source or destination path'
        raise CrossPlatformException(
            '[copy_file_remote]Invalid source or destination path')

    # Connect to network drive
    strRemoteUncPath = strSrcPath
    strSrcPath = strImage + os.path.sep
    if(0 != networkUtil.mountNetworkDrive(strImage, strRemoteUncPath, strUserName, strPassword)):
        print '[copy_file_remote()][Error] Fail on mount network drive'
        raise CrossPlatformException(
            '[copy_file_remote]Fail on mount network drive')

    # Copy file
    if not strDestPath.endswith(os.path.sep):
            strDestPath = strDestPath + os.path.sep
    print '[copy_file_remote()] Copy file from %s to %s' % (
        strSrcPath, strDestPath)
    shutil.copytree(strSrcPath, strDestPath)

    # Unmount network drive
    networkUtil.unmountNetworkDrive(strImage)
    return 0


def getLatestFolder(strPath):
    '''Get the latest folder name under the input path
       [Input]
       strPath - the specific path
       [Return]
       The folder name or None (No any folder)
       [Note]
       Support Windows, Linux
    '''
    print '----getLatestFolder()----'
    os.chdir(strPath)
    if os.name == "nt":
        files = os.popen(r"dir /ad /od /b *.*").read().splitlines()
    elif os.name == "posix":
        files = os.popen(r"ls -rtd ./*/").read().splitlines()
    else:
        files = os.popen(r"ls -rtd ./*/").read().splitlines()

    if 0 == len(files):
        print 'getLatestFolder() There is no directory'
        return None
    else:
        return files[-1]


def is64bit():
    '''
    This function will return 0 if the current system is 64-bit OS.
    '''
    import pywintypes

    if os.name == 'nt':
        import win32api
        import win32con
        try:
            win32api.RegOpenKey(win32con.HKEY_LOCAL_MACHINE,
                                "Software\\Wow6432Node")
            return 0
        except pywintypes.error, e:
            return 2
    else:
        raise RuntimeError(
            'This Function only support windows platform currently.')


def runShellCmd(cmdList, boolPrintStdOut=False, strFuncName='', strErrorMsg=''):
    ''' Run specific command list through subprocess Popen
        [Input]
        cmdList - the list contains the command and arguments
        strFuncName - The function name which is printed out in error message
        strErrorMsg - The error message print out while error occurs
        [Return]
        0 - Success
        -1 - Error
    '''
    import subprocess

    if boolPrintStdOut:
        procObj = subprocess.Popen(cmdList, stdin=subprocess.PIPE)
        intReturnCode = procObj.wait()
        if intReturnCode != 0:
            print '[%s][Error]%s\n' % (strFuncName, strErrorMsg)
            return -1
    else:
        procObj = subprocess.Popen(cmdList, stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        strReturnMsg = procObj.stdout.read()
        intReturnCode = procObj.wait()
        if intReturnCode != 0:
            print '[%s][Error]%s\n[Error Message]%s' % (
                strFuncName, strErrorMsg, strReturnMsg)
            return -1

    return 0


def OrgOfficalBuild(strOfficialBuildRoot, strArchitecture=None):
    ''' Organize official build to let ant Integration_test.xml could be execute
        [Input]
        strOfficialBuildRoot - The full path of official build root. (The upper level folder of output_release)
        strArchitecture - Specify 'win32' or 'x64'. Or Default will be determined by OS type
        [Return]
        0 - Success
        -1 - Error
    '''
    import os

    # Get architecture
    if None == strArchitecture:
        if 0 == is64bit():
            strArchitecture = 'x64'
        else:
            strArchitecture = 'win32'

    # Eliminate '\\'
    if strOfficialBuildRoot.endswith(os.path.sep):
        strOfficialBuildRoot = strOfficialBuildRoot[:len(
            strOfficialBuildRoot) - 1]

    # Variables
    strAdditionalFilePath = strOfficialBuildRoot + \
        r'\output\testing\integrating_test\runtime\addtional_file'
    strImageSrcPath = strOfficialBuildRoot + r'\output\image'
    strImageDestPath = strOfficialBuildRoot + r'\output\image\%s\%s'
    strSrcPath = strOfficialBuildRoot + r'\src'

    # Rename win32/x64 folder
    try:
        os.rename(os.sep.join([strOfficialBuildRoot,
                               strArchitecture]), strOfficialBuildRoot + r'\output')
    except:
        print '[OrgOfficalBuild][Error] rename offcial root name to output error'
        raise CrossPlatformException('[OrgOfficalBuild]rename offcial root name to output error')

    # Unzip Image file
    print 'Unzip Setup image...'
    for filename in os.listdir(strImageSrcPath):
        if '.zip' in filename:
            if ('win32' in filename) and ('win32' == strArchitecture):
                cmd = 'STAF local ZIP UNZIP ZIPFILE %s TODIRECTORY %s' % (os.sep.join([strImageSrcPath, filename]), strImageDestPath % ('win32', 'release'))
                if 0 != runShellCmd(cmd, True, 'OrgOfficalBuild'):
                    print 'Unzip Setup Error.\n'

            elif ('x64' in filename) and ('x64' == strArchitecture):
                cmd = 'STAF local ZIP UNZIP ZIPFILE %s TODIRECTORY %s' % (os.sep.join([strImageSrcPath, filename]), strImageDestPath % ('x64', 'release'))
                if 0 != runShellCmd(cmd, True, 'OrgOfficalBuild'):
                    print 'Unzip Setup Error.\n'

    # BuildImage
    print 'Prepare Setup package...'
    curFolderPath = os.getcwd()
    os.chdir(strAdditionalFilePath)
    cmd = [os.sep.join(
        [strAdditionalFilePath, 'BuildImage.bat']), strArchitecture]
    if 0 != runShellCmd(cmd, True):
        print 'Build Setup Error.\n'
        raise CrossPlatformException('[OrgOfficalBuild]Build Setup Error')

    os.chdir(curFolderPath)
    # Move build_integration_test.xml and build_integration_tset.PrepareEnv.xml
    print 'Move files...'
    moveFileList = ['build_integration_test.PrepareTestEnv.xml',
                    'build_integration_test.xml']
    if not os.access(strSrcPath, os.F_OK):
        os.mkdir(strSrcPath)
    for moveFile in moveFileList:
        cmd = ['xcopy', os.sep.join(
            [strAdditionalFilePath, moveFile]), strSrcPath, '/Y']
        runShellCmd(cmd, True)

    # Move STAF file
    print 'Moving STAF...'
    cmd = ['CMD', '/C', 'RMDIR', '/S', '/Q', r'C:\STAF\lib']
    runShellCmd(cmd, True)
    cmd = ['CMD', '/C', 'RMDIR', '/S', '/Q', r'C:\STAF\testsuites']
    runShellCmd(cmd, True)
    cmd = ['xcopy', os.sep.join(
        [strAdditionalFilePath, 'staf']), r'C:\STAF', '/Y', '/R', '/E']
    runShellCmd(cmd, True)

    return 0


def download(strSrcPath, strDestPath, strFsSharedFolderRoot, strFsNDUserName, strFsNDPassword, strFsNDDriveLetter):
    print '----Start to download----'
    # Delete previous files
    if('C:\\' != strDestPath) and (os.access(strDestPath, os.F_OK)):
        print '[download()] Delete Folder %s' % strDestPath
        cmd = ['CMD', '/C', 'RMDIR', '/S', '/Q', strDestPath]
        runShellCmd(cmd, True, 'download',
                    'delete directory %s Error' % (strDestPath))

    # Start to Download
    if not '' == strSrcPath:
        strSrcFullPath = os.sep.join([strFsSharedFolderRoot, strSrcPath])
    else:
        strSrcFullPath = strFsSharedFolderRoot

    copy_file_remote(strSrcFullPath, strDestPath, strFsNDUserName,
                     strFsNDPassword, strFsNDDriveLetter)


def download_Unzip(strSrcPath, strDestPath, strFsSharedFolderRoot, strFsNDUserName, strFsNDPassword, strFsNDDriveLetter):
    print '----Start to download----'
    # Delete previous files
    #if('C:\\' != strDestPath) and (os.access(strDestPath , os.F_OK)):
    #    print '[download()] Delete Folder %s' % strDestPath
    #    cmd = ['CMD','/C','RMDIR','/S','/Q',strDestPath]
    #    runShellCmd(cmd ,True, 'download', 'delete directory %s Error'% (strDestPath))

    # Start to Download
    if not '' == strSrcPath:
        strSrcFullPath = os.sep.join([strFsSharedFolderRoot, strSrcPath])
    else:
        strSrcFullPath = strFsSharedFolderRoot

    #copy_file_remote(strSrcFullPath, strDestPath, strFsNDUserName, strFsNDPassword, strFsNDDriveLetter)
    #cmd = r'STAF 10.201.16.52 FS COPY FILE C:\FileServerRoot\DeployZipPackage\DEPLOY.ZIP TODIRECTORY C:\\DeployPackage\\DEPLOY.ZIP'
    #runShellCmd(cmd, True, 'download_Unzip','download unzip file error.')

    # Do unzip
    cmd = ['CMD', '/C', 'RMDIR', '/S', '/Q', 'C:\\STAF\\LIB']
    runShellCmd(cmd, True, 'download_Unzip',
                'delete directory %s Error.' % ('C:\\STAF\\LIB'))
    cmd = 'STAF LOCAL ZIP UNZIP ZIPFILE C:\\DeployPackage\\DEPLOY.ZIP TODIRECTORY C:\\ REPLACE'
    runShellCmd(cmd, True, 'download_Unzip', 'download unzip file error.')


def collect_report(strClientMachineName, strFileServerIP, strReportRoot,
                   strFSToFolder='C:\\collect_report\\ZipREPORT'):
    print '----Start to collect_report----'
    strFSToFolder = strFSToFolder.replace('\\', "\\\\")
    strFSToFolder = strFSToFolder.replace('//', "////")
    if os.name == "nt":
        strZipPath = r'C:\%s.zip' % strClientMachineName
    elif os.name == "posix":
        strZipPath = r'/usr/local/staf/result/%s.zip' % strClientMachineName
    else:
        strZipPath = r'/usr/local/staf/result/%s.zip' % strClientMachineName

    if os.access(strZipPath, os.F_OK):
        os.remove(strZipPath)

    # get latest tmp folder
    strLatestFolderName = getLatestFolder(strReportRoot)
    if None == strLatestFolderName:
        print 'No report in the report folder'
        return

    # Zip report
    print 'Zip report...'
    strReportFolder = os.sep.join([strReportRoot, strLatestFolderName])

    # Copy COV file intor report folder
    lstCOVFile = glob.glob(os.path.join(strReportRoot, '*.cov'))
    print '-------- Copy COV file into report folder --------'
    print str(lstCOVFile)
    if len(lstCOVFile) > 1:
        for strFile in lstCOVFile:
            try:
                shutil.copyfile(strFile, os.path.join(strReportFolder,
                                                      os.path.basename(strFile)))
            except:
                print 'Copy COV file fail'
    else:
        print 'There has no COV file under %s' % strReportRoot

    cmd = ['STAF', 'local', 'ZIP', 'ADD', 'ZIPFILE', strZipPath, 'DIRECTORY',
           strReportFolder, 'RECURSE', 'RELATIVETO', strReportRoot]
    runShellCmd(cmd, True, 'collect_report',
                'Zip report folder %s error.' % (strReportFolder))

    print 'Copy file to File server...'
    cmd = ['STAF', 'local', 'FS', 'COPY', 'FILE', strZipPath,
           'TODIRECTORY', strFSToFolder, 'TOMACHINE', strFileServerIP]
    runShellCmd(cmd, True, 'collect_report', 'Copy report file error.')

    # Copy file to File server
    #f = open("c:\\cmd.txt", "w")
    boolMd5Compare = False
    intRetry = 0

    #f.write("md5:%s\n"%str(localMd5))
    #logging.info("Local Md5: %s"%localMd5)

    #sometimes, server cannot retrieve report from client due to staf select timeout,
    #add more retry times and wait
##    while not boolMd5Compare and intRetry < 10 :
##        print 'Copy file to File server..., retry:%s'%str(intRetry)
##        cmd = ['STAF','local','FS','COPY','FILE',strZipPath, 'TODIRECTORY', strFSToFolder,'TOMACHINE',strFileServerIP]
##        runShellCmd(cmd ,True, 'collect_report', 'Copy report file error.')
##
##        #compare md5
##        logging.info('Calculate remote md5...')
##        strRemotepath = os.path.join(strFSToFolder, os.path.basename(strZipPath))
##        strRemotepath = strRemotepath.replace("\\","\\\\")
##        cmd = r'START COMMAND python PARMS ' \
##           + r'"util_cross_client.py md5_for_file \"' + strRemotepath \
##           + r'\"" WAIT RETURNSTDOUT STDERRTOSTDOUT WORKDIR C:\STAF\lib\python\crossPlatform'
##        logging.info(cmd)
##        from staf.tmStafHandle import TmStafHandle
##
##        objTmStafHandle = TmStafHandle("Caluculate MD5")
##        objResult = objTmStafHandle.submit(strFileServerIP, "PROCESS", cmd)
##        remoteMd5 = objResult.getResult()
##        logging.info("Remote Md5: %s" %remoteMd5)
##
##        if str(localMd5) in str(remoteMd5):
##            boolMd5Compare = True
##
##        intRetry = intRetry + 1
##        logging.info("Retry[%d] times and wait 5 seconds" %intRetry)
##        time.sleep(5)


    # Delete Report folder
    #print 'Delete Report folder...'
    #cmd = ['CMD','/C','RMDIR','/S','/Q',strReportRoot]
    #runShellCmd(cmd ,True, 'collect_report', 'delete directory %s Error.'%(strReportRoot))
def md5_for_file(strfile, block_size=2 ** 20):
    f = file(strfile, 'rb')
    import hashlib
    md5 = hashlib.md5()
    while True:
        data = f.read(block_size)
        if not data:
            break
        md5.update(data)
    f.close()
    import urllib
    return urllib.quote(md5.digest(), '+?&')

if __name__ == '__main__':
    print '[DEBUG]' + ' '.join(sys.argv)

    if (len(sys.argv) < 2):
        print '[Error] Invalid input numbers %d\n [USAGE]command arg1 arg2...\ncommand = download | collect_report' % len(sys.argv)
    else:
        strCommand = sys.argv[1]
        if ('collect_report' == strCommand):
            try:
                strFileName, strCommand, strClientMachineName, strFileServerIP, strReportRoot, strFSToFolder = sys.argv
            except:
                print '[Error] Invalid arguments %s\n[Usage]collect_report strClientMachineName strFileServerIP, strReportRoot, strFSToFolder ' % sys.argv
            else:
                collect_report(strClientMachineName, strFileServerIP,
                               strReportRoot, strFSToFolder)
        elif ('download' == strCommand):
            try:
                strFileName, strCommand, strSrcPath, strDestPath, strFsSharedFolderRoot, strFsNDUserName, strFsNDPassword, strFsNDDriveLetter = sys.argv
            except:
                print '[Error] Invalid arguments %s\n[Usage]download SrcPath DestPath FsSharedFolderRoot strFsNDUserName strFsNDPassword strFsNDDriveLetter' % sys.argv
            else:
                download(strSrcPath, strDestPath, strFsSharedFolderRoot, strFsNDUserName, strFsNDPassword, strFsNDDriveLetter)
        elif ('download_Unzip' == strCommand):
            try:
                strFileName, strCommand, strSrcPath, strDestPath, strFsSharedFolderRoot, strFsNDUserName, strFsNDPassword, strFsNDDriveLetter = sys.argv
            except:
                print '[Error] Invalid arguments %s\n[Usage]download SrcPath DestPath FsSharedFolderRoot strFsNDUserName strFsNDPassword strFsNDDriveLetter' % sys.argv
            else:
                download_Unzip(strSrcPath, strDestPath, strFsSharedFolderRoot, strFsNDUserName, strFsNDPassword, strFsNDDriveLetter)
        elif ('org_build' == strCommand):
            try:
                strArchitecture = None
                strFileName, strCommand, strOfficialBuildRoot = sys.argv
                if 4 == len(sys.argv):
                    strArchitecture = sys.argv[3]
            except:
                print '[Error] Invalid arguments %s\n[Usage]org_build strOfficialBuildRoot [strArchitecture]' % sys.argv
            else:
                OrgOfficalBuild(strOfficialBuildRoot, strArchitecture)
        elif ('md5_for_file' == strCommand):
            try:
                strFileName, strCommand, strFile = sys.argv
            except:
                print '[Error] Invalid arguments %s\n[Usage]md5_for_file strFile' % sys.argv
            else:
                print md5_for_file(strFile)
        else:
            print '[Error] Invalid command type\n [USAGE]command arg1 arg2...\ncommand = download | collect_report'
