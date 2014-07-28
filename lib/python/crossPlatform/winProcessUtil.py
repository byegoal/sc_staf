'''
This module provides windows process related helper function

$Date:: 2009-09-28 22:39:01 +0800 #$
$Author: camge $
$Revision: 672 $
'''

import win32process
import win32api
import win32con
import pywintypes
import os
import time
import logging
import subprocess
import urllib
import processUtil
import misc

PSEXEC = os.path.join(os.path.dirname(__file__), 'psexec')
PSLIST = os.path.join(os.path.dirname(__file__), 'pslist')
isPsexecRegister = False
isPslistRegister = False


def killByName(strMatchStr, noError=1):
    '''
    Kill the process according to strMatchStr. This function use partial match to find the specified process.

    @param strMatchStr: Specify matching string.
    @param noError: Specify if you want to ignore "process not found" error. Default is True.
    @return:
        0 means kill process successfully.
        1 means process is not found.
    '''
    for handle, pid in enumProcessHandle(win32con.PROCESS_ALL_ACCESS):
        try:
            strImageName = win32process.GetModuleFileNameEx(handle, 0)
        except pywintypes.error, e:
            if str(e[0]) in ('6', '5'):
                continue
            logging.info('GetModuleFileNameEx failed. pid:%s Error:(%s, %s)' %
                         (pid, e[0], e[2]))
            continue
        strBaseName = os.path.basename(strImageName)
        if strBaseName.lower().find(strMatchStr.lower()) != -1:
            logging.debug('Kill process: "%s"' % strBaseName)
            win32process.TerminateProcess(handle, 0)
            return 0
    if noError:
        return 0
    return 1


def checkProcessExist(strMatchStr, intTimeout=1):
    '''
    Check if the process exists according to strMatchStr. This function use partial match to find the specified process.
    You can assign a timeout value to wait until process appeared.
    #Extra info by James C Chen 17/05/2010 : If PsList.exe does bot work on your system and displays the following messgae on console:
    =========================================================================================
    PsList 1.26 - Process Information Lister
    Copyright (C) 1999-2004 Mark Russinovich
    Sysinternals - www.sysinternals.com

    Process performance object not found on "YOUR MACHINE NAME"
    Run Exctrlst from the Windows Resource Kit to repair the performance counters.
    =========================================================================================
    Please try to download Exctrlst.exe tool to fix this issue.
    Windows 7 and Vista: http://download.microsoft.com/download/win2000platform/exctrlst/1.00.0.1/nt5/en-us/exctrlst_setup.exe
    Windows XP: http://www.microsoft.com/downloads/details.aspx?FamilyID=49ae8576-9bb9-4126-9761-ba8011fabf38&displaylang=en

    After download, install the tool and Exctrlst.exe, make sure that "PerfProc" and "PerfOS" have their Performance Counters enabled
    (select the "PerfProc" and "PerfOS" entry and verify that the "Performance Counters Enabled" option is checked)
    Once you've done that, close the window and run PsList again it shuld work

    @param strMatchStr: Specify matching string.
    @param intTimeout:
    @return:
        0 means process exists.
        2 means process is not found.
    '''
    global isPslistRegister
    if not isPslistRegister:
        misc.registerPstools('PsList')
        isPslistRegister = True
    logging.info('launch pslist.exe to check if process "%s" exists...',
                 strMatchStr)
    lstCmd = [PSLIST, strMatchStr]
    for i in range(intTimeout):
        objProcess = processUtil.TmProcess(lstCmd)
        strStdout = urllib.quote(objProcess.readStdout(), '+?&')
        if objProcess.wait() == 0:
            return 0
        time.sleep(1)
    logging.info('process "%s" does not exist', strMatchStr)
    return 2


def checkListOfProcessesExist(lstProcs):
    '''
    This funciton checks the existence of a list of processes from lstProcs by calling checkProcessExist
    @type lstProcs: List
    @param lstProcs: List of processes name to be checked
    @return: 0 means all processes in lstProcs are exist, else return a string with missing process name
    '''
    boolFoundMissing = False
    strMissingProcs = 'Following are the missing processes: '
    for proc in lstProcs:
        if checkProcessExist(proc) == 2:
            boolFoundMissing = True
            strMissingProcs += proc + ', '
    if boolFoundMissing:
        logging.info(strMissingProcs)
        return strMissingProcs
    else:
        return 0


def enumProcessHandle(intAccessMask=win32con.PROCESS_QUERY_INFORMATION):
    for pid in win32process.EnumProcesses():
        if not pid or pid < 10:
            continue
        try:
            handle = win32api.OpenProcess(intAccessMask, False, pid)
        except pywintypes.error, e:
            if str(e[0]) in ('5'):
                continue
            logging.info('OpenProcess failed. pid:%s %s' % (pid, e[2]))
            continue
        yield handle, pid


def createProcess(lstArgs, waitProcessExit=0, strPidFile=''):
    '''
    Launch an external program. Executable should be placed in the front of lstArgs.
    If you need to dump PID into a file, specify a full file path in strPidFile

    @return: Always return 0 if waitProcessExit=0 otherwise it will return the exit code after process exits.
    '''
    objPopen = processUtil.TmProcess(lstArgs)
    if strPidFile:
        logging.info('Dump PID %s into "%s"', objPopen.pid, strPidFile)
        strPidFile = open(strPidFile, 'wb')
        strPidFile.write(str(objPopen.pid))
        strPidFile.close()
    if waitProcessExit:
        strStdout = urllib.quote(objPopen.readStdout(), '+?&')
        return objPopen.wait()
    return 0


def terminateProcess(strPidFile, removePidFile=0):
    '''
    Terminate process by PID file
    @param strPidFile: PID file name
    @Return: "0" if launch successfully; Return "2" if otherwise
    '''
    intPid = int(open(strPidFile).read())
    logging.info('Terminate process with PID=%s', intPid)
    h = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, 0, intPid)
    win32api.TerminateProcess(h, 0)
    if removePidFile:
        os.remove(strPidFile)
    return 0


def runDll(strDllFile, strFunction, strParameter):
    objPopen = processUtil.TmProcess(
        ['rundll32', strDllFile, strFunction, strParameter])
    time.sleep(2)
    objPopen.kill()
    return 0


def runInSystemAccount(lstCmd, noWait=0):
    global isPsexecRegister
    logging.info('run the following cmd in the System account. %s', lstCmd)
    if not isPsexecRegister:
        misc.registerPstools('PsExec')
        isPsexecRegister = True
    #Sleep one second to prevent previous psexec call not quit completely
    time.sleep(2)

    strCmd = subprocess.list2cmdline([PSEXEC, '-s'] + lstCmd)
    objPopen = processUtil.TmProcess(strCmd, shell=False)
    if noWait:
        return objPopen
    strStdout = urllib.quote(objPopen.readStdout(), '+?&')
    intReturnCode = objPopen.wait()
    return intReturnCode, strStdout
