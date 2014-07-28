"""
Automation main module, automatic check task queue, do task prepare,
do set task to central server then trigger testing after all machines
finish test case then collect test result and generate report send to
relative account.
"""
import os
import logging
import datetime
import time
import glob
import socket
import win32api
import crossPlatform.vmWorkStationUtil
import crossPlatform.esxi4_service as esxi4
import crossPlatform.crossPlatformUtil as cp_util
import crossPlatform.crossReportUtil as cp_reportUtil
import crossPlatform.util
import crossPlatform.append_host_info
from crossPlatform.errorCode import ErrorautoServerMain as ec_MMS
from tmstaf.multiPlatformRunner import CentralServer, ShellTask, PythonTask
from crossPlatform import zipUtil
import shutil


class ProcessTask(object):
    """
    Object for process task.
    """
    def __init__(self):
        self.strConfigFile = ""
        self.lstClientIp, self.lstCopyFolders = [], []
        #, self.lstCopyFile = [], [], []
        #self.lstToFolder = []
        self.objCentralServer, self.objReport = None, None
        self.strStartTime, self.strEndTime = "", ""
        #self.strTMSTAFIniFile = ""
        #self.strTaskID = ""
        self.strIniFile = ""
        self.strRunCaseTimeOut = ""
        self.listMachineID = []
        #, self.lstTestSuites = [], []
        self.listMachineName = []
        self.lstReportFolder = ["ZipREPORT"]
        self.strLabel = ""
        self.dictMachineInfo, self.mapMachinePlatform = None, None
        self.intRevertToleranceCount = 2
        self.strDownloadRoot, self.strCollectReportRoot = "", ""
        #self.strP4Cmd = ""
        self.lstDeployFolder = ["DeployZipPackage", "DeployROOT", "Tmp"]
        self.lstCreateFolder, self.lstPackage = [], []
        self.intFailNum = 0
        self.intRet = ec_MMS.SUCCESS
        self.strErrMsg = ''

        # build
        self.strBuildFolder = ""
        self.strBuildImage = ""
        self.strBuildPath = ""
        self.strBuildOEM = ""
        self.strBuildOfficalPathRoot, self.strBuildPassword = "", ""
        self.strBuildUserName = ""

        # network
        self.strNDCrossFilePath, self.strNDDriveLetter = "", ""
        self.strNDPassword, self.strNDUserName = "", ""

        # file server
        self.strFsFileServerName = ""
        self.strFsDriveLetter, self.strFsFileServerIP = "", ""
        self.strFsPassword = ""
        self.strFsSharedFolderRoot = "\\\\%s\\FileServerRoot"
        self.strFsUserName = "", ""
        #self.strFsLmUserName, self.strFsLmPassword = "", ""

        # client
        self.lstClientCopyFile = []
        #, self.lstClientIp = [], []
        self.strLinuxFolderInClient = r"/tmp/CrossPlatformScript"
        self.strWindowsFolderInClient = r"C:\CrossPlatformScript"
        self.strLinuxDownloadFolderInClient = r"/tmp/DeployPackage"
        self.strWindowsDownloadFolderInClient = r"C:\DeployPackage"
        self.strLinuxDefaultStafInClient = r"/usr/local"
        self.strWindowsDefaultStafInClient = "C:\\"
        self.strLinuxReportFolder = r"/usr/local/staf/result"
        self.strWindowsReportFolder = r"C:\tmp"

        # email
        self.lstCc, self.lstAttachFile, self.mailList = [], [], []
        self.strSubject, self.strFrom = "", ""

        # server static check
        self.lstSvrStaticChk = []

        self.strDownloadBuildFolder = ""

    def funcStartProcess(self, strTaskFile):
        """
        The process task main entry.
        @type strTaskFile: String
        @param strTaskFile: thte task file from repack system,
                            if None then use default file,
                            else set target task file.
        """
        if cp_util.funcGetValue('SCTM', 'Update_SCTM') == "Yes":
            strSCTMResult = cp_util.funcGetValue('SCTM', 'Result_File')
            if os.path.exists(strSCTMResult):
                os.remove(strSCTMResult)

        # initial variable - before do process need to reset pevious value
        self._funcSetErrMsg(ec_MMS.SUCCESS, '')
        self.lstSvrStaticChk = []

        if strTaskFile is not None:
            self.strConfigFile = strTaskFile
        else:
            self._funcSetErrMsg(
                ec_MMS.TASK_FILE_NONE, 'The task file is None!')

        # load configure setting
        if self.intRet == ec_MMS.SUCCESS:
            self._funcLoadConfigure(strTaskFile)

        # setup file server task test environment
        if self.intRet == ec_MMS.SUCCESS:
            self._funcPrepareAutomationSrvEnv()

        # download build
        if self.intRet == ec_MMS.SUCCESS:
            self._funcDownloadFromBuildSource()

        # download QA package from P4
        if self.intRet == ec_MMS.SUCCESS:
            self._funcDownloadScriptFromP4()

        # modify depends on OEM requriement
        if self.intRet == ec_MMS.SUCCESS:
            self._funcPrepareDeployPackage()

        # do file server static check
        if self.intRet == ec_MMS.SUCCESS:
            self._funcStaticCheckOnServer()

        # create deploy package
        if self.intRet == ec_MMS.SUCCESS:
            self._funcCreateDeployPackage()

        # revert client machine will decide the workable client list
        if self.intRet == ec_MMS.SUCCESS:
            self._funcRevertClientMachine()

        # Transfer download script and networkUtil.py to clients through STAF
        if self.intRet == ec_MMS.SUCCESS:
            self._funcPrepareClientEnv()

        # Trigger Client Test
        if self.intRet == ec_MMS.SUCCESS:
            self._funcTriggerClientTest()

        # collet result from all clients
        self._funcCollectResultFromClient()

        # wait all clients complete tasks then do the analyze result
        self._funcSummarizeResult()

        # upload report to tw-ets-fs
        self._funcUploadResultToReportSrv()

        # notify relative person by email
        self._funcSendReport()

    def _funcLoadConfigure(self, strConfigIni):
        """
        Load cross platform condifuration ini content.
        @type strConfigIni: String
        @param strConfigIni: the config ini file full path info
        """
        logging.info(str("load CrossPlatform configuration %s" % strConfigIni))
        cp_util.funcLoadConfigure(strConfigIni)

        ## [Global]
        #self.strTaskID       = cp_util.funcGetValue("Global", "Task_ID")
        #self.strDownloadRoot = cp_util.funcGetValue("Global", "downloadRoot")
        #self.lstDeployFolder = cp_util.funcGetValue("Global", "Deploy_Folder")
        #if crossPlatform.util.is_list(self.lstDeployFolder) == 0:
        #    self.lstDeployFolder = [self.lstDeployFolder]
        #self.strCollectReportRoot \
        #    = cp_util.funcGetValue("Global", "collect_reportRoot")
        #self.lstReportFolder = cp_util.funcGetValue("Global", "Report_Folder")
        #if crossPlatform.util.is_list(self.lstReportFolder) == 0:
        #    self.lstReportFolder = [self.lstReportFolder]
        ## [Build]
        self.strBuildOEM = cp_util.funcGetValue("Build", "OEM")
        self.strBuildFolder = cp_util.funcGetValue("Build", "Build_Number")
        self.strBuildOfficalPathRoot = cp_util.funcGetValue("Build",
                                                            "OfficalPath")
        self.strBuildImage = cp_util.funcGetValue("Build", "Image")
        self.strBuildUserName = cp_util.funcGetValue("Build", "UserName")
        self.strBuildPassword = cp_util.funcGetValue("Build", "Password")
        #self.strP4Cmd         = cp_util.funcGetValue("P4", "Cmd")

        ## [NetworkDrive]
        self.strNDCrossFilePath = cp_util.funcGetValue('NetworkDrive',
                                                       'CrossFilePath')
        self.strNDUserName = cp_util.funcGetValue('NetworkDrive', 'UserName')
        self.strNDPassword = cp_util.funcGetValue('NetworkDrive', 'Password')
        self.strNDDriveLetter = cp_util.funcGetValue('NetworkDrive',
                                                     'DriveLetter')

        ## [FileServer]
        self.strFsSharedFolderRoot = cp_util.funcGetValue('FileServer',
                                                          'SharedFolderRoot')
        self.strFsUserName = cp_util.funcGetValue('FileServer', 'UserName')
        self.strFsPassword = cp_util.funcGetValue('FileServer', 'Password')
        self.strFsDriveLetter = cp_util.funcGetValue('FileServer',
                                                     'DriveLetter')
        self.strFsFileServerName = socket.gethostname()
        self.strFsFileServerIP = socket.gethostbyname(socket.gethostname())
        self.strFsSharedFolderRoot = self.strFsSharedFolderRoot % (
            self.strFsFileServerIP)
        #self.strFsLmUserName = cp_util.funcGetValue('FileServer', 'LM_UserName')
        #self.strFsLmPassword = cp_util.funcGetValue('FileServer', 'LM_Password')

        # Testware Config
        #self.strTMSTAFIniFile = cp_util.funcGetValue('TestwareConfig',
        #                                         'TMSTAF_Ini_File')
        self.strIniFile = cp_util.funcGetValue('TestwareConfig', 'Ini_File')
        self.strRunCaseTimeOut = cp_util.funcGetValue(
            'TestwareConfig', 'Time_Out')

        self.lstPackage = cp_util.funcGetValue('QA_Package', 'Package_List')
        if crossPlatform.util.is_list(self.lstPackage) == 0:
            self.lstPackage = [self.lstPackage]

        self.dictMachineInfo, self.mapMachinePlatform, self.listMachineID = cp_util.getMachineInfo("", None)
        self.listMachineName = self.mapMachinePlatform.keys()

        # Task Label
        self.strLabel = cp_util.funcGetValue("Global", "Task_ID") + \
            cp_util.funcGetValue("Build", "Build_Number")
        self.strCollectReportRoot = os.path.sep.join(
            ["C:\\collect_report", self.strLabel])

        self.strDownloadRoot = os.path.sep.join(
            ["C:\\FileServerRoot", self.strLabel])
        self.strDownloadBuildFolder = os.path.sep.join(
            [self.strDownloadRoot, self.lstDeployFolder[2]])

        # [Client]
        __objDict = cp_util.funcGetSectionDict('Client')
        if 'Create_Folder' in __objDict:
            self.lstCreateFolder = __objDict['Create_Folder']
            if crossPlatform.util.is_list(self.lstCreateFolder) == 0:
                self.lstCreateFolder = [self.lstCreateFolder]
            del __objDict['Create_Folder']

        self.lstClientCopyFile = []
        if 'Copy_File' in __objDict:
            __lstCopyFile = __objDict['Copy_File']
            if crossPlatform.util.is_list(__lstCopyFile) == 0:
                __lstCopyFile = [__lstCopyFile]
            __lstToFolder = __objDict['To_Folder']
            if crossPlatform.util.is_list(__lstToFolder) == 0:
                __lstToFolder = [__lstToFolder]
            for intIndex in range(len(__lstCopyFile)):
                self.lstClientCopyFile.append([__lstCopyFile[intIndex],
                                               __lstToFolder[intIndex]])
        else:
            for __strKey in __objDict:
                __lstPair = __objDict[__strKey]
                self.lstClientCopyFile.append([__lstPair[0], __lstPair[1]])

        # email
        self.mailList = cp_util.funcGetValue('EMail', 'maillist')
        if crossPlatform.util.is_list(self.mailList) == 0:
            self.mailList = [self.mailList]

        self.strSubject = cp_util.funcGetValue('EMail', 'Subject')
        self.strFrom = cp_util.funcGetValue('EMail', 'From')
        self.lstCc = cp_util.funcGetValue('EMail', 'CC')
        if crossPlatform.util.is_list(self.lstCc) == 0:
            self.lstCc = [self.lstCc]

        self.lstAttachFile = cp_util.funcGetValue('EMail', 'AttachFile')
        if self.lstAttachFile != '':
            if crossPlatform.util.is_list(self.lstAttachFile) == 0:
                self.lstAttachFile = [self.lstAttachFile]

    def _funcPrepareAutomationSrvEnv(self):
        """
        Setup File Server relative C:\\FileServerRoot and C:\\collect_report task test environment.
        There are include clean and create relative folders.
        """
        ## check the must folders, if not exist then create it
        __lstMandatoryFolder = ["C:\\FileServerRoot", "C:\\collect_report"]
        for __strFolder in __lstMandatoryFolder:
            if not os.path.exists(__strFolder):
                logging.info("create folder [%s]" % __strFolder)
                os.system(str("md %s" % __strFolder))

        ## Clean previous folder contain but reserve 6 newest tasks
        strTarget = os.path.join(self.strFsSharedFolderRoot, '*')
        lstFolder = glob.glob(strTarget)
        lstBuf = []
        for item in lstFolder:
            lstBuf.append((os.path.getctime(item), item))
        lstBuf.sort()
        lstBuf.reverse()
        lstFolder = []
        for item in lstBuf[4:]:
            lstFolder.append(item[1])
        logging.info(str('clean previous task data [%s]' % str(lstFolder)))
        if len(lstFolder) > 0:
            cp_util.funcDeleteDirectory(lstFolder)
        #
        lstEnvCreateFolder = []
        lstEnvDeleteFolder = []
        ## process deploy relative folders
        for strFolder in self.lstDeployFolder:
            strEnvFolder = os.path.sep.join([self.strDownloadRoot, strFolder])
            lstEnvCreateFolder.append(strEnvFolder)
        lstEnvDeleteFolder.append(self.strDownloadRoot)

        ## process collect report relative folders
        for strFolder in self.lstReportFolder:
            strEnvFolder = os.path.sep.join(
                [self.strCollectReportRoot, strFolder])
            lstEnvCreateFolder.append(strEnvFolder)
        lstEnvCreateFolder.append(os.path.sep.join(
            [self.strCollectReportRoot, self.strBuildFolder]))
        lstEnvDeleteFolder.append(self.strCollectReportRoot)
        #
        cp_util.funcDeleteDirectory(lstEnvDeleteFolder)
        logging.info(str('deletePathList = %s' % (lstEnvDeleteFolder)))
        #
        # create folder
        for strFolder in lstEnvCreateFolder:
            logging.info(str("create folder = %s" % strFolder))
            os.system(str('md %s' % strFolder))

    def _funcDownloadFromBuildSource(self):
        """
        Download target build.
        Because didn't really got the build, so just do the build target folder has file.
        """
