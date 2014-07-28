"""
the cross platform utility module
"""
import logging
import os
import subprocess
import shutil
import time
#
import trend.networkUtil as networkUtil
from trend import processUtil, exceptionUtil
#
from tmstaf.emailNotify import EmailNotify
from tmstaf.multiPlatformRunner import ShellTask, PythonTask
#
import crossPlatform.util
from crossPlatform.errorCode import ErrorautoServerMain as errASM

import crossPlatform.labManager
import crossPlatform.crossPlatformIni as cp_ini


def funcLoadConfigure(config):
    """
    load cross platform condifuration ini content.
    @type config: String
    @param config: configuration file.
    @return: None
    """
    if config is None:
        logging.error('The config is None.')
        return
    logging.info(str("load CrossPlatform configuration %s" % config))
    os.chdir(os.path.dirname(__file__))
    objCrossplatformConfigure = crossPlatform.util.GetIniSetting(config)
    cp_ini.g_objIni = objCrossplatformConfigure


def getMachineInfo(strMachineFile='Machine_List.ini', oMachineIni=None):
    '''
        Get machine information
        @param strMachineFile: the machine config file name
        @param oMachineIni: the machine ini object default is None, otherwise
                            ignore strMachineFile use this object get machine
                            list information.
        @return:
        A tuple (dictMachineInfo,mapMachinePlatform)
        dictMachineInfo - A Dictionary contains {machineIP :
        [machineName,machineArchitecture,machinePlatform]}
        mapMachinePlatform - A dictionary contains {machineName : Platform}
    '''
    if oMachineIni is None:
        if cp_ini.g_objIni is None:
            machineListObj = crossPlatform.util.GetIniSetting(strMachineFile)
        else:
            machineListObj = cp_ini.g_objIni
    else:
        machineListObj = oMachineIni
    dictMachineInfo = {}
    mapMachinePlatform = {}
    listMachineName = []
    listMachineID = []
    try:
        dictMachine = dict(machineListObj.iterSection('TestingTarget'))
        for strKey in dictMachine:
            listOneMachineInfo = dictMachine[strKey]

            if None == listOneMachineInfo:
                break
            else:
                dictMachineInfo[listOneMachineInfo[0]] = listOneMachineInfo[1:]
                listMachineName.append(listOneMachineInfo[1])
                mapMachinePlatform[listOneMachineInfo[1]
                                   ] = listOneMachineInfo[3]
                listMachineID.append(listOneMachineInfo[4])
    except:
        pass
    return (dictMachineInfo, mapMachinePlatform, listMachineID)


def funcGetValue(strSection, strKey):
    """
    utility export function entry provide use to get ini value
    by input data pair (section, key)
    @param strSection: specify section value
    @param strKey: specify the key value
    @return:
        to return the ini value by section and key
    """
    return cp_ini.g_objIni.getIniVar(strSection, strKey)


def funcGetSectionDict(strSection):
    """
    @type strSection: String
    @param strSection: the Section value
    @return: the all key-value dictory.
    """
    return dict(cp_ini.g_objIni.iterSection(strSection))


def funcRevertVirtualMachine(strMachineIP, strMachineID,
                             strLmIP, strLmUserName, strLmPassword):
    """
    revert VM by SOAP method.
    @param strMachineIP: machine ip
    @param strMachineID: VM machine id for VM Lab Manager
    @type strLmIP: String
    @param strLmIP: Lab Manager IP
    @param strLmUserName: lab manager account for revert command
    @param strLmPassword: lab manager password for revert command
    @return:
        errASM.SUCCESS measn revert vm OK
        others means NG, please check error log
    """
    intReTry = 3
    while intReTry > 0:
        retvalue = crossPlatform.labManager.funcRevert(
            int(strMachineID), strLmIP, strLmUserName, strLmPassword)
        if retvalue != 200:
            logging.info(str('Revert VM %s(%s) fail %s, wait 2 sec then do retry!'
                             % (strMachineIP, strMachineID, str(retvalue))))
            time.sleep(2)
            intReTry = intReTry - 1
        else:
            logging.info(str("revert VM %s OK" % strMachineID))
            return errASM.SUCCESS
    #
    logging.error(str("revert VM %s fail!" % strMachineID))
    return errASM.FAIL


