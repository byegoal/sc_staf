import logging
import subprocess
import time
import PySTAF
from staf.tmStafHandle import TmStafHandle


class StafProcessService:
    def __init__(self, intTimeout=10800, dicEnv=None):
        self.strOption = 'USEPROCESSVARS STDERRTOSTDOUT RETURNSTDOUT WAIT %s000' % intTimeout
        if dicEnv:
            for k, v in dicEnv.items():
                self.strOption += ' Env %s' % PySTAF.wrapData('%s=%s' % (k, v))

    def call(self, strDestIp, strExecutable, lstArgs):
        self.strDestIp = strDestIp
        self.strExecutable = strExecutable
        self.lstArgs = lstArgs
        strRequest = self._composeRequest(strExecutable, lstArgs)
        handle = TmStafHandle(strExecutable)
        objTmStafResult = handle.submit(strDestIp, 'PROCESS', strRequest)
        if objTmStafResult.isOk():
            dicResult = objTmStafResult.getResult()
            return self._parseResult(dicResult)
        logging.info('strRequest=%s', repr(strRequest))
        if objTmStafResult.isTimeout():
            strResult = objTmStafResult.getResult()
            return self._parseTimeoutResult(strResult)
        else:
            raise RuntimeError('Call STAF Process service failed! %s' %
                               objTmStafResult)

    def _composeRequest(self, strExecutable, lstArgs):
        strCmd = 'START SHELL COMMAND %s' % PySTAF.wrapData(strExecutable)
        strParms = subprocess.list2cmdline([str(s) for s in lstArgs])
        strParms = 'PARMS %s' % PySTAF.wrapData(strParms)
        strRequest = ' '.join([strCmd, strParms, self.strOption])
        return strRequest

    def _parseResult(self, dicResult):
        rc = int(dicResult['rc'])
        dicFile = dicResult['fileList'][0]
        #logging.debug("Result is ["+ str(dicResult.items()) + "]")
        if dicFile['rc'] != '0':
            raise RuntimeError('Call STAF Process service failed! Can get stdout/stderr content.')
        return rc, dicFile['data']

    def _parseTimeoutResult(self, strResult):
        raise RuntimeError('Wait STAF Process finished timeout!')


class ProductStafProcessService(StafProcessService):
    def __init__(self, intTimeout=10800, dicEnv=None, workdir=None):
        self.workdir = workdir
        StafProcessService.__init__(self, intTimeout, dicEnv)

    def _composeRequest(self, strExecutable, lstArgs):
        strCmd = 'START SHELL COMMAND %s' % PySTAF.wrapData(strExecutable)
        strParms = subprocess.list2cmdline([str(s) for s in lstArgs])
        strParms = 'PARMS %s' % PySTAF.wrapData(strParms)
        strRequest = ' '.join([strCmd, strParms, self.strOption])
        if self.workdir is not None:
            strWorkdir = 'WORKDIR %s' % PySTAF.wrapData(self.workdir)
            strRequest = ' '.join([strRequest, strWorkdir])
        return strRequest


class StafProcessHandle(object):
    def __init__(self, stdout, stderr, handle, strEndpoint):
        self.stdout = stdout
        self.stderr = stderr
        self.handle = handle
        self.strEndpoint = strEndpoint
        self.resultHandle = StafProcessService()

    def _getResult(self):
        wait_handle = TmStafHandle("wait_process")
        strCmd = 'LIST'
        strRequest = ' '.join([strCmd])
        objTmStafResult = wait_handle.submit(self.strEndpoint,
                                             'PROCESS', strRequest, TmStafHandle.Synchronous)
        if objTmStafResult.isOk():
            lstResult = objTmStafResult.getResult()
            rc = parseProcessListResult(
                lstResult, self.strEndpoint, self.handle)
            return rc
        elif objTmStafResult.isTimeout():
            raise RuntimeError('Wait STAF Process finished timeout!')
        else:
            raise RuntimeError('Call STAF Process service failed! %s' %
                               objTmStafResult)

    def waitProcess(self, intTimeout=600, trace=True):
        for i in range(intTimeout / 10):

            try:
                rc = self._getResult()
                if rc is not None:
                    return rc, self.getStdout(), self.getStderr()
                elif trace:
                    logging.debug("\n======== stdout ===========\n%s\n======== stdout ===========" % self.getStdout())
                    logging.debug("\n======== stderr ===========\n%s\n======== stderr ===========" % self.getStderr())
            except RuntimeError:
                import sys
                import traceback
                exc_type, exc_value, exc_traceback = sys.exc_info()
                logging.error(repr(traceback.format_exception(
                    exc_type, exc_value, exc_traceback)))
            logging.info("Start sleep times %i..." % i)
            time.sleep(10.0)

    def getStdout(self):
        return getFile(self.strEndpoint, self.stdout)

    def getStderr(self):
        return getFile(self.strEndpoint, self.stderr)

    def getStdoutTail(self):
        pass

    def getStderrTail(self):
        pass


def getFile(strEndpoint, file, intTimeout=30):
    handle = TmStafHandle("result_process")
    lstCmd = ['GET', 'FILE', file]
    strRequest = ' '.join(lstCmd)
    objTmStafResult = handle.submit(
        strEndpoint, 'FS', strRequest, TmStafHandle.Synchronous)
    if objTmStafResult.isOk():
        lstResult = objTmStafResult.getResult()
        return parseFileResult(lstResult)
    elif objTmStafResult.isTimeout():
        raise RuntimeError('Wait STAF Process finished timeout!')
    else:
        raise RuntimeError(
            'Call STAF Process service failed! %s' % objTmStafResult)


