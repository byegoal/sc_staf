import trend.networkUtil as networkUtil
import subprocess
import logging
import os
from uniclient.common.call_staf_service import StafService
from tmstaf.emailNotify import EmailNotify
from tmstaf.multiPlatformRunner import ShellTask
from trend import processUtil, exceptionUtil
from Ti_OEM.common.utility import GetIniSetting


class AllowFailTask(ShellTask):
    def __init__(self, lstArgs, strWorkDir='', expectResult=None):
        super(AllowFailTask, self).__init__(lstArgs, strWorkDir)

    def run(self):
        if self.strHost in ('', 'local', 'localhost'):
            try:
                obj = processUtil.TmProcess(self.lstArgs)
                self.strStdout = obj.readStdout()
                self.actualResult = obj.wait()
            except:
                logging.debug('[AllowFailTask()][Error] %s execute error. %s' %
                              (lstCmd, exceptionUtil.getException()))
        else:
            from staf.processHelper import AsyncStafProcess
            from trend.exceptionUtil import TimeoutError
            lstCmd = ['cmd', '/c'] + self.lstArgs
            try:
                objStafProcess = AsyncStafProcess(
                    self.strHost, lstCmd, self.strWorkDir)
                self.actualResult = objStafProcess.wait(self.intTimeout)
                self.strStdout = objStafProcess.readStdout()
            except (RuntimeError, TimeoutError):
                logging.debug('[AllowFailTask()][Error] %s execute error. %s' %
                              (lstCmd, exceptionUtil.getException()))

    def __str__(self):
        return '<AllowFailTask %s at %s>' % (os.path.join(self.strWorkDir, self.lstArgs[0]), self.strHost)


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

    logging.debug('----copy_file_remote()----')
    if(None == strSrcPath or None == strDestPath):
        logging.debug('[copy_file_remote()][Error] Invalid source or destination path')
        return -1

    # Connect to network drive
    strRemoteUncPath = None
    if('remote' in option):
        remoteOne = option['remote']
        if('src' == remoteOne):
            strRemoteUncPath = strSrcPath
            strSrcPath = strImage + os.path.sep
        elif('dest' == remoteOne):
            strRemoteUncPath = strDestPath
            strDestPath = strImage + os.path.sep
        else:
            logging.debug('[copy_file_remote()][Error] Invalid strRemote')
            return -1
    else:
        strRemoteUncPath = strSrcPath
        strSrcPath = strImage + os.path.sep

    if(0 != networkUtil.mountNetworkDrive(strImage, strRemoteUncPath, strUserName, strPassword)):
        logging.debug(
            '[copy_file_remote()][Error] Fail on mount network drive')
        return -1

    # Copy file
    copyCmdList = []

    if(not ('fileName' in option or 'pathlist' in option)):
        if not strDestPath.endswith(os.path.sep):
                strDestPath = strDestPath + os.path.sep
        copyCmd = r'xcopy "%s" "%s" /e /y /r /I' % (strSrcPath, strDestPath)
        copyCmdList.append(copyCmd)
    else:
        if('fileName' in option):
            if not strSrcPath.endswith(os.path.sep):
                strSrcPath = strSrcPath + os.path.sep
            if not strDestPath.endswith(os.path.sep):
                strDestPath = strDestPath + os.path.sep

            fileName = option['fileName']
            strSrcFile = strSrcPath + fileName
            #copyCmd = r'xcopy "%s" "%s" /e /y /r' % (strSrcFile,strDestPath)
            copyCmd = r'xcopy "%s" "%s" /y /r' % (strSrcFile, strDestPath)
            copyCmdList.append(copyCmd)

        if('pathlist' in option):
            if not strSrcPath.endswith(os.path.sep):
                strSrcPath = strSrcPath + os.path.sep
            if not strDestPath.endswith(os.path.sep):
                strDestPath = strDestPath + os.path.sep

            PathList = option['pathlist']
            strSrcFile = None
            strDestFile = None
            for path in PathList:
                if (os.path.sep == path):
                    path = ""

                strSrcFile = strSrcPath + path
                strDestFile = strDestPath + path
                if not strDestFile.endswith(os.path.sep):
                    strDestFile = strDestFile + os.path.sep
                copyCmd = r'xcopy "%s" "%s" /e /y /r /I' % (
                    strSrcFile, strDestFile)
                copyCmdList.append(copyCmd)

    for copyCmd in copyCmdList:
        logging.info('[copy_file_remote()] Copy file command is %s' % copyCmd)
        procObj = subprocess.Popen(copyCmd, stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        strReturnMsg = procObj.stdout.read()
        intReturnCode = procObj.wait()
        if intReturnCode != 0:
            logging.debug('[copy_file_remote()][Error] Copy File Error.\n [Error Message]%s' % strReturnMsg)
            networkUtil.unmountNetworkDrive(strImage)
            return -1

    # Unmount network drive
    networkUtil.unmountNetworkDrive(strImage)
    return 0


def check_new_build(intOldBuildNum, strUserName, strPassword, strImage,
                    strOfficalPathList=[r'\\10.201.16.7\Uniclient\win32\v1.1\en'],
                    strSubPath=r'\win32\v17.50\MUI_ASUS',
                    strBuildcCeckFolder='md5'):
    ''' Check whether there is newer official build by verify all {build_Num}.txt in md5 folder under strOfficalPathList
        [Input]
        intOldBuildNum - current build number
        strUserName - The username for login to remote machine
        strPassword - The password for login to remote machine
        strImage - The specific driver (Ex: C:, D:) for network construction
        strOfficalPathList - the list contain offical build root path
        strSubPath - the list contain offical build sub path
        strBuildcCeckFolder - the new build check folder (Ex: md5, check, ...)
        [Return]
        -1 - Error
        0 - One of strOfficalPathList doesn't have newer build
        new build number - interger. new official build number.
    '''
    retNewBuildNumber = 0
    newBuildNumber = 0
    if 0 == len(strOfficalPathList):
        logging.debug('[check_new_build()][Error] Invalid strOfficalPathList Number ')
        return -1

    for strOfficalPath in strOfficalPathList:
        # Connect to network drive
        if '' == strUserName:
            strUserName = None

        if(0 != networkUtil.mountNetworkDrive(strImage, strOfficalPath, strUserName, strPassword)):
            logging.debug('[check_new_build()][Error] Fail on mount network drive')
            return -1

        try:
            newestFile = ''
            #currentFile = strImage + r'\md5\%d.txt'%(intOldBuildNum)
            #strImage2 = strImage + strSubPath
            #strOfficalPath2 = strOfficalPath + strSubPath
            #
#            currentFile = strImage2 + r'\md5\%d.txt'%(intOldBuildNum)
            currentFile = os.path.join(strImage, strSubPath) + r'\%s\%d.txt' % (strBuildcCeckFolder, intOldBuildNum)
            try:
                currentTime = os.path.getctime(currentFile)
            except:
                logging.debug('[check_new_build()] %s file %s can not be found under %s' %
                              (strBuildcCeckFolder, currentFile, os.path.join(strOfficalPath, strSubPath)))
                currentTime = 0

            for file in os.listdir(os.path.join(strImage, strSubPath, strBuildcCeckFolder)):
                fullPath = os.path.join(strImage,
                                        strSubPath, strBuildcCeckFolder, file)
                if os.path.getctime(fullPath) > currentTime:
                    newestFile = file
                    currentTime = os.path.getctime(fullPath)

            if '' == newestFile:
                logging.info('[check_new_build()] No new build number under %s' % os.path.join(strOfficalPath, strSubPath))
                newBuildNumber = 0
            else:
                newBuildNumber = int(newestFile[:newestFile.find('.txt')])
                logging.info('[check_new_build()] New build number is %d for %s' % (newBuildNumber, os.path.join(strOfficalPath, strSubPath)))
        finally:
            # Unmount network drive
            networkUtil.unmountNetworkDrive(strImage)
            if 0 == newBuildNumber:
                return 0
            elif (0 != retNewBuildNumber) and (retNewBuildNumber != newBuildNumber):
                logging.info('[check_new_build()] The latest build number of two officialBuildPath does not match (%d and %d)' %
                             (retNewBuildNumber, newBuildNumber))
                return 0
            else:
                retNewBuildNumber = newBuildNumber

    return retNewBuildNumber


def check_new_build_by_folder(
    intOldBuildNum, strUserName, strPassword, strImage,
    strOfficalPathList=[r'\\10.201.16.7\Uniclient\win32\v1.1\en'],
    strSubPath=r'\win32\v17.50\MUI_ASUS',
        strBuildcCeckFolder='md5'):
    ''' Check whether there is newer official build by verify all {build_Num}.txt in md5 folder under strOfficalPathList
        [Input]
        intOldBuildNum - current build number
        strUserName - The username for login to remote machine
        strPassword - The password for login to remote machine
        strImage - The specific driver (Ex: C:, D:) for network construction
        strOfficalPathList - the list contain offical build root path
        strSubPath - the list contain offical build sub path
        strBuildcCeckFolder - the new build check folder (Ex: md5, check, ...)
        [Return]
        -1 - Error
        0 - One of strOfficalPathList doesn't have newer build
        new build number - interger. new official build number.
    '''
    retNewBuildNumber = 0
    newBuildNumber = 0
    newBuildFolder = ''
    if 0 == len(strOfficalPathList):
        logging.debug('[check_new_build()][Error] Invalid strOfficalPathList Number ')
        return -1

    for strOfficalPath in strOfficalPathList:
        # Connect to network drive
        if '' == strUserName:
            strUserName = None

        if(0 != networkUtil.mountNetworkDrive(strImage, strOfficalPath, strUserName, strPassword)):
            logging.debug('[check_new_build()][Error] Fail on mount network drive')
            return -1

        try:
            newestFile = ''
            newestFolder = getLatestFolder(os.path.join(strImage, strSubPath))
            #print newestFolder
            #currentFile = strImage + r'\md5\%d.txt'%(intOldBuildNum)
            #strImage2 = strImage + strSubPath
            #strOfficalPath2 = strOfficalPath + strSubPath
            #
            #currentFile = strImage2 + r'\md5\%d.txt'%(intOldBuildNum)
            #currentFile = os.path.join(strImage, strSubPath) + r'\%s\%d.txt'%(strBuildcCeckFolder, intOldBuildNum)
            #try:
            #    currentTime = os.path.getctime(currentFile)
            #except:
            #    logging.debug('[check_new_build()] %s file %s can not be found under %s' %
            #                  (strBuildcCeckFolder, currentFile, os.path.join(strOfficalPath, strSubPath)))
            #    currentTime = 0
            #
            #for file in os.listdir(os.path.join(strImage, strSubPath, strBuildcCeckFolder)):
            #    fullPath = os.path.join(strImage, strSubPath, strBuildcCeckFolder,file)
            #    if os.path.getctime(fullPath) > currentTime:
            #        newestFile = file
            #        currentTime = os.path.getctime(fullPath)

            if '' == newestFolder:
                logging.info('[check_new_build()] No new build foler under %s' % os.path.join(strOfficalPath, strSubPath))
                newBuildFolder = ''
            else:
                #newBuildNumber = int(newestFile[:newestFile.find('.txt')])
                newBuildFolder = newestFolder
                logging.info('[check_new_build()] New build number is %s for %s' % (newBuildFolder, os.path.join(strOfficalPath, strSubPath)))
        finally:
            # Unmount network drive
            networkUtil.unmountNetworkDrive(strImage)
            if '' == newBuildFolder:
                return 0
            #elif ('' != newBuildFolder) and (retNewBuildFolder != newBuildFolder):
            #    logging.info('[check_new_build()] The latest build number of two officialBuildPath does not match (%d and %d)'%
            #                 (retNewBuildNumber,newBuildNumber))
            #    return 0
            else:
                retNewBuildFolder = newBuildFolder

    return retNewBuildFolder


def unzipFile(strFilePath, strDestPath, boolReplace=True):
    ''' Unzip file to specific directory
        [Input]
        strFilePath - String. The fullpath of zip file.
        strDestPath - String. The destination directory to contain unzip files.
        boolReplace - Boolean. Replace previous file.
    '''
    logging.info('----unzipFile()----')
    if not os.access(strFilePath, os.F_OK):
        logging.debug('[unzipFile()] The file %s does not exist' %
                      (strFilePath))
        return

    objStafService = StafService()

    cmd = 'UNZIP ZIPFILE %s TODIRECTORY %s' % (strFilePath, strDestPath)
    if boolReplace:
        cmd = cmd + ' REPLACE'

    objStafService.callStafService('local', "ZIP", cmd)


def getSummaryFromMainHtml(strMainHtmlPath):
    ''' Get required information for whole report from main.html
        [Input]
        strMainHtmlPath - String. The fullpath to main html
        [Return]
        A list contain (IP,Total,Passes,Fails,Crashes,Elapsed Time)
        [Note]
        This function depend on reportUtil.py. If the main.html format is changed, this function may not work
    '''
    logging.info('----getSummaryFromMainHtml()----')
    if not os.access(strMainHtmlPath, os.F_OK):
        logging.debug('[getSummaryFromMainHtml()] The file %s does not exist' %
                      (strMainHtmlPath))
        return

    listResult = []
    fMainHtml = open(strMainHtmlPath, 'r')
    strLine = fMainHtml.readline()
    while '' != strLine:
        if 'IP Address:' in strLine:
            iIPIndex = strLine.find('IP Address:')
            strIPAddress = eliminateTag(strLine[(iIPIndex + 11):])
            if (strIPAddress.endswith('\n')):
                strIPAddress = strIPAddress[:(len(strIPAddress) - 1)]
            listResult.append(strIPAddress)
        if ('Total' in strLine) and ('Passes' in strLine) and ('Fails' in strLine):
            for i in range(5):
                strLine = fMainHtml.readline()
                if (strLine.endswith('\n')):
                    strLine = strLine[:(len(strLine) - 1)]
                listResult.append(eliminateTag(strLine))
            break
        strLine = fMainHtml.readline()

    fMainHtml.close()
    return listResult


def getFailedSummaryResult(strMainHtmlPath, dictMachineInfo, machineName):
    ''' If main.html could not get required information, call this function to get partial information
    [Return]
        A list contain (IP,Total,Passes,Fails,Crashes,Elapsed Time)
    '''
    logging.info('----getFailedSummaryResult()----')
    strIP = getIPfromMachineName(dictMachineInfo, machineName)
    if not os.access(strMainHtmlPath, os.F_OK):
        logging.debug('[getFailedSummaryResult()] The file %s does not exist' %
                      (strMainHtmlPath))
        return [strIP, '0', '0', '0', '0', 'No main.html']

    listResult = []
    listResult.append(strIP)
    fMainHtml = open(strMainHtmlPath, 'r')
    strLine = fMainHtml.readline()

    while '' != strLine:
        if ('Pass' in strLine) and ('Fail' in strLine):
            strLine = eliminateTag(strLine).replace(' ', '')
            passIndex = strLine.find('Pass')
            failIndex = strLine.find('Fail')
            strPassNum = strLine[(passIndex + 5):failIndex]
            strFailNum = strLine[(failIndex + 5):]
            strTotalNum = str(int(strPassNum) + int(strFailNum))
            listResult.append(strTotalNum)
            listResult.append(strPassNum)
            listResult.append(failIndex)
            listResult.append('Unavailable')
            break
        strLine = fMainHtml.readline()

    listResult.append('Not complete')

    return listResult

#def getLatestFolder(strPath):
#    '''Get the latest folder name under the input path
#       [Input]
#       strPath - the specific path
#       [Return]
#       The folder name or None (No any folder)
#       [Note]
#       This is only for windows
#    '''
#    logging.info('----getLatestFolder()----')
#    os.chdir(strPath)
#    fd = os.popen(r"dir /ad /od /b *.*")
#    files = fd.read().splitlines()
#    os.close(fd)
#    if 0 == len(files):
#        logging.info('getLatestFolder() There is no directory')
#        return None
#    else:
#        return files[-1]


def eliminateTag(strInput):
    ''' Remove any <xxx> from a string
        [Input]
        A string.
        [Return]
        A string without <...>
    '''
    logging.info('----eliminateTag()----')
    if (0 == len(strInput)):
        logging.debug('[Error]An empty String')
        return

    iStart = strInput.find('<')
    iEnd = strInput.find('>')
    while -1 != iStart and -1 != iEnd:
        strInput = strInput[:iStart] + strInput[iEnd + 1:]
        iStart = strInput.find('<')
        iEnd = strInput.find('>')

    return strInput


def initLogFile(strLogFile):
    logFile = logging.FileHandler(strLogFile, 'wb')
    logFile.setLevel(logging.DEBUG)
    strFormat = '%(asctime)s [%(thread)d] %(module)s.%(funcName)s %(message)s'
    logFile.setFormatter(logging.Formatter(strFormat, '%H:%M:%S'))
    logging.getLogger().addHandler(logFile)


def send_mail(strFrom, lstTo, lstCC, strSubject, strBodyFile, lstAttached, smtpServer='10.201.16.3', sender='uniclient_crossplatform@trend.com'):
    ''' Send mail
        [Input]
        strFrom - Who send the mail (Shown in email)
        lstTo - The receiver list
        lstCC -The cc list
        strSubject - The Subject.
        strBodyFile - The strBody file path. (Both Relative and Full are acceptable)
        lstAttached - The attached file list
        smtpServer - the smtp server address
        sender - Who send the mail
    '''
    logging.info('----send_mail()----')
    if(0 == len(lstTo)):
        logging.debug('[Error]No receiver')
        return

    if not os.access(strBodyFile, os.F_OK):
        logging.debug('[Error]strBodyFile %s access fail' % (strBodyFile))
        return

    obj = EmailNotify(strFrom, smtpServer, sender)
    obj.setSubject(strSubject)
    obj.setHtmlBody(strBodyFile)

    for fileName in lstAttached:
        obj.addAttachment(fileName)

    if(0 == len(lstCC)):
        obj.send(lstTo)
    else:
        obj.send(lstTo, lstCC)


def delete_directory(deletePathList):
    ''' Delete the path specified in the list
        [Input]
        deletePathList - the list contain path.
        [Return]
        0 - Success
        1 - Error
    '''
    logging.info('----delete_directory()----')

    iResult = 0
    for deletePath in deletePathList:
        cmd = ['CMD', '/C', 'RMDIR', '/S', '/Q', deletePath]
        procObj = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        strReturnMsg = procObj.stdout.read()
        intReturnCode = procObj.wait()
        if intReturnCode != 0:
            logging.info('Delete directory %s Error.\n [Error Message]%s' %
                         (deletePath, strReturnMsg))
            iResult = 1

    return iResult


def getMachineInfo(strMachineFile='Machine_List.ini'):
    ''' Get machine information
        [Input]
        strMachineFile - the machine config file name
        [Return]
        A tuple (dictMachineInfo,mapMachinePlatform)
        dictMachineInfo - A Dictionary contains {machineIP : [machineName,machineArchitecture,machinePlatform]}
        mapMachinePlatform - A dictionary contains {machineName : Platform}
    '''
    machineListObj = GetIniSetting(strMachineFile)
    intIndex = 1
    dictMachineInfo = {}
    mapMachinePlatform = {}
    listMachineName = []
    listMachineID = []
    while True:
        listOneMachineInfo = machineListObj.getIniVar(
            'TestingTarget', 'Machine%s' % intIndex)

        if None == listOneMachineInfo:
            break
        else:
            dictMachineInfo[listOneMachineInfo[0]] = listOneMachineInfo[1:]
            listMachineName.append(listOneMachineInfo[1])
            mapMachinePlatform[listOneMachineInfo[1]] = listOneMachineInfo[3]
            listMachineID.append(listOneMachineInfo[4])
            intIndex = intIndex + 1
    return (dictMachineInfo, mapMachinePlatform, listMachineID)


def getIPfromMachineName(dictMachineInfo, strMachineName):
    ''' Get machine information
        [Input]
        dictMachineInfo - A Dictionary contains {machineIP : [machineName,machineArchitecture,machinePlatform]}
        strMachineName - Machine Name
        [Return]
        IP or 0
    '''
    ipList = dictMachineInfo.keys()
    for ip in ipList:
        if dictMachineInfo[ip][0] == strMachineName:
            return ip
    return 0


def getMailProperty(strConfigFile='CrossPlatform_Config.ini'):
    ''' Get Mail property from ini file
        [Input]
        strConfigFile - The config file name
        [Return]
        Sender , SmtpServer , mailList , ccList , AttachedFileList , Subject
    '''
    returnList = []
    INIObj = GetIniSetting(strConfigFile)

    returnList.append(INIObj.getIniVar('Mail', 'Sender'))
    returnList.append(INIObj.getIniVar('Mail', 'SmtpServer'))
    mailList = INIObj.getIniVar('Mail', 'mailList')
    if isList(mailList):
        returnList.append(mailList)
    else:
        returnList.append([mailList])

    ccList = INIObj.getIniVar('Mail', 'ccList')
    if isList(ccList):
        returnList.append(ccList)
    else:
        returnList.append([ccList])

    AttachedFileList = INIObj.getIniVar('Mail', 'AttachedFileList')
    if isList(AttachedFileList):
        returnList.append(AttachedFileList)
    else:
        returnList.append([AttachedFileList])

    returnList.append(INIObj.getIniVar('Mail', 'Subject'))
    return returnList


def isList(listTest):
    if listTest.__class__ is list:
        return True
    else:
        return False


def unittest_copy_file_remote():
    copy_file_remote(r'\\tw-testing\Uniclient_Lab\QA\Geffrey\UPD_BF_PU_004',
                     'c:\\ttttt', r'uniclient', 'Automation@2009', 'G:')


def unittest_check_new_build():
##    print '  Latest build number is %s' % (check_new_build(1022,'', '', 'Y:'))
##    print '  Latest build number is %s' % (check_new_build(1150,'', '', 'Y:',[r'\\10.201.16.7\Uniclient\win32\v1.1\en',r'\\10.201.16.7\Uniclient\win32\v1.0\en']))
    print '  Latest build number is %s' % (check_new_build(1150, '', '', 'Y:', [r'\\10.201.16.7\Uniclient\win32\v1.1\en', r'\\10.201.16.7\Uniclient\win32\v1.1\en']))


def unittest_unzipFile():
    unzipFile('C:\\TW-SAMCHANG.zip', 'C:\\TTT\\1088')
    unzipFile('C:\\TW-SAMCHANG.zip', 'C:\\TTT\\1088', False)
    unzipFile('C:\\TW-SAMCHANG.zip', 'C:\\TTT\\1088')
    os.system('RMDIR /S /Q c:\\TTT')


def unittest_eliminateTag():
    print eliminateTag('</b></td><td>Windows XP SP3</td></tr>')
    print eliminateTag('<td><font color="red">9</font></td>')


def unittest_getSummaryFromMainHtml():
    getSummaryFromMainHtml('C:\UniClient_TestCase_Result\Uniclient_result_2009-04-21_21-04\main.html')


def unittest_getFailedSummaryResult():
    print getFailedSummaryResult('C:\main.html', '', '')


def unittest_getLatestFolder():
    getLatestFolder('C:\UniClient_TestCase_Result')
    getLatestFolder('C:\log')


def unittest_send_mail():
    send_mail('sam_chang@trend.com.tw', ['sam_chang@trend.com.tw'], [
        ], 'Test for Cross Platform', r'C:\STAF\NOTICES.htm', [])


def unittest_getIPfromMachineName():
    dictMachineInfo = {'10.201.16.7': ['CI', 'x86', 'windows xp sp2']}
    print getIPfromMachineName(dictMachineInfo, 'CI')


def getLatestFolder(strPath):
    '''Get the latest folder name under the input path
       [Input]
       strPath - the specific path
       [Return]
       The folder name or None (No any folder)
       [Note]
       This is only for windows
    '''
    print '----getLatestFolder()----'
    curdir = os.getcwd()
    os.chdir(strPath)
    #files = os.popen(r"dir /ad /od /b *.*").read().splitlines()
    fd = os.popen(r"dir /ad /od /b *.*")
    files = fd.read().splitlines()
    fd.close()
    os.chdir(curdir)
    if 0 == len(files):
        print 'getLatestFolder() There is no directory'
        return None
    else:
        return files[-1]

if __name__ == '__main__':
    x = getLatestFolder("C:\\STAF\\lib\\python\\Ti_OEM")
    print x
    #logging.basicConfig(level = logging.DEBUG)
    #logging.info('****Start to execute Unittest****')
    #unittest_check_new_build()
##    print get_officalBuildRootPath(1075)
##    print get_officalBuildRootPath(1074)
    #print getMachineInfo()
    #unittest_unzipFile()
    #unittest_eliminateTag()
    #unittest_getSummaryFromMainHtml()
    #unittest_getLatestFolder()
##    unittest_getFailedSummaryResult()
##    unittest_send_mail()
##    unittest_getIPfromMachineName()
##    print getMailProperty()
    #delete_directory(['C:\\log','C:\\Donkey','C:\\tmp\\1071'])
    #unittest_check_new_build()