def funcFetchTask(lstTaskFolder):
    """
    fetch the earlier task in folder task list
    @type lstTaskFolder: List
    @param lstTaskFolder: the task folder list the first folder has first
                            period. fetch task is first in first out in
                            task queue.

    @return: if get task will return full file path, otherwise None.
    """
    for folder in lstTaskFolder:
        task = None
        currentTime = 0
        if os.path.exists(folder):
            for item in os.listdir(folder):
                filename = os.path.join(folder, item)
                if os.path.isfile(filename):
                    logging.info(str("found a task %s" % filename))
                    if (currentTime == 0) or \
                        (os.path.getctime(filename) < currentTime):
                        task = filename
                        currentTime = os.path.getctime(filename)
            if task is not None:
                logging.info(str("found the earlier task %s" % task))
                return task
        else:
            logging.error("The task folder [%s] is NOT exist!" % folder)
    return None

###############################################################################


def getTasksInfo(strMachineFile='Machine_List.ini', oMachineIni=None,
                 strSection='TestingTarget', strItem='Machine'):
    '''
        Get machine information
        @param strMachineFile: the machine config file name
        @param oMachineIni: the machine ini object default is None, otherwise
                            ignore strMachineFile use this object get machine
                            list information.
        @return:
        A tuple (dictMachineInfo,mapMachinePlatform)
        dictMachineInfo - A Dictionary contains
        {machineIP: [machineName,machineArchitecture,machinePlatform]}
        mapMachinePlatform - A dictionary contains {machineName : Platform}
    '''
    if oMachineIni is None:
        machineListObj = crossPlatform.util.GetIniSetting(strMachineFile)
    else:
        machineListObj = oMachineIni
    intIndex = 1
    dictMachineInfo = {}
    listMachineName = []
    while True:
        listOneMachineInfo = \
            machineListObj.getIniVar(
                strSection, str(strItem + '%s') % intIndex)

        if None == listOneMachineInfo:
            break
        else:
            dictMachineInfo[listOneMachineInfo[0]] = listOneMachineInfo[1:]
            listMachineName.append(listOneMachineInfo[1])
            intIndex = intIndex + 1
    return (dictMachineInfo)


def funcInitLogFile(strLogFile, backup=False, backupfile="C:\\cp_debug.log"):
    """
    backup and reset debug.log file
    @param strLogFile: the log file full path file name.
    @param backup: backup flag control do backup or not,
                   the defaul is no do backup
    @param backupfile: the backup file full path file name,
                       the defaul is C:\cp_debug.log
    """
    if backup:
        if os.path.isfile(strLogFile):
            logging.info(str("backup previous debug.log file %s to %s"
                             % (strLogFile, backupfile)))
            shutil.copyfile(strLogFile, backupfile)
    #
    logFile = logging.FileHandler(strLogFile, 'wb')
    logFile.setLevel(logging.DEBUG)
    strFormat = '%(asctime)s [%(thread)d] %(module)s.%(funcName)s %(message)s'
    logFile.setFormatter(logging.Formatter(strFormat, '%H:%M:%S'))
    logging.getLogger().addHandler(logFile)


def funcRevertRealMachine(strClientIp):
    """
    revert real machine use acronis through machine IP.
    @param strClientIp: the real machine IP
    @return:
        errASM.SUCCESS means OK
        others means NG, please check error log
    """
    objStafService = crossPlatform.util.StafService()
    logging.info("Do copy acronis_restore.py to client.")
    cmd = "COPY FILE C:\\STAF\\lib\\python\\crossPlatform\\acronis_restore.py " + \
          "TODIRECTORY C:\\STAF\\lib\\python TOMACHINE %s" % strClientIp
    objStafService.callStafService("local", "FS", cmd)

    logging.info("Do restore in client")
    cmd = "START COMMAND \"cmd\" PARAMS \"/C python acronis_restore.py\" " + \
          "RETURNSTDOUT RETURNSTDERR " + \
          "WORKDIR C:\\STAF\\lib\\python TITLE cmd WAIT"
    objStafService.callStafService(strClientIp, "PROCESS", cmd)

    # check staf status
    logging.info("Check staf status wait client reboot!")
    import staf.util
    ret = staf.util.waitStafQuit(strClientIp, 600)
    if ret != 0:
        logging.error(str("wait client %s showdown fail (%s)"
                          % (strClientIp, ret)))
        return errASM.STAF_QUIT_FAIL

    ret = staf.util.waitStafReady(strClientIp, 600)
    if ret != 0:
        logging.error(str("wait client %s re-start fail (%s)"
                          % (strClientIp, ret)))
        return errASM.STAF_READY_FAIL
    return errASM.SUCCESS