##        raise NotImplementedError('%s._funcDownloadFromBuildSource()'+\
##                                  ' should be implemented!'% \
##                self.__class__.__name__)

        __strDownloadTmpFolder = os.path.sep.join(
            [self.strDownloadRoot, 'Tmp'])
        logging.info(str("download build %s from %s to %s" %
                     (self.strBuildImage,
                      self.strBuildOfficalPathRoot,
                      __strDownloadTmpFolder)))
        if cp_util.funcCopyFileRemote(self.strBuildOfficalPathRoot,
                                      __strDownloadTmpFolder,
                                      self.strBuildUserName,
                                      self.strBuildPassword,
                                      self.strNDDriveLetter,
                                      fileName=self.strBuildImage) != 0:
            logging.error('Download CD image fail')
            self.intRet = ec_MMS.DOWNLOAD_BUILD_FAIL
            self.strErrMsg = "Download build  %s from %s to %s fail" % \
                             (self.strBuildImage,
                              self.strBuildOfficalPathRoot,
                              __strDownloadTmpFolder)

    def _funcDownloadScriptFromP4(self):
        """
        Download QA package from P4
        """
        __strP4Cmd = cp_util.funcGetValue("P4", "Cmd")
        logging.info(str('Download STAF lib and testsuites from P4...%s' %
                         (__strP4Cmd)))
        if __strP4Cmd is not None:
            os.system(__strP4Cmd)

    def _funcPrepareDeployPackage(self):
        """
        modify ini depends on OEM requriement
        """
        # modify testsuites depends on Task ini settings
        __lstTestSuites = cp_util.funcGetValue('TestwareConfig', 'TestSuites')
        if crossPlatform.util.is_list(__lstTestSuites) == 0:
            __lstTestSuites = [__lstTestSuites]
        strVal = ''
        for item in __lstTestSuites:
            if strVal == '':
                strVal = item
            else:
                strVal = strVal + ',' + item
        win32api.WriteProfileVal("TestwareConfig", 'TestSuites', strVal,
                                 cp_util.funcGetValue('TestwareConfig', 'TMSTAF_Ini_File'))

    def _funcCreateDeployPackage(self):
        """
        Create client deploy package
        """
        # Copy P4 QA TMSTAF Suite lib and testsuites
        strQASuiteDest = os.path.sep.join([self.strDownloadRoot, 'DeployROOT'])
        logging.info(str('strQASuiteDest = %s' % (strQASuiteDest)))
        for item in self.lstPackage:
            os.system('xcopy "C:\\STAF\\%s" "' % item + os.path.sep.join([strQASuiteDest, 'staf', item]) + '" /E /Y /I /R /H')
        #
        __strDeployFolder = "Deploy"
        os.system(str('mkdir "%s\\%s"' % (strQASuiteDest, __strDeployFolder)))
        logging.info(str('xcopy %s\\Tmp\\*.* "%s\\%s" /E /Y /I /R /H' % (
            self.strDownloadRoot, strQASuiteDest, __strDeployFolder)))
        os.system(str('xcopy %s\\Tmp\\*.* "%s\\%s" /E /Y /I /R /H') %
                  (self.strDownloadRoot, strQASuiteDest, __strDeployFolder))
        # copy Test Data to 'Deploy' folder
        os.system(str('xcopy "C:\\STAF\\test data" "%s\\%s" /E /Y /I /R /H')
                  % (strQASuiteDest, __strDeployFolder))
        # Package Deploy Folder into one package for client use.
        objStafService = crossPlatform.util.StafService()
        cmd = 'ADD ZIPFILE %s DIRECTORY %s RECURSE RELATIVETO %s' % (os.path.sep.join([self.strDownloadRoot, 'DeployZipPackage', 'DEPLOY.ZIP']),
                                                                     os.path.sep.join([self.strDownloadRoot, 'DeployROOT']),
                                                                     os.path.sep.join([self.strDownloadRoot, 'DeployROOT']))
        logging.info(cmd)
        objStafService.callStafService('LOCAL', "ZIP", cmd)

    def funcRevertVm(self, arrIPOK, arrIPNG, arrHost, strMachineIP, strHostIp, strImagePath, strSnapshotName):
        """
        """
        from crossPlatform.errorCode import ErrorautoServerMain as ec_MMS
        logging.info("the running host ip: %s" % arrHost.value)
        logging.info("the machine ip %s, host ip %s, image path %s and snapshot name %s" % (strMachineIP, strHostIp, strImagePath, strSnapshotName))
        intRet = crossPlatform.vmWorkStationUtil.revertVmByStaf(
            strHostIp, strImagePath, strSnapshotName)
        if intRet == ec_MMS.SUCCESS:
            if arrIPOK.value == '':
                arrIPOK.value = strMachineIP
            else:
                arrIPOK.value = arrIPOK.value + ',' + strMachineIP
            logging.info("ok ip list: %s" % arrIPOK.value)
        else:
            if arrIPNG.value == '':
                arrIPNG.value = strMachineIP
            else:
                arrIPNG.value = arrIPNG.value + ',' + strMachineIP
            logging.info("ng ip list: %s" % arrIPNG.value)

    def funcRevertLMVm(self, arrIPOK, arrIPNG, strMachineIP, strMachineID, strServerIp, strAccount, strPassword):
        """
        """
        from crossPlatform.errorCode import ErrorautoServerMain as ec_MMS
        logging.info("the machine ip %s and id %s" % (strMachineIP,
                                                      strMachineID))
        intRet = cp_util.funcRevertVirtualMachine(strMachineIP,
                                                  strMachineID, strServerIp, strAccount, strPassword)
        if intRet == ec_MMS.SUCCESS:
            if arrIPOK.value == '':
                arrIPOK.value = strMachineIP
            else:
                arrIPOK.value = arrIPOK.value + ',' + strMachineIP
            logging.info("ok ip list: %s" % arrIPOK.value)
        else:
            if arrIPNG.value == '':
                arrIPNG.value = strMachineIP
            else:
                arrIPNG.value = arrIPNG.value + ',' + strMachineIP
            logging.info("ng ip list: %s" % arrIPNG.value)

    def funcRevertESXi4Vm(self, arrIPOK, arrIPNG, strMachineIP, strVmName, strHostIp, strAccount, strPassword, strSnapshotName):
        from crossPlatform.errorCode import ErrorautoServerMain as ec_MMS
        logging.info("the vm name %s, host ip %s, and snapshot name %s" %
                     (strVmName, strHostIp, strSnapshotName))
        intRet = cp_util.funcRevertESXi4(strVmName, strHostIp,
                                         strAccount, strPassword, strSnapshotName)
        if intRet == ec_MMS.SUCCESS:
            if arrIPOK.value == '':
                arrIPOK.value = strMachineIP
            else:
                arrIPOK.value = arrIPOK.value + ',' + strMachineIP
            logging.info("ok ip list: %s" % arrIPOK.value)
        else:
            if arrIPNG.value == '':
                arrIPNG.value = strMachineIP
            else:
                arrIPNG.value = arrIPNG.value + ',' + strMachineIP
            logging.info("ng ip list: %s" % arrIPNG.value)

    def _funcRevertClientMachine(self):
        """
        Revert Machine List before do test
            1. first process target client list.
                if belongs host vm push to host vm queue
                if belongs LM vm push to LM vm queue
                if belogns real machine just revert it
            2. Then do host vm revert in parallel depends host
            3. Then do LM vm revert in sequence in max 3 hours period.
            4. process final OK and NG result
        """
        from crossPlatform.errorCode import ErrorautoServerMain as ec_MMS
        from multiprocessing.sharedctypes import Value, Array
        from multiprocessing import Process, Lock

        arrHost = Array('c', len(self.dictMachineInfo) * 16)
        arrHost.value = ''
        arrIPOK = Array('c', len(self.dictMachineInfo) * 16)
        arrIPOK.value = ''
        arrIPNG = Array('c', len(self.dictMachineInfo) * 16)
        arrIPNG.value = ''
        _dictTmp = {}
        lstOKIP = []
        lstNGIP = []
        lstProcess = []
        dictQueue = {}
        for strMachineIP in self.dictMachineInfo:
            strMachineID = self.dictMachineInfo[strMachineIP][3]
            if strMachineID == '0':   # means the real machine
                intRet = cp_util.funcRevertRealMachine(strMachineIP)
                if intRet == ec_MMS.SUCCESS:
                    lstOKIP.append(strMachineIP)
                else:
                    lstNGIP.append(strMachineIP)
            elif strMachineID == '1':   # means the VM workstation
                strHostIp = self.dictMachineInfo[strMachineIP][4]
                strImagePath = self.dictMachineInfo[strMachineIP][5]
                strSnapshotName = self.dictMachineInfo[strMachineIP][6]
                logging.info(str('Revert VM HostIp:%s Image:%s Snapshotname %s'
                                 % (strHostIp, strImagePath, strSnapshotName)))
                p = Process(target=self.funcRevertVm, args=(arrIPOK, arrIPNG, arrHost, strMachineIP, strHostIp, strImagePath, strSnapshotName,))
                if strHostIp in dictQueue:
                    intStatus, objProcess, strIp, intTimeCount, lstProc, intRetry = dictQueue[strHostIp]
                    lstProc.append((p, strMachineIP))
                else:
                    dictQueue[strHostIp] = 0, None, '', 0, [
                        (p, strMachineIP)], 0
            elif strMachineID == '2':  # ESXi4.0 client machine
                strVmName = self.dictMachineInfo[strMachineIP][0]
                strSnapshotName = self.dictMachineInfo[strMachineIP][4]
                strEsxServer = self.dictMachineInfo[strMachineIP][5]
                strHostIp = cp_util.funcGetValue(strEsxServer, 'ServerIp')
                strAccount = cp_util.funcGetValue(strEsxServer, 'Account')
                strPassword = cp_util.funcGetValue(strEsxServer, 'Password')
                logging.info("strMachineID : %s ,strVmName : %s ,strSnapshotName : %s , strEsxServer : %s , ServerIp : %s, Account : %s , Password : %s"
                             % (strMachineID, strVmName, strSnapshotName, strEsxServer, strHostIp, strAccount, strPassword))
                p = Process(target=self.funcRevertESXi4Vm, args=(arrIPOK, arrIPNG, strMachineIP, strVmName, strHostIp, strAccount, strPassword, strSnapshotName))
                if strHostIp in dictQueue:
                    intStatus, objProcess, strIp, intTimeCount, lstProc, intRetry = dictQueue[strHostIp]
                    lstProc.append((p, strMachineIP))
                else:
                    dictQueue[strHostIp] = 0, None, '', 0, [
                        (p, strMachineIP)], 0
            else:   # lab manager client
                strServerIp = cp_util.funcGetValue("LabManagerSrv", "ServerIp")
                strAccount = cp_util.funcGetValue("LabManagerSrv", "Account")
                strPassword = cp_util.funcGetValue("LabManagerSrv", "Password")
                p = Process(target=self.funcRevertLMVm, args=(arrIPOK, arrIPNG, strMachineIP, strMachineID, strServerIp, strAccount, strPassword,))
                dictQueue[strMachineIP] = 0, None, '', 0, [
                    (p, strMachineIP)], 0

        while dictQueue != {}:
            for itemkey in dictQueue:
                intStatus, objProcess, strIp, intTimeCount, lstProc, intRetry = dictQueue[itemkey]
                if intStatus == 0:
                    if len(lstProc) == 0:  # means tasks are all finished
                        intStatus = -1
                        dictQueue[itemkey] = intStatus, objProcess, strIp, intTimeCount, lstProc, intRetry
                    else:  # means there is still task to do
                        objProcess, strIp = lstProc.pop()
                        objProcess.start()
                        intStatus = 1
                        intTimeCount = 0
                        dictQueue[itemkey] = intStatus, objProcess, strIp, intTimeCount, lstProc, intRetry
                        #avoid triggering revert at the same time, it will result lab manager crash
                        time.sleep(30)
                elif intStatus == 1:  # means running status
                    # check process stop
                    if not objProcess.is_alive():
                        logging.info("The machine ip %s completed!" % strIp)

                        strMachineID = self.dictMachineInfo[strIp][3]
                        # process is finished, but need to check status is successful or not. Only support rerun on lab manager client.
                        if (strIp in arrIPNG.value) and (intRetry <= self.intRevertToleranceCount) and not strMachineID in ["0", "1", "2"]:
                            # rerun once more
                            logging.info("Revert process return status is error, rerun %d/%d" % (intRetry, self.intRevertToleranceCount))
                            intRetry = intRetry + 1
                            strMachineID = self.dictMachineInfo[strIp][3]
                            objProcess = Process(target=self.funcRevertLMVm, args=(arrIPOK, arrIPNG, strIp, strMachineID, strServerIp, strAccount, strPassword,))
                            dictQueue[itemkey] = 2, objProcess, strIp, 0, lstProc, intRetry
                            # update ipNG list
                            lstTmp = arrIPNG.value.split(',')
                            lstTmp.remove(strIp)
                            logging.info("after remove ip %s NG ip list %s" %
                                         (strIp, lstTmp))
                            logging.info("before remove ip %s NG ip list %s" % (strIp, arrIPNG.value))
                            arrIPNG.value = ''
                            for itemNG in lstTmp:
                                if arrIPNG.value == '':
                                    arrIPNG.value = itemNG
                                else:
                                    arrIPNG.value = arrIPNG.value + ',' + itemNG
                        else:   # finish successfully or exceed retry limit, will be clean from dictQueue later
                            dictQueue[itemkey] = 0, None, '', 0, lstProc, intRetry
                    else:
                        if intTimeCount < 6 * 30:    # time out is 6 *30 *10   seconds
                            intTimeCount = intTimeCount + 1
                            dictQueue[itemkey] = intStatus, objProcess, strIp, intTimeCount, lstProc, intRetry
                        else:   # timeout, terminate subprocess
                            logging.error("time out to terminate machine ip %s" % strIp)
                            objProcess.terminate()
                elif intStatus == 2:  # it means this task has failed once
                    objProcess.start()
                    intStatus = 1
                    intTimeCount = 0
                    dictQueue[itemkey] = intStatus, objProcess, strIp, intTimeCount, lstProc, intRetry
            # after every for loop finishes, wait 10 seconds
            time.sleep(10)

            dictTemp = {}
            for itemkey in dictQueue:
                intStatus, objProcess, strIp, intTimeCount, lstProc, intRetry = dictQueue[itemkey]
                if intStatus != -1:  # only keep unfinish process stack
                    dictTemp[itemkey] = intStatus, objProcess, strIp, intTimeCount, lstProc, intRetry
                    logging.info("the running client %d, %s, %d, %s" % (intStatus, strIp, intTimeCount, lstProc))
            dictQueue = dictTemp

        if arrIPOK.value != '':
            lstTmp = arrIPOK.value.split(',')
            lstOKIP = lstOKIP + lstTmp
        logging.info("the final ok list %s" % lstOKIP)
        for strItemIP in lstOKIP:
            #check client's os and record it, dictMachineInfo[strIP][-1] will record "windows" or "linux"
            objStafService = crossPlatform.util.StafService()
            cmd = "resolve system string {STAF/Config/OS/Name}"
            objStafService.callStafService(strItemIP, "VAR", cmd)
            if "Win" in objStafService.resultContent:
                self.dictMachineInfo[strItemIP].append("windows")
            elif "Linux" in objStafService.resultContent:
                self.dictMachineInfo[strItemIP].append("linux")
            _dictTmp[strItemIP] = self.dictMachineInfo[strItemIP]

        #OK list for later central server used
        self.lstClientIp = lstOKIP

        if arrIPNG.value != '':
            lstTmp = arrIPNG.value.split(',')
            lstNGIP = lstNGIP + lstTmp
        logging.info("the final ng list %s" % lstNGIP)
        for strItemIP in lstNGIP:
            self.funcAddSvrStaticChkResult(self.dictMachineInfo[strItemIP][0], str('%s %s %s Revert Fail!' % (strItemIP, self.dictMachineInfo[strItemIP][1], self.dictMachineInfo[strItemIP][2])))
        logging.info("Final self.dictMachineInfo:%s", _dictTmp)
        self.dictMachineInfo = _dictTmp

    def _funcDownloadPackage(self, strClientIp):
        """
        Download deploy package to each client.
        @type strClientIp: String
        @param strClientIp: the download package to client's IP value.
        """
        objStafService = crossPlatform.util.StafService()
        strFrom = os.path.sep.join(
            [self.strDownloadRoot, 'DeployZipPackage', 'DEPLOY.ZIP'])
        strTo = "C:\\DeployPackage\\"
        cmd = "COPY FILE %s TODIRECTORY %s TOMACHINE %s" % (
            strFrom, strTo, strClientIp)
        logging.info(str("copy file %s to VM %s folder %s" % (
            strFrom, strTo, strClientIp)))
        objStafService.callStafService("local", "FS", cmd)

    def _funcPrepareClientEnv(self):
        """
        To setup client environment for test.
        There are include createa folder, copy files and
        copy deploy package to clients.
        """
        intOneMin = 60
        logging.info('Transfer download script to clients through STAF')
        ##objStafService = crossPlatform.util.StafService()
        # initial multithread central server for client environment setup
        self._funcPreparationCentralServerInit()
        for strHost, objClient in self.objPreparationCentralServer.getAllTestMachine():
            ## prepare 1: create folder on clent
            for strFolder in self.lstCreateFolder:
                logging.info(str("create folder %s in VM %s" %
                                 (strFolder, strHost)))
                lstArgs = [strHost, strFolder]
                objClient.addServerTask(PythonTask('crossPlatform.crossPlatformUtil', 'funcCreateFolder', lstArgs))

            ## prepare 2: copy specific files to client for later use
            for lstItem in self.lstClientCopyFile:
                logging.info(str("copy file from %s to %s folder in client %s" % (lstItem[0], lstItem[1], strHost)))

                if self.dictMachineInfo[strHost][-1] == "windows":
                    strScriptDownloadWorkDir = self.strWindowsFolderInClient
                    strPathSplitSymbol = "\\"
                elif self.dictMachineInfo[strHost][-1] == "linux":
                    strScriptDownloadWorkDir = self.strLinuxFolderInClient
                    strPathSplitSymbol = "//"
                else:
                    strScriptDownloadWorkDir = self.strLinuxFolderInClient
                    strPathSplitSymbol = "//"
                    strTo = self.strLinuxDownloadFolderInClient

                strRemoteFileName = lstItem[1] + strPathSplitSymbol + \
                    os.path.basename(lstItem[0])
                lstArgs = [strHost, lstItem[0], lstItem[1], strRemoteFileName,
                           strScriptDownloadWorkDir]
                objClient.addServerTask(PythonTask('crossPlatform.crossPlatformUtil', 'funcCopyFileMd5Verify', lstArgs))

            ## prepare 3: add Automation Server name and ip into client hosts file
            ##            for staf connection speeding up.
            strAppendHostInfoCmd = ['python',
                                    'append_host_info.py',
                                    'setNetworkHost',
                                    self.strFsFileServerName,
                                    self.strFsFileServerIP]
            if self.dictMachineInfo[strHost][-1] == "windows":
                __objShellTask = ShellTask(strAppendHostInfoCmd,
                                           self.strWindowsFolderInClient)
                logging.info(str('do append automation server info into hosts file [%s] in %s [%d]' %
                             (strAppendHostInfoCmd, self.strWindowsFolderInClient, __objShellTask.intTimeout)))
            elif self.dictMachineInfo[strHost][-1] == "linux":
                __objShellTask = ShellTask(strAppendHostInfoCmd,
                                           self.strLinuxFolderInClient)
                logging.info(str('do append automation server info into hosts file [%s] in %s [%d]' %
                             (strAppendHostInfoCmd, self.strLinuxFolderInClient, __objShellTask.intTimeout)))
            else:
                logging.error("Unknown OS %s in client %s" % (self.dictMachineInfo[strHost][-1], strHost))
                logging.error("Try to use linux path")
                __objShellTask = ShellTask(strAppendHostInfoCmd,
                                           r"/tmp/CrossPlatformScript")
                logging.info(str('do append automation server info into hosts file [%s] in %s [%d]' %
                             (strAppendHostInfoCmd, self.strLinuxFolderInClient, __objShellTask.intTimeout)))
            objClient.addTask(__objShellTask)

        logging.info('Execute preparation task on each client by multithread method')
        self.objPreparationCentralServer.run()

        ## prepare 4: add Automation Client name and ip into server hosts file
        ## this step can not be executed in multithread becasue there is no mutex to protect accessing
        ## host file concurrently

        for strClientIp in self.dictMachineInfo:
            try:
                #set host ip in server, however, it will fail on linux client
                lstHost = socket.gethostbyaddr(strClientIp)
                crossPlatform.append_host_info.setNetworkHost(
                    lstHost[0], strClientIp)
            except:
                pass
        logging.info('Execute preparation task on each client by single method')

    def _funcAddClientTask(self):
        """
        Add tasks to clients
        """
        #
        logging.info('Add tasks to each machine....')
        intOneMin = 60
        #strDownloadWorkDir = "C:\\CrossPlatformScript"