def shutdown(strEndpoint):
    handle = TmStafHandle("shutdown_process")
    lstCmd = ['shutdown']
    strRequest = ' '.join(lstCmd)
    objTmStafResult = handle.submit(
        strEndpoint, 'shutdown', strRequest, TmStafHandle.Synchronous)
    if objTmStafResult.isOk():
        return 0
    elif objTmStafResult.isTimeout():
        raise RuntimeError('Wait STAF Process finished timeout!')
    else:
        raise RuntimeError('Call STAF Process service failed! %s' %
                           objTmStafResult)


def parseFileResult(lstResult):
    return lstResult


class StafProcessServiceAsync(ProductStafProcessService):
    def __init__(self, dicEnv=None, workdir=None, stdout="stdout.txt", stderr="stderr.txt"):
        self.strOption = 'USEPROCESSVARS STDOUT %s STDERR %s WAIT %s000' % (
            stdout, stderr, str(0))
        if dicEnv:
            for k, v in dicEnv.items():
                self.strOption += ' Env %s' % PySTAF.wrapData('%s=%s' % (k, v))
        self.workdir = workdir
        self.stdout = stdout
        self.stderr = stderr

    def _parseTimeoutResult(self, strResult):
        self.handle = strResult
        return self.handle, StafProcessHandle(self.stdout, self.stderr, self.handle, self.strDestIp)
'''
def waitProcess(strEndpoint, strProcessHandle, intTimeout=600):
    handle = TmStafHandle("wait_process")
    lstCmd=['LIST']
    strRequest=' '.join(lstCmd)
    for i in range(intTimeout/10):
        objTmStafResult = handle.submit(strEndpoint, 'PROCESS',
            strRequest,TmStafHandle.Synchronous)
        if objTmStafResult.isOk():
            lstResult=objTmStafResult.getResult()
            rc = parseProcessListResult(lstResult,strEndpoint,strProcessHandle)
            if rc<>None:
                return rc
        elif objTmStafResult.isTimeout():
            raise RuntimeError('Wait STAF Process finished timeout!')
        else:
            raise RuntimeError('Call STAF Process service failed! %s'%
                objTmStafResult)
        time.sleep( 10.0 )
        logging.info("sleep times %i"%i)
'''


def parseProcessListResult(lstResult, strEndpoint, strProcessHandle):
    '''
    print lstResult
    >>>[{'staf-map-class-name': 'STAF/Service/Process/ProcessListInfo', 'handle': '45', 'startTimestamp': '20110927-04:40:45', 'command': 'ifconfig', 'rc': '0', 'endTimestamp': '20110927-04:40:46'},
    {'staf-map-class-name': 'STAF/Service/Process/ProcessListInfo', 'handle': '54', 'startTimestamp': '20110927-04:58:56', 'command': 'ipconfig', 'rc': '127', 'endTimestamp': '20110927-04:58:57'},
    {'staf-map-class-name': 'STAF/Service/Process/ProcessListInfo', 'handle': '57', 'startTimestamp': '20110927-05:11:28', 'command': 'ifconfig', 'rc': '0', 'endTimestamp': '20110927-05:11:29'},
    {'staf-map-class-name': 'STAF/Service/Process/ProcessListInfo', 'handle': '84', 'startTimestamp': '20110927-06:03:38', 'command': 'ruby -C /usr/local/staf/lib/ruby/autoAgentMountLinux1.2/ /usr/local/staf/lib/ruby/autoAgentMountLinux1.2/runCase.rb build_name no_smoke', 'rc': '0', 'endTimestamp': '20110927-06:06:56'},
    {'staf-map-class-name': 'STAF/Service/Process/ProcessListInfo', 'handle': '145', 'startTimestamp': '20110927-21:47:54', 'command': 'ruby -C /usr/local/staf/lib/ruby/autoAgentMountLinux1.2/ /usr/local/staf/lib/ruby/autoAgentMountLinux1.2/runCase.rb build_name no_smoke', 'rc': None, 'endTimestamp': None}]
    '''
    logging.debug("Parsing Process List ...")
    for mapResult in lstResult:
        #logging.debug("mapResult is [%s]" % str(mapResult))
        if mapResult["handle"] == strProcessHandle:
            #logging.debug("ProcessHandle [%s] on Endpoint [%s] Return Code is [%s]" % (strProcessHandle, strEndpoint,str(mapResult["rc"])))
            if mapResult["rc"] is None:
                logging.info("ProcessHandle [%s] on Endpoint [%s] is Still Running" % (strProcessHandle, strEndpoint))
                return None
            else:
                logging.info("ProcessHandle [%s] on Endpoint [%s] Returned [%s]" % (strProcessHandle, strEndpoint, str(mapResult["rc"])))
                return int(mapResult["rc"])
    else:
        logging.error("ProcessHandle [%s] on Endpoint [%s] doesn't exist" %
                      (strProcessHandle, strEndpoint))
        return 0


def freeProcess(strEndpoint, strProcessHandle):
    handle = TmStafHandle("free_process")
    logging.debug("Freeing process handle [%s]" % strProcessHandle)
    strCmd = "FREE HANDLE %s" % strProcessHandle
    strRequest = ' '.join([strCmd])
    objTmStafResult = handle.submit(
        strEndpoint, 'PROCESS', strRequest, TmStafHandle.Synchronous)