class CAllowFailServerTask(PythonTask):
    """
    class for server task to avoid fail then stop do test.
    PythonTask: the parent object
    """

    def __init__(self, strModule, strFunc, lstArgs=None, expectResult=None):
        super(CAllowFailServerTask, self).__init__(strModule, strFunc,
                                                      lstArgs, expectResult)

    def run(self):
        """
        the class entry do the task.
        """
        if self.strHost in ('', 'local', 'localhost'):
            try:
                exec u"from %s import %s" % (self.strModule, self.strFunc)
                funcObj = eval(self.strFunc)
                self.actualResult = funcObj(*self.lstArgs)
            except:
                logging.debug(str('[CAllowFailServerTask()]' +
                                  '[Error] execute error. %s'
                                  % (exceptionUtil.getException())))

        else:
            from staf.pyFuncHelper import RemotePythonRunner
            from trend.exceptionUtil import TimeoutError
            try:
                objRemotePythonRunner = RemotePythonRunner(self.strHost,
                                                           self.strModule,
                                                           self.strFunc,
                                                           self.lstArgs,
                                                           self.intTimeout)
                self.actualResult = objRemotePythonRunner.wait()
                self.strStdout = objRemotePythonRunner.readStdout()
            except (RuntimeError, TimeoutError):
                logging.debug(str('[CAllowFailServerTask()]' +
                                  '[Error] execute timeout error. %s'
                                  % (exceptionUtil.getException())))

    def __str__(self):
        return '<CAllowFailServerTask %s.%s at %s>' % (self.strModule,
                                                          self.strFunc,
                                                          self.strHost)


