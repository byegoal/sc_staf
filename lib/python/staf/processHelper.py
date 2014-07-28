import logging
import subprocess
import os
import traceback
import socket
import stafQueue
import tmStafHandle
import stafVar


class TimeoutError(Exception):
    pass


def wrapData(s):
    import PySTAF
    return PySTAF.wrapData(s)


def getHostName():
    return socket.gethostname().split('.')[0]


class StafProcess(object):

    def __init__(self, strHost, lstCmd, strWorkDir='', dicEnv={}, shell=False, intTimeout=0, strStaticHandleName=None):
        self.isStdoutDownloaded = 0
        self.intRc = None
        self.intTimeout = intTimeout
        self._strHost = strHost
        self._h = tmStafHandle.TmStafHandle(r'Trend\StafProcess')
        self._strLogPath = os.path.join(
            stafVar.getVar('STAF/DataDir', self._h), 'tmp')
        self._strRemoteStdoutFile = os.path.join('{STAF/DataDir}', 'tmp', 'stafProcess_%s_%s_stdout.log' % (getHostName(), self._h.handle))
        self._strRemoteStderrFile = os.path.join('{STAF/DataDir}', 'tmp', 'stafProcess_%s_%s_stderr.log' % (getHostName(), self._h.handle))
        self._strStdoutFile = os.path.join(self._strLogPath, 'stafProcess_%s_%s_stdout_local.log' % (self._strHost, self._h.handle))
        self._strStderrFile = os.path.join(self._strLogPath, 'stafProcess_%s_%s_stderr_local.log' % (self._strHost, self._h.handle))
        strCmd = wrapData(lstCmd[0])
        strParms = subprocess.list2cmdline([str(s) for s in lstCmd[1:]])
        if shell:
            strStart = 'START SHELL COMMAND'
        else:
            strStart = 'START COMMAND'
        lstParms = [strStart, strCmd, 'PARMS', wrapData(strParms), 'STDOUT', wrapData(self._strRemoteStdoutFile), 'STDERR', wrapData(self._strRemoteStderrFile)]
        if strStaticHandleName:
            lstParms.extend(['STATICHANDLENAME', strStaticHandleName])
        if strWorkDir:
            lstParms.extend(['WORKDIR', wrapData(strWorkDir)])
        if dicEnv:
            for k, v in dicEnv.items():
                v = subprocess.list2cmdline([v])
                lstParms.append('Env %s' % wrapData('%s=%s' % (k, v)))
        lstParms.extend(self._getAdditionalParms())
        lstParms.extend(self.getWindowsTitle(lstCmd))
        self._run(lstParms)

    def getWindowsTitle(self, lstCmd):
        if lstCmd[0].lower() == 'cmd' and lstCmd[1].lower() == '/c':
            strTitle = ' '.join([str(x) for x in lstCmd[2:]])
        else:
            strTitle = ' '.join([str(x) for x in lstCmd])
        return ['TITLE', wrapData(strTitle)]

    def _getAdditionalParms(self):
        if self.intTimeout:
            return ['WAIT %ss' % self.intTimeout]
        else:
            return ['WAIT']

    def _run(self, lstParms):
        strRequest = ' '.join(lstParms)
        #objResult=self._h.submit(self._strHost, 'PROCESS', strRequest, mode = self._h.Synchronous)
        objResult = self._h.submit(self._strHost, 'PROCESS',
                                   strRequest, mode=self._h.Queue)
        if objResult.isTimeout():
            raise TimeoutError(objResult)
        if not objResult.isOk():
            raise RuntimeError(objResult)
        queue = stafQueue.StafQueue(self._h, 'local')
        objResult, dicMsg = queue.get('STAF/RequestComplete', self.intTimeout)
        if not objResult.isOk():
            if objResult.isTimeout():
                raise TimeoutError(objResult)
            raise RuntimeError(objResult)
        self._handleResult(dicMsg['rc'], dicMsg['result'])

    def _handleResult(self, rc, result):
        if isinstance(result, (str, unicode)):
            self.intRc = int(rc)
            self.isStdoutDownloaded = 1
            open(self._strStderrFile, 'wb').write(result)
        else:
            self.intRc = int(result.getRootObject()['rc'])

    def _getStdout(self):
        '''
        Downloading stdout/stderr file via FS service can prevent STAF crash in Non-English OS
        '''
        strRequest = 'COPY FILE %s TOFILE %s' % (
            self._strRemoteStdoutFile, self._strStdoutFile)
        objResult = self._h.submit(self._strHost, 'FS', strRequest)
        if not objResult.isOk():
            logging.error('download stdout file from %s failed! Error:%s',
                          self._strHost, objResult)
        strRequest = 'COPY FILE %s TOFILE %s' % (
            self._strRemoteStderrFile, self._strStderrFile)
        objResult = self._h.submit(self._strHost, 'FS', strRequest)
        if not objResult.isOk():
            logging.error('download stderr file from %s failed! Error:%s',
                          self._strHost, objResult)

    def _deleteRemoteStdout(self):
        if hasattr(self, '_h'):
            #remove stdout and stderr log files in remote {STAF/DataDir}/tmp folder.
            #we don't care if these files will be removed or not because STAF will empty the folder after it restarts
            strRequest = 'DELETE ENTRY {STAF/DataDir}/tmp CHILDREN NAME "stafProcess_%s_%s*" EXT log CONFIRM' % (getHostName(), self._h.handle)
            self._h.submit(self._strHost, 'FS', strRequest,
                           self._h.FireAndForget)

    def wait(self):
        return self.intRc

    def readStdout(self):
        if not self.isStdoutDownloaded:
            self.isStdoutDownloaded = 1
            self._getStdout()
        if os.path.exists(self._strStdoutFile):
            return open(self._strStdoutFile, 'rb').read()
        else:
            return ''

    def readStderr(self):
        if not self.isStdoutDownloaded:
            self.isStdoutDownloaded = 1
            self._getStdout()
        if os.path.exists(self._strStderrFile):
            return open(self._strStderrFile, 'rb').read()
        else:
            return ''

    def getStdoutPath(self):
        if os.path.exists(self._strStdoutFile):
            return self._strStdoutFile
        else:
            return ''

    def __del__(self):
        self._deleteRemoteStdout()
        if hasattr(self, '_strStdoutFile') and os.path.exists(self._strStdoutFile):
            os.remove(self._strStdoutFile)
        if hasattr(self, '_strStderrFile') and os.path.exists(self._strStderrFile):
            os.remove(self._strStderrFile)


