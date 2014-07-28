import time
import os

_dicResultTemplate = {'elapsedTime': 0, 'passes': 0, 'fails': 0, 'starts':
                      0, 'crashes': 0, 'scenario': '', 'title': ''}


class TestResult:
    def __init__(self):
        self._dicSuites = {}
        self._dicStartTime = {}
        self._lstNotPassed = []
        self.intNumOfCase = 0
        self.intStarted = 0
        self.intPassed = 0
        self.intFailed = 0
        self.intCrashed = 0
        self.intElapsedTime = 0

    def addTestCase(self, objTestCase):
        strTestCaseName, strSuiteName = objTestCase.getName(
        ), objTestCase.getTestsuite()
        dicSuite = self._dicSuites.setdefault(strSuiteName, {'testcases': {}, 'starts': 0, 'passes': 0, 'fails': 0, 'crashes': 0, 'elapsedTime': 0})
        dicResult = dicSuite['testcases'].setdefault(
            strTestCaseName, _dicResultTemplate.copy())
        dicResult['scenario'] = os.path.basename(objTestCase.getScenario())
        dicResult['title'] = objTestCase.getTitle()
        self.intNumOfCase += 1

    def isTested(self, strSuiteName, strTestCaseName):
        dicResult = self._dicSuites[strSuiteName]['testcases'][strTestCaseName]
        if dicResult['passes'] or dicResult['fails'] or dicResult['crashes']:
            return True
        return False

    def startTest(self, strSuiteName, strTestCaseName):
        dicSuite = self._dicSuites[strSuiteName]
        dicSuite['starts'] += 1
        dicResult = dicSuite['testcases'][strTestCaseName]
        dicResult['starts'] += 1
        self._startTimer(strSuiteName, strTestCaseName)
        self._lstCurrentCase = (strSuiteName, strTestCaseName)
        self.intStarted += 1

    def passed(self):
        self.intPassed += 1
        self._finishTest('passes')

    def failed(self):
        self.intFailed += 1
        self._finishTest('fails')

    def crashed(self):
        self.intCrashed += 1
        self._finishTest('crashes')

    def _finishTest(self, status):
        strSuiteName, strTestCaseName = self._lstCurrentCase
        if status != 'passes':
            self._lstNotPassed.append((strSuiteName, strTestCaseName))

        self._stopTimer(strSuiteName, strTestCaseName)
        dicSuite = self._dicSuites[strSuiteName]
        dicResult = dicSuite['testcases'][strTestCaseName]
        dicSuite[status] += 1
        dicResult[status] += 1

    def _startTimer(self, strSuiteName, strTestCaseName):
        self._dicStartTime[strSuiteName + strTestCaseName] = time.time()

    def _stopTimer(self, strSuiteName, strTestCaseName):
        intSpend = time.time(
        ) - self._dicStartTime[strSuiteName + strTestCaseName]
        dicSuite = self._dicSuites[strSuiteName]
        dicSuite['elapsedTime'] += intSpend
        dicResult = dicSuite['testcases'][strTestCaseName]
        dicResult['elapsedTime'] += intSpend
        self.intElapsedTime += intSpend

    def getTestsuiteList(self):
        return self._dicSuites.keys()

    def getSuite(self, strSuiteName):
        return self._dicSuites[strSuiteName]

    def getFailedCaseList(self):
        return self._lstNotPassed

    def getAllTestCase(self):
        lstOutput = []
        lstSuite = self._dicSuites.keys()
        lstSuite.sort()
        for strSuite in lstSuite:
            dicSuite = self._dicSuites[strSuite]
            lstCase = dicSuite['testcases'].keys()
            lstCase.sort()
            for strTestCaseId in lstCase:
                dicResult = dicSuite['testcases'][strTestCaseId]
                lstOutput.append((strSuite, strTestCaseId, dicResult))
        return lstOutput