def funcCopyFileRemote(strSrcPath, strDestPath, strUserName, strPassword,
                       strImage, **option):
    '''
        Copy file to or from remote machine through network drive
        @param strSrcPath: The path to the source folder
        @param strDestPath: The path to the destination folder
        @param strUserName: The username for login to remote machine
        @param strPassword: The password for login to remote machine
        @param strImage: The specific driver (Ex: C:, D:) for network construction
        @param option:  remote = 'src' | 'dest'. Specify which one is the remote machine. Default is src.
                        pathlist = A list contains paths. Paths could be directory. The path would be append to strSrcPath
                        fileName = A string means specific file name.The name would be append to strSrcPath
        @return:
            0 - Success
            -1 - Failed
    '''

    logging.debug('----funcCopyFileRemote()----')
    if(None == strSrcPath or None == strDestPath):
        logging.error('Invalid source or destination path')
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
            logging.error('Invalid strRemote')
            return -1
    else:
        strRemoteUncPath = strSrcPath
        strSrcPath = strImage + os.path.sep

    #if(0 != networkUtil.mountNetworkDrive(strImage, strRemoteUncPath,
    #                                      strUserName, strPassword)):
    #    logging.error('Fail on mount network drive')
    #    return -1

    strSubPath = ''
    while(0 != networkUtil.mountNetworkDrive(strImage, strRemoteUncPath,
                                          strUserName, strPassword)):
        (filepath, filename) = os.path.split(strRemoteUncPath)
        print (filepath, filename)
        if len(filename) == 0:
            logging.error('Fail on mount network drive')
            return -1
        strRemoteUncPath = filepath
        strSubPath = os.path.sep.join([filename, strSubPath])

    # Copy file
    copyCmdList = []

    if(not ('fileName' in option or 'pathlist' in option)):
        if not strDestPath.endswith(os.path.sep):
            strDestPath = strDestPath + os.path.sep
        copyCmd = "xcopy \"%s\" \"%s\" /e /y /r /I" % (strSrcPath, strDestPath)
        copyCmdList.append(copyCmd)
    else:
        if('fileName' in option):
            if not strSrcPath.endswith(os.path.sep):
                strSrcPath = strSrcPath + os.path.sep
            if not strDestPath.endswith(os.path.sep):
                strDestPath = strDestPath + os.path.sep

            fileName = option['fileName']
            strSrcFile = os.path.join(strSrcPath, strSubPath, fileName)
            copyCmd = "xcopy \"%s\" \"%s\" /y /r" % (strSrcFile, strDestPath)
            copyCmdList.append(copyCmd)

        if('pathlist' in option):
            if not strSrcPath.endswith(os.path.sep):
                strSrcPath = strSrcPath + os.path.sep
            if not strDestPath.endswith(os.path.sep):
                strDestPath = strDestPath + os.path.sep

            lstPathList = option['pathlist']
            strSrcFile = None
            strDestFile = None
            for path in lstPathList:
                if (os.path.sep == path):
                    path = ""

                strSrcFile = strSrcPath + path
                strDestFile = strDestPath + path
                if not strDestFile.endswith(os.path.sep):
                    strDestFile = strDestFile + os.path.sep
                copyCmd = "xcopy \"%s\" \"%s\" /e /y /r /I" % (strSrcFile,
                                                            strDestFile)
                copyCmdList.append(copyCmd)

    for copyCmd in copyCmdList:
        logging.info(str('[funcCopyFileRemote()] Copy file command is %s'
                         % copyCmd))
        procObj = subprocess.Popen(copyCmd, stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.STDOUT)
        strReturnMsg = procObj.stdout.read()
        intReturnCode = procObj.wait()
        if intReturnCode != 0:
            logging.debug(str('[funcCopyFileRemote()]'
                              '[Error] Copy File Error.\n [Error Message]%s'
                              % strReturnMsg))
            networkUtil.unmountNetworkDrive(strImage)
            return -1

    # Unmount network drive
    networkUtil.unmountNetworkDrive(strImage)
    return 0


class AllowFailTask(ShellTask):
    """
    AllowFailTask class is a ShellTask class. It will handle the runtime and
    timeout exception to avoid stop run.
    """
    def __init__(self, lstArgs, strWorkDir='', expectResult=None):
        super(AllowFailTask, self).__init__(lstArgs, strWorkDir)

    def run(self):
        """
        Run Task
        """
        if self.strHost in ('', 'local', 'localhost'):
            try:
                obj = processUtil.TmProcess(self.lstArgs)
                self.strStdout = obj.readStdout()
                self.actualResult = obj.wait()
            except:
                logging.debug(str('[AllowFailTask()]'
                                  '[Error] %s execute error. %s'
                                  % (self.lstArgs,
                                     exceptionUtil.getException())))
        else:
            from staf.processHelper import AsyncStafProcess
            from trend.exceptionUtil import TimeoutError
            lstCmd = ['cmd', '/c'] + self.lstArgs
            try:
                objStafProcess = AsyncStafProcess(self.strHost, lstCmd,
                                                  self.strWorkDir)
                self.actualResult = objStafProcess.wait(self.intTimeout)
                self.strStdout = objStafProcess.readStdout()
            except (RuntimeError, TimeoutError):
                logging.debug(str('[AllowFailTask()]'
                                  '[Error] %s execute error. %s'
                                  % (lstCmd, exceptionUtil.getException())))

    def __str__(self):
        return '<AllowFailTask %s at %s>' % (os.path.join(self.strWorkDir,
                                                          self.lstArgs[0]),
                                             self.strHost)