class AsyncStafProcess(StafProcess):
    strRemoteHandle = None
    autoFree = 1

    def _getAdditionalParms(self):
        return ['NOTIFY', 'ONEND']

    def _handleResult(self, rc, result):
        self.strRemoteHandle = result

    def wait(self, intTimeout):
        if self.intRc is not None:
            return self.intRc
        queue = stafQueue.StafQueue(self._h, 'local')
        objResult, dicMessage = queue.get('STAF/Process/End', intTimeout)
        if not objResult.isOk():
            if objResult.isTimeout():
                raise TimeoutError(objResult)
            raise RuntimeError(objResult)
        self.intRc = int(dicMessage['rc'])
        return self.intRc

    def stop(self):
        if self.strRemoteHandle:
            logging.debug('stop handle %s in %s',
                          self.strRemoteHandle, self._strHost)
            try:
                self._h.submit(self._strHost, 'PROCESS',
                               'STOP HANDLE %s' % self.strRemoteHandle)
                self._h.submit(self._strHost, 'PROCESS', 'FREE ALL')
            except:
                logging.error('stop handle %s failed! Exception:%s', self.strRemoteHandle, traceback.format_exc())
            self.strRemoteHandle = None

    def disableAutoFree(self):
        self.autoFree = 0

    def __del__(self):
        super(AsyncStafProcess, self).__del__()
        if self.autoFree:
            try:
                self.stop()
            except:
                pass


def test1():
    logging.debug('-- test StafProcess --')
    lstCmd = ['python', 'test.py', 2, 'This is "a" dog.']
    obj = StafProcess('10.2.204.71', lstCmd, r'c:\staf\lib\python\trend')
    logging.debug('wait() return %s', obj.wait())
    logging.debug(obj.getStdoutPath())
    logging.debug('stdout:\n%s', obj.readStdout())


def test2():
    logging.debug('-- test AsyncStafProcess --')
    lstCmd = ['python', 'test.py', 3, 'This is "a" dog.']
    obj = AsyncStafProcess('10.2.204.71', lstCmd, r'c:\staf\lib\python\trend')
    logging.debug('wait() return %s', obj.wait(10))
    logging.debug('stdout:\n%s', obj.readStdout())


def test3():
    logging.debug('-- test AsyncStafProcess --')
    lstCmd = ['python', 'test.py', 30, 'This is "a" dog.']
    obj = AsyncStafProcess('10.2.204.71', lstCmd, r'c:\staf\lib\python\trend')
    try:
        logging.debug('wait() return %s', obj.wait(1))
    except TimeoutError:
        logging.debug('wait() timeout.')
    logging.debug('stdout:\n%s', obj.readStdout())


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, datefmt='%H:%M:%S',
                        format='%(asctime)s %(module)s.%(funcName)s %(message)s')
    test1()
    test2()
    test3()
