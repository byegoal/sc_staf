import os
import logging
from tmstaf.runnable import PythonFunction, ExternalProgram  # This two classes will be used in PythonTestCase.load() in the runtime
from tmstaf.testCase import ITestCase, ITestCaseFactory
from tmstaf.util import getException


class PythonTestCaseFactory(ITestCaseFactory):
    def createTestCase(self, strCaseName, strSuiteName, strCasePath, strTestResultFolder, objPrdSetting):
        objTestCase = PythonTestCase(strCaseName, strSuiteName,
                                     strCasePath, strTestResultFolder, objPrdSetting)
        return objTestCase


class PythonTestCase(ITestCase):
    def __init__(self, strCaseName, strSuiteName, strCaseFile, strTestResultFolder, objProductSetting):
        super(PythonTestCase, self).__init__(strCaseName, strSuiteName,
                                             strCaseFile, strTestResultFolder, objProductSetting)
        self._strModule = ''
        self._strScenarioFile = ''
        self._strCaseId = ''

    def isSyntaxCorrect(self):
        try:
            self.load()
            return True
        except:
            logging.error('Load test case "%s" failed! Exception:\n%s',
                          self._strName, getException())
        return False

    def load(self):
        f = open(self._strTestCaseFile)
        try:
            exec f in globals(), locals()
        finally:
            f.close()
            del f
        if self._strScenarioFile:
            f = open(self._strScenarioFile)
            try:
                exec f in globals(), locals()
            finally:
                f.close()
                del f

    def setModule(self, strModule):
        self._strModule = strModule

    def setScenario(self, strFileName):
        strDirName = os.path.dirname(strFileName)
        if not strDirName:
            strScenarioFile = os.path.join(os.getcwd(), strFileName)
        else:
            strScenarioFile = strFileName
        if not os.path.exists(strScenarioFile):
            strScenarioFile = os.path.join(self._strTestCaseDir, strFileName)
            if not os.path.exists(strScenarioFile):
                strScenarioFile = os.path.join(os.path.dirname(
                    self._strTestCaseDir), strFileName)
                if not os.path.exists(strScenarioFile):
                    strScenarioFile = os.path.join(os.path.dirname(os.path.dirname(self._strTestCaseDir)), strFileName)

        self._strScenarioFile.append(strScenarioFile)

    def getScenario(self):
        # temp resolution, just return the first one
        if not self._strScenarioFile:
            return ""
        else:
            return self._strScenarioFile[0]

    def getAllAttr(self):
        lst = super(PythonTestCase, self).getAllAttr()
        lst.extend([('Module', self._strModule), ('Scenario',
                                                  self._strScenarioFile), ('CaseId', self._strCaseId)])
        return lst