def funcCheckNewBuild(intOldBuildNum, strUserName, strPassword, strImage="U:",
                      strOfficalPathList="", strSubPath="",
                      strBuildCheckFolder="md5"):
    '''
        Check whether there is newer official build by verify all
        {build_Num}.txt in md5 folder under strOfficalPathList
        @param intOldBuildNum: current build number
        @param strUserName: The username for login to remote machine
        @param strPassword: The password for login to remote machine
        @param strImage: The specific driver (Ex: C:, D:) for network construction
        @param strOfficalPathList: the list contain offical build root path
        @param strSubPath: the list contain offical build sub path
        @param strBuildCheckFolder: the new build check folder (Ex: md5, check, ...)
        @return:
        -1 - Error
        0 - One of strOfficalPathList doesn't have newer build
        new build number - interger. new official build number.
    '''
    retNewBuildNumber = 0
    newBuildNumber = 0
    if 0 == len(strOfficalPathList):
        logging.debug('Invalid strOfficalPathList Number')
        return -1

    for strOfficalPath in strOfficalPathList:
        # Connect to network drive
        if '' == strUserName:
            strUserName = None

        if(0 != networkUtil.mountNetworkDrive(strImage, strOfficalPath,
                                              strUserName, strPassword)):
            logging.debug('Fail on mount network drive')
            return -1

        try:
            newestFile = ''
            currentFile = os.path.sep.join([strImage, strSubPath,
                                            r'%s\%d.txt' % (strBuildCheckFolder,
                                                          intOldBuildNum)])
            try:
                currentTime = os.path.getctime(currentFile)
            except:
                logging.debug(str('%s file %s can not be found under %s' %
                              (strBuildCheckFolder, currentFile,
                               os.path.join(strOfficalPath, strSubPath))))
                currentTime = 0

            for strFile in os.listdir(os.path.join(strImage, strSubPath,
                                                   strBuildCheckFolder)):
                fullPath = os.path.join(strImage, strSubPath,
                                        strBuildCheckFolder, strFile)
                if os.path.getctime(fullPath) > currentTime:
                    newestFile = strFile
                    currentTime = os.path.getctime(fullPath)

            if '' == newestFile:
                logging.info(str('No new build number under %s'
                                 % os.path.join(strOfficalPath, strSubPath)))
                newBuildNumber = 0
            else:
                newBuildNumber = int(newestFile[:newestFile.find('.txt')])
                logging.info(str('New build number is %d for %s'
                                 % (
                                     newBuildNumber, os.path.join(
                                         strOfficalPath,
                                                                 strSubPath))))

        finally:
            # Unmount network drive
            networkUtil.unmountNetworkDrive(strImage)
            if 0 == newBuildNumber:
                return 0
            elif (0 != retNewBuildNumber) and \
                 (retNewBuildNumber != newBuildNumber):
                logging.info(str('The latest build number of two '
                                'officialBuildPath does not match '
                                '(%d and %d)'
                                % (retNewBuildNumber, newBuildNumber)))
                return 0
            else:
                retNewBuildNumber = newBuildNumber

    return retNewBuildNumber


def check_new_build_by_folder(intOldBuildNum, strUserName, strPassword,
                strImage,
                strOfficalPathList=[
                    r'\\10.201.16.7\Uniclient\win32\v1.1\en'],
                strSubPath=r'\win32\v17.50\MUI_ASUS',
                strBuildCheckFolder='md5'):
    '''
        Check whether there is newer official build by verify all
        {build_Num}.txt in md5 folder under strOfficalPathList
        @param intOldBuildNum: current build number
        @param strUserName: The username for login to remote machine
        @param strPassword: The password for login to remote machine
        @param strImage: The specific driver (Ex: C:, D:) for network construction
        @param strOfficalPathList: the list contain offical build root path
        @param strSubPath: the list contain offical build sub path
        @param strBuildCheckFolder: the new build check folder (Ex: md5, check, ...)
        @return:
        -1 - Error
        0 - One of strOfficalPathList doesn't have newer build
        new build number - interger. new official build number.
    '''
    newBuildFolder = ''
    if 0 == len(strOfficalPathList):
        logging.debug('[check_new_build()]' +
                      '[Error] Invalid strOfficalPathList Number ')
        return -1

    for strOfficalPath in strOfficalPathList:
        # Connect to network drive
        if '' == strUserName:
            strUserName = None

        if(0 != networkUtil.mountNetworkDrive(strImage, strOfficalPath,
                                              strUserName, strPassword)):
            logging.debug('[check_new_build()]' +
                          '[Error] Fail on mount network drive')
            return -1

        try:
            newestFolder = funcGetLatestFolder(os.path.sep.join(strImage,
                                                        strSubPath))

            if '' == newestFolder:
                logging.info(str('[check_new_build()]' +
                                 ' No new build foler under %s'
                                 % os.path.join(strOfficalPath, strSubPath)))
                newBuildFolder = ''
            else:
                newBuildFolder = newestFolder
                logging.info(str('[check_new_build()]' +
                                 ' New build number is %s for %s'
                                 % (newBuildFolder,
                                    os.path.join(strOfficalPath, strSubPath))))
        finally:
            # Unmount network drive
            networkUtil.unmountNetworkDrive(strImage)
            if '' == newBuildFolder:
                return 0
            else:
                retNewBuildFolder = newBuildFolder

    return retNewBuildFolder