##        strDownloadDeployPackageCmd = ['Python', 'util_cross_client.py',
##                                       'download_Unzip', 'DeployZipPackage',
##                                       "C:\\DeployPackage",
##                                       self.strFsSharedFolderRoot,
##                                       self.strFsUserName,
##                                       self.strFsPassword,
##                                       self.strFsDriveLetter]

        #lstCmd = [r'runTest.bat', '--bypass-syntax-check']
        strProjectProcessTaskClass = cp_util.funcGetValue(
            'Global', 'ProjectProcessTaskClass')

        for strHost, objClient in self.objCentralServer.getAllTestMachine():
            logging.info(str('process host [%s] task start!' % strHost))
            # copy deploy.zip from server to client
            strFrom = os.path.sep.join([self.strDownloadRoot,
                                        'DeployZipPackage', 'DEPLOY.ZIP'])
            if self.dictMachineInfo[strHost][-1] == "windows":
                strScriptDownloadWorkDir = self.strWindowsFolderInClient
                strTo = self.strWindowsDownloadFolderInClient
                strWorkingFolder = "%s\\STAF\\testsuites\\%s" % (self.strWindowsDefaultStafInClient, strProjectProcessTaskClass.rsplit('.', 2)[0].replace('.', '\\'))
                lstArgs = [strHost, strFrom, strTo, os.path.join(strTo,
                                                                 'DEPLOY.ZIP'), strScriptDownloadWorkDir]
                lstArgs2 = [strHost, os.path.join(strTo, 'DEPLOY.ZIP'),
                            self.strWindowsDefaultStafInClient]
                lstCmd = [r'runTest.bat', '--bypass-syntax-check']
                lstArgs3 = [strHost, lstCmd, strWorkingFolder,
                            int(self.strRunCaseTimeOut), 600, 1]
            elif self.dictMachineInfo[strHost][-1] == "linux":
                strScriptDownloadWorkDir = self.strLinuxFolderInClient
                strTo = self.strLinuxDownloadFolderInClient
                strWorkingFolder = r"%s/staf/testsuites/%s" % (self.strLinuxDefaultStafInClient, strProjectProcessTaskClass.rsplit('.', 2)[0].replace('.', '//'))
                lstArgs = [strHost, strFrom, strTo, strTo +
                           r'/DEPLOY.ZIP', strScriptDownloadWorkDir]
                lstArgs2 = [strHost, strTo + r'/DEPLOY.ZIP',
                            self.strLinuxDefaultStafInClient]
                lstCmd = [r'./runTest.sh']
                lstArgs3 = [strHost, lstCmd, strWorkingFolder,
                            int(self.strRunCaseTimeOut), 600, 1]
            else:
                strScriptDownloadWorkDir = self.strLinuxFolderInClient
                strTo = self.strLinuxDownloadFolderInClient
                strWorkingFolder = r"%s/staf/testsuites/%s" % (self.strLinuxDefaultStafInClient, strProjectProcessTaskClass.rsplit('.', 2)[0].replace('.', '//'))
                lstArgs = [strHost, strFrom, strTo, strTo +
                           r'/DEPLOY.ZIP', strScriptDownloadWorkDir]
                lstArgs2 = [strHost, strTo + r'/DEPLOY.ZIP',
                            self.strLinuxDefaultStafInClient]
                lstCmd = [r'./runTest.sh']
                lstArgs3 = [strHost, lstCmd, strWorkingFolder,
                            int(self.strRunCaseTimeOut), 600, 1]

