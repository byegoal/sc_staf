import os
import logging
import time
import shutil
from tmstaf.zipUtil import zipFolder
from tmstaf.platformUtil import getPlatformInfo
from tmstaf.util import getException
from tmstaf.pythonTestCase import PythonTestCaseFactory
from tmstaf.testCaseLoader import PythonTestCaseLoader
from tmstaf.testCaseRunner import TestCaseRunner
from tmstaf.testResult import TestResult
from tmstaf.reportGenerator import ReportGenerator
from tmstaf.emailNotify import EmailNotify


class ITestRunner(object):
    SUCCESS = 0
    FAIL = 1

    def __init__(self, objTestwareConfig, objPrdSetting):
        self.objTestwareConfig = objTestwareConfig
        self.objPrdSetting = objPrdSetting
        self.objTestCaseFactory = self.getTestCaseFactory()
        self.objTestCaseLoader = self.getTestCaseLoader()
        self.objTestCaseRunner = self.getTestCaseRunner()
        self.objTestResult = self.getTestResult()
        self.objReportGenerator = ReportGenerator(
            self.objTestwareConfig.strTestResultFolder,
            self.objTestwareConfig.strTestRunName)
        self.objCurrentTestCase = None
        self.resumed = 0
        self.strResumeCase = None
        self.dicResumeSteps = {}

    def getTestCaseFactory(self):
        return PythonTestCaseFactory()

    def getTestCaseLoader(self):
        obj = PythonTestCaseLoader(
            self.objTestwareConfig.strTestCaseRootFolder)
        obj.setExcludeList(self.objTestwareConfig.lstExcludedTestSuite,
                           self.objTestwareConfig.lstExcludedTestCase)
        return obj

    def getTestResult(self):
        return TestResult()

    def getTestCaseRunner(self):
        return TestCaseRunner(self.objTestwareConfig.intLogLevel)

    def intoResumeMode(self, dicResumeData):
        self.resumed = 1
        self.strResumeCase = dicResumeData['strTestCase']
        self.dicResumeSteps = dicResumeData['dicTestedSteps']

    def createResumeData(self):
        dicResumeData = {'strTestCase': self.objCurrentTestCase.getName()}
        dicResumeData['dicTestedSteps'] = {'setup': [], 'test': [],
                                           'tearDown': []}
        for obj in self.objCurrentTestCase.getSetupSteps():
            if not obj.tested:
                break
            dicResumeData['dicTestedSteps']['setup'].append(obj.getResult())
        for obj in self.objCurrentTestCase.getTestSteps():
            if not obj.tested:
                break
            dicResumeData['dicTestedSteps']['test'].append(obj.getResult())
        for obj in self.objCurrentTestCase.getTearDownSteps():
            if not obj.tested:
                break
            dicResumeData['dicTestedSteps']['tearDown'].append(obj.getResult())
        return dicResumeData

    def run(self):
        if self.setup():
            return self.FAIL
        if not self.resumed:
            if self.checkTestCaseSyntax() == self.FAIL and not self.objTestwareConfig.isBypassSyntaxCheck:
                return self.FAIL
        if self.objTestwareConfig.strUser:
            self.addReportInfo('Run by', self.objTestwareConfig.strUser)
        self.objReportGenerator.setProductInfo(self.getProductInfo())
        self.objReportGenerator.start(self.objTestResult)
        self.runAllTestCase()
        self.objReportGenerator.setProductInfo(self.getProductInfo(
        ))  # get again if product was not installed in the beginning
        self.tearDown()
        self.objReportGenerator.finish(self.objTestResult, 'Test Report - %s - %s' % (self.getProductInfo(), self.objTestwareConfig.strTestRunName))
        self.notifyFinish()
        if self.objTestResult.getFailedCaseList():
            return self.FAIL
        return self.SUCCESS

    def setup(self):
        '''
        This method can be overwritten by sub-class.
        @Return: 0 means Success
        '''
        return self.SUCCESS

    def addReportInfo(self, strName, strValue):
        '''
        Add additional info into test report. Sub-class can call this method to add it's custom info.
        '''
        self.objReportGenerator.addAdditionalInfo(strName, strValue)

    def checkTestCaseSyntax(self):
        isFailed = False
        for strSuiteName, strCaseName, strCaseFile in self.objTestCaseLoader.get(self.objTestwareConfig.lstTargetTestSuite, self.objTestwareConfig.lstTargetTestCase):
            objTestCase = self.objTestCaseFactory.createTestCase(strCaseName, strSuiteName, strCaseFile, self.objTestwareConfig.strTestResultFolder, self.objPrdSetting)
            start = time.time()
            if not objTestCase.isSyntaxCorrect():
                isFailed = True
            if time.time() - start > 5:
                logging.warn('loading %s spends more than 5 secs: %d',
                             strCaseName, time.time() - start)
            self.objTestResult.addTestCase(objTestCase)
        return isFailed

    def runAllTestCase(self):
        strFailListFileName = 'fail_list.txt'
        strFailListFile = os.path.join(self.objTestwareConfig.strTestResultFolder, strFailListFileName)
        if os.path.exists(strFailListFile) and not self.resumed:
            os.remove(strFailListFile)
        for strSuiteName, strCaseName, strCaseFile in self.objTestCaseLoader.get(self.objTestwareConfig.lstTargetTestSuite, self.objTestwareConfig.lstTargetTestCase):
            if self.objTestResult.isTested(strSuiteName, strCaseName):
                continue
            self.objCurrentTestCase = objTestCase = self.objTestCaseFactory.createTestCase(strCaseName, strSuiteName, strCaseFile, self.objTestwareConfig.strTestResultFolder, self.objPrdSetting)
            isStopTesting = self._runTestCase(objTestCase)
            self.objReportGenerator.genTestCaseDoc(objTestCase)
            if self.objTestwareConfig.isRealTimeReport and not self.objTestwareConfig.isDryRun:
                self.objReportGenerator.update(
                    strSuiteName, self.objTestResult)
            if objTestCase.isFailed():
                open(strFailListFile, 'ab').write(objTestCase.getName() + ',')
            if isStopTesting:
                break
        if os.path.exists(strFailListFile):
            shutil.copy(strFailListFile,
                        self.objTestwareConfig.strTestCaseRootFolder)

    def _runTestCase(self, objTestCase):
        strSuiteName, strCaseName = objTestCase.getTestsuite(
        ), objTestCase.getName()
        if strCaseName != self.strResumeCase:
            self.objTestResult.startTest(strSuiteName, strCaseName)
        handler = self._initTestCaseLogger(os.path.join(objTestCase.getTestResultDir(), '%s.log' % objTestCase.getName()))
        isStopTesting = 0
        try:
            logging.info('=== %s.%s ===', strSuiteName, strCaseName)
            objTestCase.load()
            if strCaseName == self.strResumeCase:
                objTestCase.resume(self.dicResumeSteps['setup'], self.dicResumeSteps['test'], self.dicResumeSteps['tearDown'])
            self.testCaseStart(objTestCase)
            if not self.objTestwareConfig.isDryRun:
                isStopTesting = self.objTestCaseRunner.run(objTestCase)
            if objTestCase.isFailed():
                self.objTestResult.failed()
            else:
                self.objTestResult.passed()
            logging.info('run %s.%s %s', strSuiteName, strCaseName,
                         ('Pass', 'Fail')[objTestCase.isFailed()])
            logging.info('==================================')
        except SystemExit:
            raise
        except:
            objTestCase.fail()
            self.objTestResult.crashed()
            logging.error('TestCase: %s crashed! Exception:\n%s',
                          strCaseName, getException())
        finally:
            handler.close()
            logging.getLogger().removeHandler(handler)
        self.testCaseFinish(objTestCase)
        return isStopTesting

    def _initTestCaseLogger(self, strLogPath):
        h = logging.FileHandler(strLogPath, 'ab')
        h.setLevel(logging.DEBUG)
        strFormat = self.getTestCaseLoggerFormat()
        h.setFormatter(logging.Formatter(strFormat))
        logging.getLogger().addHandler(h)
        return h

    def getTestCaseLoggerFormat(self):
        '''
        This method can be overwritten by sub-class
        '''
        return '%(asctime)s %(levelname)s [%(module)s.%(funcName)s] %(message)s'

    def testCaseStart(self, objTestCase):
        '''
        This method can be overwritten by sub-class
        '''
        pass

    def testCaseFinish(self, objTestCase):
        '''
        This method can be overwritten by sub-class
        '''
        pass

    def tearDown(self):
        '''
        This method can be overwritten by sub-class.
        @Return 0 means Success
        '''
        return self.SUCCESS

    def notifyFinish(self):
        '''
        This method can be overwritten by sub-class
        '''
        pass

    def getProductInfo(self):
        '''
        This method could be overwritten by sub-class and return the product info under test
        '''
        return self.objTestwareConfig.strProductName