def funGetNewTaskList(floatOldTaskModDateTime, strUserName, strPassword,
                      strImage="U:", strOfficalPath="", strSubPath="",
                      strLocalTasksFolder="C:\\Tasks"):
    '''
        Check whether there is newer official build by verify all
        {build_Num}.txt in md5 folder under strOfficalPathList

        @param floatOldTaskModDateTime: current build number
        @param strUserName: The username for login to remote machine
        @param strPassword: The password for login to remote machine
        @param strImage: The specific driver (Ex: C:, D:) for network construction
        @param strOfficalPath: the list contain offical build root path
        @param strSubPath: the list contain offical build sub path

        @return:
        -1 - Error
        0 - One of strOfficalPathList doesn't have newer build
        new build number - interger. new official build number.
    '''
    floatNewestTime = float(0.0)
    if 0 == len(strOfficalPath):
        logging.debug('Invalid strOfficalPathList Number')
        return float(-1), []

    # Connect to network drive
    if '' == strUserName:
        strUserName = None

    if(0 != networkUtil.mountNetworkDrive(strImage, strOfficalPath,
                                          strUserName, strPassword)):
        logging.debug('Fail on mount network drive')
        return float(-1), []

    try:
        lstReturnTask = []
        lstNewTask = []
        floatCurrentTime = floatOldTaskModDateTime
        for strFile in os.listdir(os.path.sep.join([strImage, strSubPath])):
            fullPath = os.path.sep.join([strImage, strSubPath, strFile])
            if os.path.isfile(fullPath):
                floatFileDateTime = float(os.path.getmtime(fullPath))
                if  time.gmtime(floatFileDateTime) > \
                    time.gmtime(floatCurrentTime):
                    lstNewTask.append((time.gmtime(floatFileDateTime),
                                       floatFileDateTime, strFile))
                    # copy file
                    os.system("xcopy %s %s /e /y /r /I"
                              % (fullPath, strLocalTasksFolder))

        if len(lstNewTask) == 0:
            logging.info(str('No new build number under %s'
                             % os.path.sep.join([strOfficalPath, strSubPath])))
            floatNewestTime = float(0.0)
        else:
            lstNewTask.sort()
            #lstNewTask.reverse()
            # get the latest file ctime
            floatNewestTime = float(lstNewTask[-1][1])
            lstReturnTask = [os.path.sep.join([strLocalTasksFolder, strFile])
                             for (objDTime, floatCTime, strFile) in lstNewTask]
            logging.info(str('New build number is %.10f for %s'
                             % (floatNewestTime,
                                os.path.sep.join([strOfficalPath,
                                                  strSubPath]))))

    finally:
        # sleep 1 to avoid unmount error
        time.sleep(1)
        # Unmount network drive
        networkUtil.unmountNetworkDrive(strImage)
        if float(0.0) == floatNewestTime:
            return float(0.0), []
        else:
            return floatNewestTime, lstReturnTask


