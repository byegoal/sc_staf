'''
Created on 2012/4/11

@author: eason_lin
'''
from tmstafPatch.pythonTestCaseFix import PythonTestCaseFactoryFix
from tmstaf.testRunner import BaseTestRunner


class LinearTestRunner(BaseTestRunner):
    def getTestCaseFactory(self):
        return PythonTestCaseFactoryFix()

    def checkTestCaseSyntax(self):
        isFailed = False
        for strSuiteName, strCaseName, strCaseFile in self.objTestCaseLoader.get(self.objTestwareConfig.lstTargetTestSuite,
                                                                                 self.objTestwareConfig.lstTargetTestCase):
            objTestCase = self.objTestCaseFactory.createTestCase(
                strCaseName, strSuiteName, strCaseFile, self.objTestwareConfig.strTestResultFolder,
                self.objPrdSetting)
            if not self.objTestwareConfig.isBypassSyntaxCheck:
                start = time.time()
                if not objTestCase.isSyntaxCorrect():
                    isFailed = True
                if time.time() - start > 5:
                    logging.warn('loading %s spends more than 5 secs: %d',
                                 strCaseName, time.time() - start)
            self.objTestResult.addTestCase(objTestCase)
        return isFailed

    def run(self):
        if self.setup():
            return self.FAIL
        if not self.resumed:
            if self.checkTestCaseSyntax() == self.FAIL:
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