##            strTo = "C:\\DeployPackage"
            logging.info(str("copy file %s to VM %s folder %s" %
                             (strFrom, strHost, strTo)))
##            objClient.addTask(ShellTask(['staf', self.strFsFileServerIP, 'FS', 'COPY', 'FILE', strFrom, 'TODIRECTORY', strTo, 'TOMACHINE', strHost],''), intOneMin*30)
##            lstArgs = [strHost, strFrom, strTo, os.path.join(strTo, 'DEPLOY.ZIP'), strScriptDownloadWorkDir]
            objClient.addServerTask(PythonTask('crossPlatform.crossPlatformUtil', 'funcCopyFileMd5Verify', lstArgs))
            # unzip deploypackage
            objClient.addServerTask(PythonTask('crossPlatform.crossPlatformUtil', 'funcRemoteUnzip', lstArgs2))
            # run TMSTAF in client
            logging.info(str('add servertask [%s]' % lstArgs3))
            objClient.addServerTask(cp_util.CAllowFailServerTask(
                'tmstaf.util', 'runRemoteTmstaf', lstArgs3))

    def _funcCentralServerRun(self):
        """
        Start server central run
        Ececute task on each client by multithread method
        """
        logging.info('Ececute task on each client by multithread method')
        self.objCentralServer.run()

    def _funcSummarizeResult(self):
        """
        """
        self._funcAnalyzeResult()

        # proces report header
        self._funcReportHeader()

    def _funcAnalyzeResult(self):
        """
        Wait all clients complete tasks then do the analyze result
        Analyze the test result.
        """
        #self.strCollectReportRoot = r'C:\collect_report\672214672214'
        #self.listMachineName = ['Win7 64 EN-US','WinXP 32 EN-US']
        #self.lstReportFolder = ["ZipREPORT"]

        self.objReport = cp_reportUtil.CrossSummaryReport()
        self.intFailNum = 0
        self.lstCopyFolders = []
        dicFailSummary = {}
        dictotaltestcase = {}
        for machineName in self.listMachineName:
            for strReportFolder in self.lstReportFolder:
                zipPath = '%s\\%s\\%s.zip' % (self.strCollectReportRoot,
                                              strReportFolder, machineName)
                if not os.access(zipPath, os.F_OK):
                    self.objReport.addFailedMachine(machineName,
                                                    self.mapMachinePlatform[machineName])
                    self.intFailNum = self.intFailNum + 1
                else:
                    strUnzipDestPath = (str('%s\\%s' %
                                            (self.strCollectReportRoot,
                                             self.strBuildFolder) +
                                            '\\%s')) % (machineName)
                    cp_util.funcUnzipFile(zipPath, strUnzipDestPath)
                    strFolderName = \
                        cp_util.funcGetLatestFolder(strUnzipDestPath)
                    if None == strFolderName:
                        logging.debug(str('There is no unzip folder'
                                          'under %s' % (strUnzipDestPath)))
                        self.objReport.addFailedMachine(machineName,
                                                        self.mapMachinePlatform[machineName])
                        self.intFailNum = self.intFailNum + 1
                        continue
                    strMainHtmlPath = os.sep.join([strUnzipDestPath,
                                                   strFolderName,
                                                   'main.html'])
                    try:
                        (strIP, intNumOfCase, intPass,
                         intFail, intCrash, intElapsedTime,
                         intDevelopingCasePassNum, intDevelopingCaseFailNum) \
                            = cp_util.funGetSummaryFromMainHtml(strMainHtmlPath)

                    except (ValueError, TypeError):
                        (strIP, intNumOfCase, intPass, intFail, intCrash,
                         intElapsedTime, intDevelopingCasePassNum, intDevelopingCaseFailNum
                         ) = cp_util.funcGetFailedSummaryResult(
                             strMainHtmlPath,
                             self.dictMachineInfo,
                             machineName)

                    for strRoot, lstDirectory, lstFile in os.walk(strUnzipDestPath):
                        for strFile in lstFile:
                            if strFile.split('.')[-1] == 'log':
                                if(strFile.split('.')[0] in dictotaltestcase):
                                    pass
                                else:
                                    dictotaltestcase[strFile.split('.')[0]] = 'Pass'

                    strComputerName = \
                        (str(r'<a href="%s\%s\report\%s' % (self.strNDCrossFilePath,
                                                            self.strBuildOEM,
                                                            self.strBuildFolder) +
                         r'\%s\%s\index.html">%s</a>')) % (machineName,
                                                           strFolderName,
                                                           machineName)
                    self.objReport.addResultSummary(strComputerName,
                                                    self.mapMachinePlatform[machineName], strIP,
                                                    intNumOfCase, intPass, intFail, intCrash,
                                                    intElapsedTime, int(intPass) - intDevelopingCasePassNum, int(intFail) - intDevelopingCaseFailNum)
                    self.lstCopyFolders.append(
                        os.sep.join([self.strBuildFolder, machineName,
                                     strFolderName]))
                    #get fail case information from main.html
                    dicFailCases = cp_util.getFailedDictFromMainHtml(
                        strMainHtmlPath)

                    if dicFailCases:
                        cp_util.updateFailSummary(dicFailSummary,
                                                  dicFailCases, machineName)
                        for key in dicFailCases:
                            key = key.split("\\")[1]
                            dictotaltestcase[key] = 'Fail'

        #get fail information from fail summary
        lstFailSummary = sorted(dicFailSummary.items(
        ), key=lambda x: (x[0]), reverse=False)
        lstFailSummary = sorted(
            lstFailSummary, key=lambda x: (x[1]), reverse=True)
        for keyItem in lstFailSummary:
            lstFailCountMachine = dicFailSummary.get(keyItem[0])
            intfailedCount = lstFailCountMachine[0]
            strCaseDescription = lstFailCountMachine[1]
            lstFailedMachine = lstFailCountMachine[2::]
            self.objReport.addFailSummary(keyItem[0], intfailedCount,
                                          strCaseDescription, lstFailedMachine)
        if cp_util.funcGetValue('SCTM', 'Update_SCTM') == "Yes":
            strSCTMResult = cp_util.funcGetValue('SCTM', 'Result_File')
            #if os.path.isfile(strSCTMResult) == 1:
             #   os.remove(strSCTMResult)
            os.chdir(os.path.dirname(strSCTMResult))
            outFile = open(os.path.basename(strSCTMResult), 'w')
            for key in sorted(dictotaltestcase.keys()):
                outFile.write("%s:%s\n" % (key, dictotaltestcase[key]))
            outFile.close()
            strresulttime = time.strftime(
                "%Y%m%d %H%M%S", time.localtime(time.time()))
            shutil.copyfile(strSCTMResult, os.path.join(
                os.path.dirname(strSCTMResult), strresulttime))

        #logging.info("dicFailSummary is " %dicFailSummary)

    def _funcReportAppendHeader(self):
        """
        Append others header for report
        """
        pass

    def _funcReportHeader(self):
        """
        process the report header contents.
        """
        # Add header info into report
        self.objReport.addHeaderInfo('**** Automation Test Result ****', '')
        self.objReport.addHeaderInfo(
            'Build', self.strBuildFolder)
        self.objReport.addHeaderInfo(
            'Total Machine Number', len(self.listMachineName))
        self.objReport.addHeaderInfo(
            'Unavailable Machine Number', str(self.intFailNum))
        __strEndTime = str(datetime.datetime.now())
        self.objReport.addHeaderInfo('Start Time',
                                     self.strStartTime[:self.strStartTime.rfind('.')])
        self.objReport.addHeaderInfo('End Time',
                                     __strEndTime[:__strEndTime.rfind('.')])
        #
        self._funcReportAppendHeader()
        #
        # do process error report
        if self.intRet != ec_MMS.SUCCESS:
            if self.intRet != ec_MMS.STATIC_CHECK_FAIL:
                self.objReport.addHeaderInfo("**** Process Error Result ****", "[ERROR %s]%s" % (str(self.intRet), self.strErrMsg))
        # list Static Report
        if len(self.lstSvrStaticChk) > 0:
            self.objReport.addHeaderInfo(
                "**** Static Test Result on Server ****", "")
            for item in self.lstSvrStaticChk:
                self.objReport.addHeaderInfo(item[0], item[1])
        #
        os.chdir('%s\\%s' % (self.strCollectReportRoot, self.strBuildFolder))
        self.objReport.write(open('WholeReport.html', 'wb'))

    def _funcUploadResultToReportSrv(self):
        """
        Upload report to tw-ets-fs
        """
        if len(self.strBuildOEM) > 0:
            strDestPath = os.path.sep.join([self.strNDCrossFilePath,
                                            self.strBuildOEM, 'report'])
        else:
            strDestPath = os.path.sep.join(
                [self.strNDCrossFilePath, 'report'])
        cp_util.funcCopyFileRemote(self.strCollectReportRoot, strDestPath,
                                   self.strNDUserName, self.strNDPassword,
                                   self.strNDDriveLetter,
                                   pathlist=self.lstCopyFolders, remote='dest')

    def _funcSendReport(self):
        """
        Notify relative person by email
        """
        strBodyFile = r'%s\%s\WholeReport.html' % \
                      (self.strCollectReportRoot, self.strBuildFolder)
        strSubject = self.strSubject % (self.strBuildOEM, self.strBuildFolder)
        # process attached file list
        lstTmp = []
        for strfile in self.lstAttachFile:
            if os.path.isfile(strfile):
                lstTmp.append(strfile)
            else:
                logging.info(str("The file [%s] is not exist!" % strfile))
        # (dev) send the server log
        strLogPath = r'C:\log\debug.log'
        if os.path.exists(strLogPath):
            strZippedLogPath = r'C:\log\debug.zip'
            zipUtil.zipFolder(strLogPath, strZippedLogPath)
            if os.path.exists(strZippedLogPath):
                lstTmp.append(strZippedLogPath)
        logging.info(str("the ini attach file list [%s]"
                     " the processed attach file list [%s]"
                     % (self.lstAttachFile, lstTmp)))
        strEmailServerIp = cp_util.funcGetValue('EMail', 'ServerIp')
        if strEmailServerIp is not None:
            logging.info(str("The Email Server IP [%s]" % strEmailServerIp))
            cp_util.send_mail(
                self.strFrom, self.mailList, self.lstCc, strSubject,
                strBodyFile, lstTmp, strEmailServerIp)
        else:
            cp_util.send_mail(
                self.strFrom, self.mailList, self.lstCc, strSubject,
                strBodyFile, lstTmp)

    def _funcStaticCheckOnServer(self):
        """
        Do static check function in server
        """
        pass

    def funcAddSvrStaticChkResult(self, strCase, strResult):
        """
        function for server static check case used.
        @param strCase: the static check case name
        @param strResult: the static check result message
        """
        self.lstSvrStaticChk.append([strCase, strResult])

    def _funcSetErrMsg(self, intErrCode, strErrMsg):
        """
        Process error code and message.
        @type intErrCode: Integate
        @param intErrCode: the error code, please reference the errocode class
        @type strErrMsg: String
        @param strErrMsg: The error message
        @note:
            Pass Static Signature Check Fail        ec_MMS.STATIC_CHECK_FAIL
            Pass Static SIA Download URL Check Fail ec_MMS.SIA_DOWNLOAD_URL_FAIL
        """
        if intErrCode == ec_MMS.STATIC_CHECK_FAIL or \
            intErrCode == ec_MMS.SIA_DOWNLOAD_URL_FAIL:
            self.intRet = ec_MMS.SUCCESS
        else:
            self.intRet = intErrCode
        self.strErrMsg = strErrMsg

    def _funcTriggerClientTest(self):
        """
        Trigger to start run case in client.
        """
        # init Central Server for all clients
        if self.intRet == ec_MMS.SUCCESS:
            self._funcCentralServerInit()

        # add tasks to
        if self.intRet == ec_MMS.SUCCESS:
            self._funcAddClientTask()

        # start server central run
        if self.intRet == ec_MMS.SUCCESS:
            self._funcCentralServerRun()

    def _funcCollectResultFromClient(self):
        """
        """
        if self.objCentralServer is None:
            return

        for strHost, objClient in self.objCentralServer.getAllTestMachine():
            try:
                ## set environment host to client for staf communication
                logging.info(str('process host [%s] task start!' % strHost))
                logging.info(str('machine info: %s' %
                    self.dictMachineInfo[strHost]))
                ## prepare 5: unzip package for test
                if self.dictMachineInfo[strHost][-1] == "windows":
                    strClientReportFolder = self.strWindowsReportFolder
                    #client report zip is created under c:/
                    strClientZipReport = os.path.join(r"C:/", self.dictMachineInfo[strHost][0] + ".zip")
                    strScriptDownloadWorkDir = self.strWindowsFolderInClient
                elif self.dictMachineInfo[strHost][-1] == "linux":
                    strClientReportFolder = self.strLinuxReportFolder
                    strClientZipReport = strClientReportFolder + r"/" + self.dictMachineInfo[strHost][0] + ".zip"
                    strScriptDownloadWorkDir = self.strLinuxFolderInClient
                else:
                    strClientReportFolder = self.strLinuxReportFolder
                    strClientZipReport = strClientReportFolder + r"/" + self.dictMachineInfo[strHost][0] + ".zip"
                    strScriptDownloadWorkDir = self.strLinuxFolderInClient
                collectReportCmd = ['python', 'util_cross_client.py',
                                    'collect_report',
                                    self.dictMachineInfo[strHost][0],
                                    self.strFsFileServerIP, strClientReportFolder,
                                    #under linux shell and STAF escape character, it needs 4 \ to specify Windows  folder
                                    os.path.sep.join([r"C:\collect_report",
                                                      self.strLabel,
                                                      'ZipREPORT']).replace("\\", "\\\\")]
                __objShellTask = ShellTask(collectReportCmd,
                    strScriptDownloadWorkDir)
                __objShellTask.strHost = strHost
                boolCompareResult = False
                intRetry = 0
                while boolCompareResult == False and intRetry < 10:
                    logging.info(str('Collect report [%s] in %s [%d], retry:%d' %
                                     (collectReportCmd, strScriptDownloadWorkDir, __objShellTask.intTimeout, intRetry)))
                    __objShellTask.run()
                    #verify md5
                    boolCompareResult = cp_util.funcComapreFileMd5Verify(
                        strHost,
                                             os.path.sep.join(["C:\\collect_report", self.strLabel,
                                                               'ZipREPORT', self.dictMachineInfo[strHost][0] + ".zip"]),
                                             strClientZipReport)
                    logging.info("client report md5 remote file %s, local file %s, comparison result %s" %
                                 (strClientZipReport,
                                  os.path.sep.join(["C:\\collect_report", self.strLabel,
                                                'ZipREPORT', self.dictMachineInfo[strHost][0] + ".zip"]),
                                    boolCompareResult))
                    intRetry = intRetry + 1
            except:
                import traceback
                logging.error("collect machine %s fail" % strHost)
                logging.error(traceback.format_exc())

    def _funcCentralServerInit(self):
        """
        Initial Central Server object. There are include create object and
        set working directory for client output resutl.
        """
        self.objCentralServer = CentralServer(self.lstClientIp,
                                              os.path.split(self.strConfigFile)[0],
                                              self.strRunCaseTimeOut)

    def _funcPreparationCentralServerInit(self):
        """
        Initial Central Server object. There are include create object and
        set working directory for client output resutl.
        """
        self.objPreparationCentralServer = CentralServer(self.lstClientIp,
                                              os.path.split(self.strConfigFile)[0],
                                              self.strRunCaseTimeOut)

##if __name__ == '__main__':
##    funcAutomationServerMain()
##    ProcessTask()._funcAnalyzeResult()
