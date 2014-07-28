import os
import logging
import time
import shutil
import threading
from tmstaf.util import getException
from tmstaf.testCaseRunner import TestCaseRunner
from tmstafPatch.linearTestRunner import LinearTestRunner
from tmstaf.testResult import TestResult
from threading import Thread


class ThreadTestResult(TestResult):
    def passed(self, strSuiteName, strTestCaseName):
        self.intPassed += 1
        self._finishTest('passes', strSuiteName, strTestCaseName)

    def failed(self, strSuiteName, strTestCaseName):
        self.intFailed += 1
        self._finishTest('fails', strSuiteName, strTestCaseName)

    def crashed(self, strSuiteName, strTestCaseName):
        self.intCrashed += 1
        self._finishTest('crashes', strSuiteName, strTestCaseName)

    def _finishTest(self, status, strSuiteName, strTestCaseName):
        #strSuiteName,strTestCaseName = self._lstCurrentCase
        if status != 'passes':
            self._lstNotPassed.append((strSuiteName, strTestCaseName))
        self._stopTimer(strSuiteName, strTestCaseName)
        dicSuite = self._dicSuites[strSuiteName]
        dicResult = dicSuite['testcases'][strTestCaseName]
        dicSuite[status] += 1
        dicResult[status] += 1

    def _stopTimer(self, strSuiteName, strTestCaseName):
        intSpend = time.time(
        ) - self._dicStartTime[strSuiteName + strTestCaseName]
        dicSuite = self._dicSuites[strSuiteName]
        if dicSuite['elapsedTime'] < intSpend:
            dicSuite['elapsedTime'] = intSpend
            self.intElapsedTime = intSpend
        dicResult = dicSuite['testcases'][strTestCaseName]
        dicResult['elapsedTime'] += intSpend

# TODO: Remove the unused testcase runner


class ThreadTestCaseRunner(TestCaseRunner):
    def __init__(self, intLogLevel):
        self.__intLogLevel = intLogLevel

    def runTestSteps(self, lstTestStep):
        for objTestStep in lstTestStep:
            if objTestStep.tested:
                if not objTestStep.isPass:
                    return False
                continue
            logging.info('run "%s" lstArgs=%s machine:%s', objTestStep.objRunnable, objTestStep.lstArgs, objTestStep.strDestIp)

            if not self.runStep(objTestStep):
                return False
        return True


