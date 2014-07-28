import logging
import os
import time
import subprocess
import sys
import PySTAF
from processHelper import StafProcess, AsyncStafProcess
from tmStafHandle import TmStafHandle
from stafQueue import StafQueue
ERR_REBOOT = 100
ERR_SHUTDOWN = 101


def reboot(strHost=None, intWaitTime=10):
    '''
    This function can reboot current machine or a remote machine according to strHost value.
    If reboot self, it will call sys.exit(100) before reboot. Otherwise, it will return 0 or error code.
    @param strHost: Specify an IP address or hostname if you want to reboot a remote host. Default value "None" means reboot self.
    @param intWaitTime: Specify how much time to wait before reboot. Default is 10 seconds.
    @return: Reboot self will raise SystemExit exception. Reboot remote host will return 0 or error code.
    '''
    lstCmd = ['shutdown', '-r', '-f', '-t', str(intWaitTime)]
    if not strHost or strHost.lower() in ('127.0.0.1', 'localhost'):
        objP = subprocess.Popen(lstCmd, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        objP.stdout.read()
        objP.wait()
        sys.exit(ERR_REBOOT)
    objStafProcess = StafProcess(strHost, lstCmd)
    intRc = objStafProcess.wait()
    if intRc:
        logging.error('Shutdown %s failed. Error:%s', strHost, intRc)
        return intRc
    logging.debug('waiting for %s shutdown...', strHost)
    time.sleep(10)
    intRc = waitStafQuit(strHost, 60)
    if intRc:
        return intRc
    logging.debug('waiting for %s start...', strHost)
    time.sleep(10)
    intRc = waitStafReady(strHost, 60)
    return intRc


def shutdown(strHost=None, intWaitTime=10):
    '''
    This function can shutdown current machine or a remote machine according to strHost value.
    If shutdown self, it will call sys.exit(100) before shutdown.
    @param strHost: Specify an IP address or hostname if you want to reboot a remote host. Default value "None" means shutdown self.
    @param intWaitTime: Specify how much time to wait before shutdown. Default is 10 seconds.
    @return: Shutdown self will raise SystemExit exception. Shutdown remote host will return 0 or error code.
    '''
    if os.name == 'nt':
        lstCmd = ['shutdown', '-s', '-d', 'p:2:4', '-f', '-t', str(
            intWaitTime)]
    else:
        lstCmd = ['shutdown', '-P', '-f', '-t', str(intWaitTime)]
    if not strHost or strHost.lower() in ('127.0.0.1', 'localhost'):
        objP = subprocess.Popen(lstCmd, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        objP.stdout.read()
        objP.wait()
        sys.exit(ERR_SHUTDOWN)
    objStafProcess = StafProcess(strHost, lstCmd)
    intRc = objStafProcess.wait()
    if intRc:
        logging.error('Shutdown %s failed. Error:%s stdout:\n%s\n%s', strHost, intRc, objStafProcess.readStdout(), objStafProcess.readStderr())
        return intRc
    logging.debug('waiting for %s shutdown...', strHost)
    time.sleep(10)
    intRc = waitStafQuit(strHost, 60)
    if intRc:
        return intRc
    return 0


def downloadFile(strHost, strTargetFile, strLocalPath, strLocalFileName=None):
    if not os.path.exists(strLocalPath):
        os.makedirs(strLocalPath)
    strRequest = 'COPY FILE %s' % (PySTAF.wrapData(strTargetFile))
    if strLocalFileName:
        strRequest += ' TOFILE %s' % (PySTAF.wrapData(
            os.path.join(strLocalPath, strLocalFileName)))
    else:
        strRequest += ' TODIRECTORY %s' % (PySTAF.wrapData(strLocalPath))
    h = TmStafHandle('Trend/copyFile')
    objResult = h.submit(strHost, 'FS', strRequest)
    if not objResult.isOk():
        logging.error('copy "%s" to "%s" failed! %s' % (
            strTargetFile, strLocalPath, objResult))
        return 1
    return 0


def waitStafReady(strHost, intLoopTimes=30):
    '''
    Wait for STAF service ready on remote machine.
    @param strHost: Remote machine IP or hostname
    @param intLoopTimes: loop how many times to wait remote machine start, default is 30 times
    @return: 0 means STAF is ready; 1 means not
    '''
    handle = TmStafHandle(r'Trend/Ping')
    for i in range(intLoopTimes):
        objResult = handle.submit('local', 'ping',
                                  'ping machine %s' % strHost, mode=handle.Synchronous)
        if objResult.isOk():
            logging.debug('STAF service is ready on %s', strHost)
            return 0
    logging.error('STAF service is NOT ready on %s', strHost)
    return 1


def waitStafQuit(strHost, intLoopTimes=30, intInterval=1):
    '''
    Wait STAF service to quit(means shutdown) on remote machine.
    @param strHost: Remote machine IP or hostname
    @param intLoopTimes: loop how many times to wait remote machine shutdown, default is 30 times
    @param intInterval: sleep how many seconds in each loop of waiting remote shutdown
    @return: 0 means STAF quitted; 1 means not
    '''
    handle = TmStafHandle(r'Trend/Ping')
    for i in range(intLoopTimes):
        objResult = handle.submit('local', 'ping',
                                  'ping machine %s' % strHost, mode=handle.Synchronous)
        if not objResult.isOk():
            logging.debug('STAF service quited on %s', strHost)
            return 0
        time.sleep(intInterval)
    logging.error('STAF service does NOT quit on %s', strHost)
    return 1


def pingRemoteHosts(lstHost, intTimeout=30):
    '''
    This function uses STAF PING service to check if STAF service is ready on remote host.
    It check all hosts asynchronously, so it will return very quickly if all hosts are online.
    Note! This function will raise RuntimeError exception if local STAF service is not running.
    @param lstHost: specify a list of remote hosts. Ex. ("192.168.1.1","192.168.1.2",...)
    @param intTimeout: specify how long will this function wait for remote host's response. Default is 30 seconds
    @return: (lstOnline, lstOffline)
    '''
    handle = TmStafHandle('Trend/Ping')
    dicHost = {}
    for strHost in lstHost:
        objResult = handle.submit('local', 'ping',
                                  'ping machine %s' % strHost, mode=handle.Queue)
        if not objResult.isOk():
            raise RuntimeError(objResult)
        strRequestNumber = objResult.getResult()
        dicHost[strRequestNumber] = strHost
    lstOnline, lstOffline = [], []
    queue = StafQueue(handle, 'local')
    start = time.time()
    while time.time() - start < intTimeout and dicHost:
        objResult, dicMsg = queue.get('STAF/RequestComplete', 2)
        if objResult.isTimeout():
            logging.debug('waiting for response from %s ...',
                          ','.join(dicHost.values()))
            continue
        if not objResult.isOk():
            raise RuntimeError(objResult)
        strHost = dicHost.pop(dicMsg['requestNumber'])
        if dicMsg['rc'] == '0':
            logging.debug('%s is online', strHost)
            lstOnline.append(strHost)
        else:
            logging.error('ping %s failed. rc:%s error:%s',
                          strHost, dicMsg['rc'], dicMsg['result'])
            lstOffline.append(strHost)
    if dicHost:
        logging.warn('TIMEOUT waiting for response from %s',
                     ','.join(dicHost.values()))
        lstOffline.extend(dicHost.values())
    return lstOnline, lstOffline
