import thread
import logging
import os
import time
import threading
import staf.util
from tmstaf.util import getException
from tmstaf.processUtil import TmProcess


class Task(object):
    def __init__(self, lstArgs=None, expectResult=None):
        self.strHost = ''
        self.intTimeout = 300
        self.strStdout = ''
        self.strStderr = ''
        self.expectResult = expectResult
        self.actualResult = None
        self.lstArgs = []
        self.__isTimeout = False
        if lstArgs:
            self.lstArgs = lstArgs

    def run(self):
        raise NotImplementedError('%s.run() should be implemented!' %
                                  self.__class__.__name__)

    def isFail(self):
        if self.expectResult is not None and self.actualResult != self.expectResult:
            return True
        if self.isTimeout():
            return True
        return False

    def isTimeout(self):
        return self.__isTimeout

    def timeout(self):
        self.__isTimeout = True

    def readStdout(self):
        return self.strStdout

    def readStderr(self):
        return self.strStderr


class ShellTask(Task):
    def __init__(self, lstArgs, strWorkDir='', expectResult=None):
        self.strWorkDir = strWorkDir
        super(ShellTask, self).__init__(lstArgs, expectResult)

    def run(self):
        if self.strHost in ('', 'local', 'localhost'):
            obj = TmProcess(self.lstArgs)
            self.strStdout = obj.readStdout()
            self.actualResult = obj.wait()
        else:
            import staf.processHelper
            lstCmd = self.lstArgs
            objStafProcess = staf.processHelper.AsyncStafProcess(self.strHost, lstCmd, self.strWorkDir, shell=True, strStaticHandleName='%s@%s' % (lstCmd[0], self.strWorkDir))
            try:
                self.actualResult = objStafProcess.wait(self.intTimeout)
            except staf.processHelper.TimeoutError:
                self.timeout()
            finally:
                self.strStdout = objStafProcess.readStdout()
                self.strStderr = objStafProcess.readStderr()

    def __str__(self):
        return '<ShellTask %s@%s at %s>' % (self.lstArgs[0], self.strWorkDir, self.strHost)


class PythonTask(Task):
    def __init__(self, strModule, strFunc, lstArgs=None, expectResult=None):
        self.strModule = strModule
        self.strFunc = strFunc
        super(PythonTask, self).__init__(lstArgs, expectResult)

    def run(self):
        if self.strHost in ('', 'local', 'localhost'):
            exec "from %s import %s" % (self.strModule, self.strFunc)
            f = eval(self.strFunc)
            self.actualResult = f(*self.lstArgs)
        else:
            import staf.pyFuncHelper
            objRemotePythonRunner = staf.pyFuncHelper.RemotePythonRunner(self.strHost, self.strModule, self.strFunc, self.lstArgs, self.intTimeout)
            try:
                self.actualResult = objRemotePythonRunner.wait()
            except staf.pyFuncHelper.TimeoutError:
                self.timeout()
            finally:
                self.strStdout = objRemotePythonRunner.readStdout()
                self.strStderr = objRemotePythonRunner.readStderr()

    def __str__(self):
        return '<PythonTask %s.%s at %s>' % (self.strModule, self.strFunc, self.strHost)


class TestMachine(object):
    STATUS_INIT = 'init'
    STATUS_OFFLINE = 'offline'
    STATUS_ONLINE = 'online'
    STATUS_RUNNING = 'running'
    STATUS_PASS = 'pass'
    STATUS_FAIL = 'fail'
    STATUS_CRASH = 'crash'

    def __init__(self, server, strHost):
        self.strStatus = self.STATUS_INIT
        self.server = server
        self.strHost = strHost
        self.lstTask = []
        self.server.addMachine(self)
        self.strResultPath = os.path.join(self.server.strResultPath, strHost)

    def isPass(self):
        return self.strStatus == self.STATUS_PASS

    def initLog(self):
        strFormat = '%(asctime)s [%(module)s.%(funcName)s] %(message)s'
        objFileHandler = logging.FileHandler(
            os.path.join(self.strResultPath, 'task.log'), 'wb')
        objFileHandler.setFormatter(logging.Formatter(strFormat, '%H:%M:%S'))
        logging.getLogger(self.strHost).addHandler(objFileHandler)
        logging.getLogger(self.strHost).setLevel(logging.DEBUG)
        return objFileHandler

    def __str__(self):
        return '<Machine %s>' % self.strHost

    def addTask(self, task, intTimeout=10800):
        task.intTimeout = intTimeout
        task.strHost = self.strHost
        self.lstTask.append(task)

    def addServerTask(self, task):
        '''
        Server task will be executed on Central Server
        '''
        task.strHost = 'local'
        self.lstTask.append(task)

    def run(self):
        if not self.checkStafService():
            return self.STATUS_OFFLINE

        if not os.path.exists(self.strResultPath):
            os.makedirs(self.strResultPath)
        objFileHandler = self.initLog()
        logging.getLogger(self.strHost).info('%s start to run task.', self)
        for task in self.lstTask:
            logging.getLogger(self.strHost).info('run task: %s', task)
            self.strStatus = self.STATUS_RUNNING
            try:
                task.run()
            except:
                self.strStatus = self.STATUS_CRASH
                logging.getLogger(self.strHost).error('run %s failed! Exception:\n%s', task, getException())
                break
            for strPipeName, strBuf in (('stdout', task.readStdout()), ('stderr', task.readStderr())):
                if strBuf:
                    logging.getLogger(self.strHost).propagate = 0
                    logging.getLogger(self.strHost).debug(
                        '%s:\n%s', strPipeName, strBuf)
                    logging.getLogger(self.strHost).propagate = 1
            if task.isFail():
                if task.isTimeout():
                    logging.getLogger(self.strHost).error(
                        'run %s timeout!', task)
                else:
                    logging.getLogger(self.strHost).error(
                        'run %s failed!', task)
                self.strStatus = self.STATUS_FAIL
                break
        else:
            self.strStatus = self.STATUS_PASS
        objFileHandler.close()
        logging.getLogger(self.strHost).removeHandler(objFileHandler)
        return self.strStatus

    def checkStafService(self):
        logging.getLogger(self.strHost).info(
            'check STAF service on %s', self.strHost)
        if staf.util.waitStafReady(self.strHost, self.server.intClientOnlineCheckRetryCount):
            self.strStatus = self.STATUS_OFFLINE
            return False
        else:
            self.strStatus = self.STATUS_ONLINE
            return True


