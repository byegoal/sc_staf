import os
import subprocess
import time
import tmstaf.callPyFunction


class IRunnable(object):
    strExecutable = ''
    intTimeout = 10800
    cwd = None

    def getType(self):
        return self.__class__.__name__

    def getExecutable(self):
        return self.strExecutable

    def run(self, strDestIp, lstArgs, intLogLevel):
        if not strDestIp or strDestIp in ('local', 'localhost', '127.0.0.1'):
            intExitCode, strStdout = self._runInLocal(lstArgs, intLogLevel)
        else:
            from stafServices import StafProcessService
            objStafProcessService = StafProcessService(self.intTimeout,
                                                       {'TMSTAF_LOG_LEVEL': str(intLogLevel)})
            lstArgs = self._processArgs(lstArgs)
            intExitCode, strStdout = objStafProcessService.call(
                strDestIp, self.strExecutable, lstArgs)
        return intExitCode, strStdout

    def _runInLocal(self, lstArgs, intLogLevel):
        lstArgs = self._processArgs(lstArgs)        
        lstArgs.insert(0, self.strExecutable)        
        dicEnv = os.environ.copy()
        dicEnv['TMSTAF_LOG_LEVEL'] = str(intLogLevel)
    
        if os.name == "nt":
            _strExecutable = None
        else:
            _strExecutable = self.strExecutable
            
        p = subprocess.Popen(lstArgs, stdin=subprocess.PIPE, stdout=subprocess.PIPE, \
            stderr=subprocess.STDOUT, env=dicEnv, universal_newlines=True, shell=True, \
            cwd=self.cwd, executable=_strExecutable)

        strStdout = p.stdout.read()
        for i in range(self.intTimeout):
            intExitCode = p.poll()
            if intExitCode is not None:
                break
            time.sleep(1)
        if intExitCode is None:
            raise RuntimeError('Wait process finished timeout!')
        return intExitCode, strStdout

    def _processArgs(self, lstArgs):
        #return copy string
        return lstArgs[:]

    def __str__(self):
        return '%s' % self.strExecutable


class PythonFunction_org(IRunnable):
    def __init__(self, strModule, strFuncName, intTimeout=10800):
        self.intTimeout = intTimeout
        self.strModuleName = strModule
        self.strFuncName = strFuncName
        self.strExecutable = 'python'
        self._callPyFunctionPath = os.path.basename(
            tmstaf.callPyFunction.__file__)
        if self._callPyFunctionPath[-3:].lower() == 'pyc':
            self._callPyFunctionPath = self._callPyFunctionPath[:-3] + 'py'

    def _processArgs(self, lstArgs):
        if os.environ.get('TMSTAF_HOME'):
            strDir = r'C:\STAF\lib\python\tmstaf'
        else:
            strDir = os.path.dirname(__file__) or os.getcwd()
        lstOutput = [os.path.join(strDir, self._callPyFunctionPath),
                     self.strModuleName, self.strFuncName]
        strArgs = tmstaf.callPyFunction.encodeCmdLine(lstArgs)
        lstOutput.append(strArgs)
        return lstOutput

    def _runInLocal(self, lstArgs, intLogLevel):
        exec 'from %s import %s' % (self.strModuleName, self.strFuncName)
        func = eval(self.strFuncName)
        result = func(*lstArgs)
        return result, ''

    def __str__(self):
        return '%s.%s' % (self.strModuleName, self.strFuncName)


class PythonFunction(IRunnable):
    def __init__(self, strModule, strFuncName, intTimeout=10800):
        self.intTimeout = intTimeout
        self.strModuleName = strModule
        self.strFuncName = strFuncName
        self.strExecutable = 'callPyFunction'
        #self._callPyFunctionPath=os.path.basename(tmstaf.callPyFunction.__file__)
        #if self._callPyFunctionPath[-3:].lower()=='pyc':
        #    self._callPyFunctionPath=self._callPyFunctionPath[:-3]+'py'

    def _processArgs(self, lstArgs):
        #if os.environ.get('TMSTAF_HOME'):
        #    strDir=r'C:\STAF\lib\python\tmstaf'
        #else:
        #    strDir=os.path.dirname(__file__) or os.getcwd()
        #lstOutput = [os.path.join(strDir,self._callPyFunctionPath),self.strModuleName,self.strFuncName]
        lstOutput = [self.strModuleName, self.strFuncName]
        strArgs = tmstaf.callPyFunction.encodeCmdLine(lstArgs)
        lstOutput.append(strArgs)
        return lstOutput

    def _runInLocal(self, lstArgs, intLogLevel):
        os.putenv('TMSTAF_LOG_LEVEL', str(intLogLevel))
        exec 'from %s import %s' % (self.strModuleName, self.strFuncName)
        func = eval(self.strFuncName)
        result = func(*lstArgs)
        return result, ''

    def __str__(self):
        return '%s.%s' % (self.strModuleName, self.strFuncName)


class ExternalProgram(IRunnable):
    def __init__(self, strProgram, intTimeout=10800, cwd=None):
        self.intTimeout = intTimeout
        self.strExecutable = strProgram
        self.cwd = cwd