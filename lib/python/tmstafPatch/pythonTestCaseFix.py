'''
Created on 2012/4/11

@author: eason_lin
'''
import os
import logging
from tmstaf.runnable import PythonFunction, ExternalProgram  # This two classes will be used in PythonTestCase.load() in the runtime
from tmstaf.pythonTestCase import PythonTestCase, PythonTestCaseFactory
from tmstaf.util import getException


class PythonTestCaseFactoryFix(PythonTestCaseFactory):
    def createTestCase(self, strCaseName, strSuiteName, strCasePath, strTestResultFolder, objPrdSetting):
        objTestCase = PythonTestCaseFix(strCaseName, strSuiteName,
                                        strCasePath, strTestResultFolder, objPrdSetting)
        return objTestCase


class PythonTestCaseFix(PythonTestCase):
    def __init__(self, strCaseName, strSuiteName, strCaseFile, strTestResultFolder, objProductSetting):
        super(self.__class__, self).__init__(strCaseName, strSuiteName,
                                             strCaseFile, strTestResultFolder, objProductSetting)
        self._strModule = ''
        self._strScenarioFile = []
        self._isLoaded = False
        self._isFinished = False

    def load(self):
        if not self._isLoaded:
            f = open(self._strTestCaseFile)
            try:
                exec f in globals(), locals()
            finally:
                f.close()
                del f
            if self._strScenarioFile:
                total_scenario = ""
                for each_scenario in self._strScenarioFile:
                    f = open(each_scenario)
                    total_scenario += f.read()
                    f.close()


                try:
                    #exec f in globals(), locals()
                    exec total_scenario in globals(), locals()
                finally:
                    pass
                #    f.close()
                #    del f
                
        self._isLoaded = True

    def isFinished(self):
        return self._isFinished

    def finish(self):
        self._isFinished = True