class ThreadTestRunner(LinearTestRunner):
    def __init__(self, objTestwareConfig, objPrdSetting):
        super(self.__class__, self).__init__(objTestwareConfig, objPrdSetting)
        #self.lstTestCases = []
        strLogPath = os.path.join(self.objTestwareConfig.strTestResultFolder, "ThreadTestRunner.log")
        self._initTestRunnerLog(strLogPath)

    def _initTestRunnerLog(self, strLogPath):
        self._initTestCaseLogger(strLogPath)

    def runAllTestCase(self):
        strFailListFileName = 'fail_list.txt'
        strFailListFile = os.path.join(self.objTestwareConfig.strTestResultFolder, strFailListFileName)
        if os.path.exists(strFailListFile) and not self.resumed:
            os.remove(strFailListFile)
        thread_list = []
        testResultLock = threading.Lock()
        for strSuiteName, strCaseName, strCaseFile in self.objTestCaseLoader.get(self.objTestwareConfig.lstTargetTestSuite, self.objTestwareConfig.lstTargetTestCase):
            t = Thread(target=self._ThreadRunTestCase, args=(strFailListFile, strSuiteName, strCaseName, strCaseFile, testResultLock))
            thread_list.append(t)

        for i in range(len(thread_list)):
            thread_list[i].start()

        for i in range(len(thread_list)):
            thread_list[i].join()

        if os.path.exists(strFailListFile):
            shutil.copy(strFailListFile,
                        self.objTestwareConfig.strTestCaseRootFolder)
        else:
            if os.path.exists(os.path.join(self.objTestwareConfig.strTestCaseRootFolder, strFailListFileName)):
                os.remove(os.path.join(self.objTestwareConfig.strTestCaseRootFolder, strFailListFileName))

    def getTestResult(self):
        return ThreadTestResult()

    def getTestCaseRunner(self):
        return TestCaseRunner(self.objTestwareConfig.intLogLevel)

    def _ThreadRunTestCase(self, strFailListFile, strSuiteName, strCaseName, strCaseFile, testResultLock):
        if self.objTestResult.isTested(strSuiteName, strCaseName):
            return
        self.objCurrentTestCase = objTestCase = self.objTestCaseFactory.createTestCase(strCaseName, strSuiteName, strCaseFile,
                                                                                       self.objTestwareConfig.strTestResultFolder, self.objPrdSetting)
        """
        testResultLock.acquire()
        self.lstTestCases.append(objTestCase)
        testResultLock.release()
        """
        # the following code does test steps
        strSuiteName, strCaseName = objTestCase.getTestsuite(), objTestCase.getName()
        if strCaseName != self.strResumeCase:
            self.objTestResult.startTest(strSuiteName, strCaseName)

        self._runTestCase(objTestCase)

        testResultLock.acquire()
        try:
            self.objReportGenerator.genTestCaseDoc(objTestCase)
            if self.objTestwareConfig.isRealTimeReport and not self.objTestwareConfig.isDryRun:
                self.objReportGenerator.update(strSuiteName, self.objTestResult)
            if objTestCase.isFailed():
                open(strFailListFile, 'ab').write(objTestCase.getName() + ',')

        finally:
            objTestCase.finish()
            testResultLock.release()

    def _runTestCase(self, objTestCase):
        strSuiteName, strCaseName = objTestCase.getTestsuite(
        ), objTestCase.getName()
        isStopTesting = 0

        #named logger
        strLogPath = os.path.join(
            objTestCase.getTestResultDir(), '%s.log' % strCaseName)
        logging.info("strLogPath is: " + strLogPath)
        case_logger = logging.getLogger(strCaseName)
        h = logging.FileHandler(strLogPath, mode="a")
        case_logger.addHandler(h)

        try:
            case_logger.info('=== %s.%s ===', strSuiteName, strCaseName)
            objTestCase.load()
            if strCaseName == self.strResumeCase:
                objTestCase.resume(self.dicResumeSteps['setup'], self.dicResumeSteps['test'], self.dicResumeSteps['tearDown'])
            self.testCaseStart(objTestCase)
            if not self.objTestwareConfig.isDryRun:
                isStopTesting = self.objTestCaseRunner.run(objTestCase)
            if objTestCase.isFailed():
                self.objTestResult.failed(strSuiteName, strCaseName)
            else:
                self.objTestResult.passed(strSuiteName, strCaseName)
            case_logger.info('run %s.%s %s' % (strSuiteName, strCaseName, ('Pass', 'Fail')[objTestCase.isFailed()]))
            case_logger.info('==================================')

        except SystemExit:
            case_logger.warn('%s SystemExit' % strCaseName)
            raise

        except:
            case_logger.warn('%s exception' % strCaseName)
            objTestCase.fail()
            self.objTestResult.crashed(strSuiteName, strCaseName)
            case_logger.error('TestCase: %s crashed! Exception:\n%s', strCaseName, getException())

        self.testCaseFinish(objTestCase)
        return isStopTesting

    def _initTestCaseLogger(self, strLogPath):
        h = logging.FileHandler(strLogPath, 'ab')

        class ThreadFilter(logging.Filter):
            def filter(self, record):
                return record.thread == threading.currentThread().ident
        h.addFilter(ThreadFilter())
        h.setLevel(logging.DEBUG)
        strFormat = self.getTestCaseLoggerFormat()
        h.setFormatter(logging.Formatter(strFormat))
        logging.getLogger().addHandler(h)
        return h

    def getTestCaseLoggerFormat(self):
        #return '%(asctime)s %(levelname)s [%(module)s.%(funcName)s] %(message)s'
        return '%(asctime)s %(levelname)s [%(threadName)s] %(message)s'