def funcUnzipFile(strFilePath, strDestPath, boolReplace=True):
    '''
        Unzip file to specific directory
        @param strFilePath: String. The fullpath of zip file.
        @param strDestPath: String. The destination directory to contain unzip files.
        @param boolReplace: Boolean. Replace previous file.
    '''
    logging.info('----funcUnzipFile()----')
    if not os.access(strFilePath, os.F_OK):
        logging.debug(str('[funcUnzipFile()] The file %s does not exist'
                      % (strFilePath)))
        return

    objStafService = crossPlatform.util.StafService()

    cmd = 'UNZIP ZIPFILE %s TODIRECTORY %s' % (strFilePath, strDestPath)
    if boolReplace:
        cmd = cmd + ' REPLACE'

    objStafService.callStafService('local', "ZIP", cmd)


def funGetSummaryFromMainHtml(strMainHtmlPath):
    '''
        Get required information for whole report from main.html
        @param strMainHtmlPath: String. The fullpath to main html
        @return: A list contain (IP,Total,Passes,Fails,Crashes,Elapsed Time)
        [Note]
        This function depend on reportUtil.py.
        If the main.html format is changed, this function may not work
    '''
    logging.info('----funGetSummaryFromMainHtml()----')
    if not os.access(strMainHtmlPath, os.F_OK):
        logging.debug('[funGetSummaryFromMainHtml()]' +
                      ' The file %s does not exist' % (strMainHtmlPath))
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
        if ('Total' in strLine) and ('Passes' in strLine) \
            and ('Fails' in strLine):
            for i in range(5):
                strLine = fMainHtml.readline()
                if (strLine.endswith('\n')):
                    strLine = strLine[:(len(strLine) - 1)]
                listResult.append(eliminateTag(strLine))
            break
        strLine = fMainHtml.readline()

    fMainHtml.close()
    return listResult


def funcGetFailedSummaryResult(strMainHtmlPath, dictMachineInfo, machineName):
    '''
    If main.html could not get required information,
    call this function to get partial information
    @param strMainHtmlPath: the main.html file path
    @param dictMachineInfo: the all client dictionary
    @param machineName: the target machine name
    @return:
        A list contain (IP,Total,Passes,Fails,Crashes,Elapsed Time)
    '''
    logging.info('----funcGetFailedSummaryResult()----')
    strIP = getIPfromMachineName(dictMachineInfo, machineName)
    if not os.access(strMainHtmlPath, os.F_OK):
        logging.debug('[funcGetFailedSummaryResult()]' +
                      ' The file %s does not exist' % (strMainHtmlPath))
        return [strIP, '0', '0', '0', '0', 'No main.html']

    listResult = []
    listResult.append(strIP)
    fMainHtml = open(strMainHtmlPath, 'r')
    strLine = fMainHtml.readline()

    while '' != strLine:
        if ('Pass' in strLine) and ('Fail' in strLine):
            strLine = eliminateTag(strLine).replace(' ', '')
            strLine = eliminateTag(strLine).replace('\n', '')
            strLine = eliminateTag(strLine).replace('\t', '')
            passIndex = strLine.find('Pass')
            failIndex = strLine.find('Fail')
            strPassNum = strLine[(passIndex + 5):failIndex]
            strFailNum = strLine[(failIndex + 5):]
            strTotalNum = str(int(strPassNum) + int(strFailNum))
            listResult.append(strTotalNum)
            listResult.append(strPassNum)
            listResult.append(strFailNum)
            listResult.append('Unavailable')
            break
        strLine = fMainHtml.readline()

    listResult.append('Not complete')

    return listResult


