import binascii
import logging
import os
import sys

#It's value should be "{STAF/Config/STAFRoot}/lib/python/staf"
STAF_WRAPPER_LIB_DIR = os.path.dirname(__file__) or os.getcwd()


def addTmstafLibPath():
    sys.path.insert(0, os.path.dirname(STAF_WRAPPER_LIB_DIR))


def addStafLibPath():
    stafRoot = os.path.dirname(
        os.path.dirname(os.path.dirname(STAF_WRAPPER_LIB_DIR)))
    sys.path.insert(0, os.path.join(stafRoot, 'bin'))

if __name__ == '__main__':
    addTmstafLibPath()
    addStafLibPath()

from processHelper import AsyncStafProcess, StafProcess
from processHelper import TimeoutError  # for pyFuncHelper caller


class RemotePythonRunner(object):
    HelperKlass = StafProcess
    lstDelegateFunc = ['readStdout', 'readStderr', 'getStdoutPath']

    def __init__(self, strHost, strModule, strFunc, lstArgs, intTimeout=0, dicEnv={}):
        self.strModule = strModule
        self.strFunc = strFunc
        self.intTimeout = intTimeout
        strSelfName = os.path.basename(__file__)
        if strSelfName[-3:].lower() == 'pyc':
            strSelfName = strSelfName[:-3] + 'py'
        strWorkDir = '{STAF/Config/STAFRoot}{STAF/Config/Sep/File}lib{STAF/Config/Sep/File}python{STAF/Config/Sep/File}staf'
        lstCmd = ['python', strSelfName, self.strModule,
                  self.strFunc, self._encodeData(lstArgs)]
        #Below line will block until remote command finished
        self._objHelper = self.HelperKlass(strHost, lstCmd, strWorkDir, dicEnv=dicEnv, intTimeout=self.intTimeout, strStaticHandleName='Python/%s.%s' % (self.strModule, self.strFunc))

        self._setMethod()

    def wait(self):
        return self._objHelper.wait()

    def _setMethod(self):
        for strMethod in self.lstDelegateFunc:
            setattr(self, strMethod, getattr(self._objHelper, strMethod))

    @staticmethod
    def _encodeData(lstArgs):
        return binascii.b2a_base64(str(lstArgs)).replace('\r\n', '')

    @staticmethod
    def _decodeData(strData):
        return eval(binascii.a2b_base64(strData))

    @staticmethod
    def _realRun():
        logging.basicConfig(level=logging.DEBUG, stream=sys.stdout, datefmt='%H:%M:%S', format='%(asctime)s\t%(levelname)s\t[%(module)s.%(funcName)s]\t%(message)s')
        try:
            strModuleName, strFuncName, strArgs = sys.argv[1:]
        except ValueError, e:
            raise RuntimeError('Parameter error: %s' % sys.argv[1:])
        lstArgs = RemotePythonRunner._decodeData(strArgs)
        exec('from %s import %s' % (strModuleName, strFuncName))
        func = eval(strFuncName)
        return func(*lstArgs)


class AsyncRemotePythonRunner(RemotePythonRunner):
    HelperKlass = AsyncStafProcess
    lstDelegateFunc = RemotePythonRunner.lstDelegateFunc + ['stop']

    def wait(self, intTimeout):
        return self._objHelper.wait(intTimeout)

if __name__ == '__main__':
    sys.exit(RemotePythonRunner._realRun())