class BaseTestRunner(ITestRunner):
    def notifyFinish(self):
        strSummaryReportFile = os.path.join(
            self.objTestwareConfig.strTestResultFolder, 'report.html')
        self._generateEmailReport(strSummaryReportFile)
        if self.objTestwareConfig.isEmailNotifyEnable:
            self._emailNotify(strSummaryReportFile)

    def _generateEmailReport(self, strFileName):
        f = file(strFileName, 'wb')
        f.write(open(os.path.join(self.objTestwareConfig.strTestResultFolder,
                                  self.objReportGenerator.strMainPage), 'rb').read())
        f.close()
        logging.info('Generate email report: "%s"' % strFileName)

    def _emailNotify(self, strBodyFile):
        lstTo = self.objTestwareConfig.getEmailNotifyConfig().lstTo
        lstCc = self.objTestwareConfig.getEmailNotifyConfig().lstCc
        if not lstTo and not lstCc:
            return
        objEmailNotify = EmailNotify(
            self.objTestwareConfig.getEmailNotifyConfig().strSender,
            self.objTestwareConfig.getEmailNotifyConfig().strSmtpServer,
            self.objTestwareConfig.getEmailNotifyConfig().strSmtpFrom)
        objR = self.objTestResult
        if objR.intNumOfCase == objR.intPassed:
            strSubject = '[PASS]'
        else:
            strSubject = '[FAIL]'
        strSubject += ' %s' % self.getProductInfo()
        #strSubject += ' -%s-' % getPlatformInfo()
        strSubject += ' result=(F:%s, T:%s)' % (
            objR.intFailed + objR.intCrashed, objR.intNumOfCase)
        objEmailNotify.setSubject(strSubject)
        objEmailNotify.setHtmlBody(strBodyFile)

        strFolder = self.objTestwareConfig.strTestResultFolder
        strArchivePath = os.path.join(os.path.dirname(strFolder), 'result.zip')
        if self.objTestwareConfig.getEmailNotifyConfig().isIncludeReport:
            zipFolder(strFolder, strArchivePath)
            objEmailNotify.addAttachment(strArchivePath)
        try:
            objEmailNotify.send(lstTo, lstCc)
            logging.info('send test report to %s' % ','.join(lstTo + lstCc))
        finally:
            if os.path.exists(strArchivePath):
                os.remove(strArchivePath)