def eliminateTag(strInput):
    '''
        Remove any <xxx> from a string
        @param strInput: A string.
        @return: A string without <...>
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


def send_mail(strFrom, lstTo, lstCC, strSubject, strBodyFile, lstAttached,
               smtpServer='10.201.16.3',
               sender='uniclient_crossplatform@trend.com'):
    '''
        Send mail
        @param strFrom: Who send the mail (Shown in email)
        @param lstTo: The receiver list
        @param lstCC: The cc list
        @param strSubject: The Subject.
        @param strBodyFile: The strBody file path. (Both Relative and Full are acceptable)
        @param lstAttached: The attached file list
        @param smtpServer: the smtp server address
        @param sender: Who send the mail
    '''
    logging.info('----send_mail()----')
    if(0 == len(lstTo)):
        logging.debug('[Error]No receiver')
        return

    if not os.access(strBodyFile, os.F_OK):
        logging.debug(str('[Error]strBodyFile %s access fail' % (strBodyFile)))
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


def funcDeleteDirectory(deletePathList):
    '''
        Delete the path specified in the list
        @param deletePathList: the list contain path.
        @return:
            0 - Success
            NG: subprocess.Popen return code
    '''
    logging.info('----funcDeleteDirectory()----')

    iResult = 0
    for deletePath in deletePathList:
        if os.path.exists(deletePath):
            cmd = ['CMD', '/C', 'RMDIR', '/S', '/Q', deletePath]
            procObj = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                                       stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT)
            strReturnMsg = procObj.stdout.read()
            intReturnCode = procObj.wait()
            if intReturnCode != 0:
                logging.error(str('Delete directory %s Error.\n[Error Message]%s'
                              % (deletePath, strReturnMsg)))
                iResult = intReturnCode
        else:
            logging.info(str('The folder %s is not exist!' % deletePath))
    return iResult


def getIPfromMachineName(dictMachineInfo, strMachineName):
    '''
        Get machine information
        @param dictMachineInfo: A Dictionary contains
        {machineIP : [machineName,machineArchitecture,machinePlatform]}
        @param strMachineName: Machine Name
        @return:
        IP or 0
    '''
    ipList = dictMachineInfo.keys()
    for strIp in ipList:
        if dictMachineInfo[strIp][0] == strMachineName:
            return strIp
    return 0


def getMailProperty(strConfigFile='CrossPlatform_Config.ini'):
    '''
        Get Mail property from ini file
        @param strConfigFile: The config file name
        @return:
            Sender ,SmtpServer ,mailList ,ccList , AttachedFileList, Subject
    '''
    returnList = []
    objIni = crossPlatform.util.GetIniSetting(strConfigFile)

    returnList.append(objIni.getIniVar('Mail', 'Sender'))
    returnList.append(objIni.getIniVar('Mail', 'SmtpServer'))
    mailList = objIni.getIniVar('Mail', 'mailList')
    if isList(mailList):
        returnList.append(mailList)
    else:
        returnList.append([mailList])

    ccList = objIni.getIniVar('Mail', 'ccList')
    if isList(ccList):
        returnList.append(ccList)
    else:
        returnList.append([ccList])

    lstAttachedFile = objIni.getIniVar('Mail', 'AttachedFileList')
    if isList(lstAttachedFile):
        returnList.append(lstAttachedFile)
    else:
        returnList.append([lstAttachedFile])

    returnList.append(objIni.getIniVar('Mail', 'Subject'))
    return returnList


def isList(listTest):
    """
    Verify list type or not.
    @param listTest: verify object
    @return:
        True or False
    """
    if listTest.__class__ is list:
        return True
    else:
        return False


def funcGetLatestFolder(strPath):
    '''
        Get the latest folder name under the input path
        @param strPath: the specific path
        @return: The folder name or None (No any folder)
        [Note]
        This is only for windows
    '''
    print '----funcGetLatestFolder()----'
    curdir = os.getcwd()
    os.chdir(strPath)
    objFd = os.popen(r"dir /ad /od /b *.*")
    files = objFd.read().splitlines()
    objFd.close()
    os.chdir(curdir)
    if 0 == len(files):
        print 'funcGetLatestFolder() There is no directory'
        return None
    else:
        return files[-1]

if __name__ == '__main__':
    #dictMachineInfo, mapMachinePlatform, listMachineID = getMachineInfo( \
    #r"C:\STAF\lib\python\tis_oem\cross_platform\CrossPlatform_Config.ini")
    #funcLoadConfigure()
    #print funcFetchTask(["C:\\Task_0", "C:\\Task_1", "C:\\Task_2"])
    #x = funcGetLatestFolder("C:\\STAF\\lib\\python\\Ti_OEM")
    #print x
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
    #funcDeleteDirectory(['C:\\log','C:\\Donkey','C:\\tmp\\1071'])
    #unittest_check_new_build()
    print "End"