class CentralServer(object):
    FAIL = 1
    SUCCESS = 0

    def __init__(self, lstMachine=(), strResultDir=os.getcwd(), strRunTaskTimeOut=None):
        logging.basicConfig(format='%(asctime)s %(levelname)s\t[%(thread)d] %(message)s', datefmt='%H:%M:%S', level=logging.DEBUG)
        self.intClientOnlineCheckRetryCount = 2
        self.strResultPath = os.path.join(
            strResultDir, 'result', time.strftime('%Y-%m-%d_%H%M%S'))
        if not os.path.exists(self.strResultPath):
            os.makedirs(self.strResultPath)
        else:
            raise RuntimeError('"%s" already exists.' % self.strResultPath)
        self.logFile = self.initFileLog(
            os.path.join(self.strResultPath, 'debug.log'))
        self.dicMachines = {}
        self.dicHostStatus = {}

        for strHost in lstMachine:
            self.addMachine(TestMachine(self, strHost))
        self.objEvent = threading.Event()
        self.objEvent.clear()
        self.objLock = threading.Lock()
        self.intRestClient = 0
        self.intRunTaskTimeOut = 86400 * 7  # default is one week
        if strRunTaskTimeOut and int(strRunTaskTimeOut):
            self.intRunTaskTimeOut = int(strRunTaskTimeOut)

    def initFileLog(self, strLogFile):
        strFormat = '%(asctime)s %(levelname)s\t[%(thread)d] [%(module)s.%(funcName)s] %(message)s'
        logFile = logging.FileHandler(strLogFile, 'wb')
        logFile.setFormatter(logging.Formatter(strFormat, '%H:%M:%S'))
        logging.getLogger().addHandler(logFile)
        logging.getLogger().setLevel(logging.DEBUG)
        return logFile

    def addMachine(self, machine):
        '''
        This method is called in TestMachine.__init__()
        '''
        self.dicMachines.setdefault(machine.strHost, machine)

    def getAllTestMachine(self):
        for strHost, objMachine in self.dicMachines.items():
            yield strHost, objMachine

    def getMachine(self, strHost):
        return self.dicMachines.get(strHost)

    def updateResult(self, machine):
        self.objLock.acquire()
        self.intRestClient -= 1
        if not self.intRestClient:
            self.objEvent.set()
        self.objLock.release()
        logging.info("machine %s finished. machine-running/total: %s/%s" % (machine.strHost, self.intRestClient, len(self.dicMachines)))

    def runTaskInClient(self, machine):
        try:
            machine.run()
        except:
            logging.getLogger(self.strHost).error('run task in %ss failed! Exception:\n%s', machine.strHost, getException())
        self.updateResult(machine)

    def run(self):
        if not self.setup():
            return self.FAIL

        if staf.util.waitStafReady('local', 1):
            return self.FAIL

        if not self.dicMachines:
            logging.warning('machine list is empty')
            return self.SUCCESS

        logging.info("run central server with timeout %s seconds",
                     self.intRunTaskTimeOut)
        self.intRestClient = len(self.dicMachines)
        for machine in self.dicMachines.values():
            thread.start_new_thread(self.runTaskInClient, (machine,))

        self.objEvent.wait(self.intRunTaskTimeOut)
        intResult = self.SUCCESS
        for machine in self.dicMachines.values():
            logging.info('machine %s status: %s',
                         machine.strHost, machine.strStatus)
            if not machine.isPass():
                intResult = self.FAIL
        logging.info('log files: %s', self.strResultPath)
        self.logFile.close()
        logging.getLogger().removeHandler(self.logFile)
        return intResult

    def setup(self):
        return True

    def checkIfAllMachinesOnline(self, intTimeout=30):
        logging.info('check if all machines are online...')
        lstOnline, lstOffline = staf.util.pingRemoteHosts([objMachine.strHost for objMachine in self.dicMachines.values()], intTimeout)
        for strHost in lstOffline:
            logging.warn('%s is *OFFLINE*', strHost)
        if lstOffline:
            return False
        return True
