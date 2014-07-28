import os
from tmstaf.resultInspector import ResultInspector


class TestStep(object):
    def __init__(self, objRunnable, lstArgs, strDestIp, objResultInspector):
        self.objRunnable = objRunnable
        self.lstArgs = lstArgs
        self.strDestIp = strDestIp
        self.objResultInspector = objResultInspector
        self.isPass = 0
        self.isCrash = 0
        self.tested = 0

    def verifyResult(self, result, strStdout):
        self.tested = 1
        self.objResultInspector.setResult(result)
        self.objResultInspector.setStdout(strStdout)
        self.isPass = self.objResultInspector.isPassed()
        return self.isPass

    def exceptionOccurred(self):
        self.tested = 1
        self.isCrash = 1

    def getAllAttr(self):
        lst = [('Type', self.objRunnable.getType()), ('Executable', str(self.objRunnable)),
               ('Args', str(self.lstArgs)), ('Expected-Return', str(self.objResultInspector))]
        if self.tested and not self.isCrash:
            lst.append(('Actual-Return', repr(
                self.objResultInspector.getResult())))
        else:
            lst.append(('Actual-Return', '-'))
        return lst

    def getResult(self):
        return self.objResultInspector.getResult()


class ITestCase(object):
    STAGE_SETUP = 'setup'
    STAGE_TEST = 'test'
    STAGE_TEARDOWN = 'tearDown'

    def __init__(self, strCaseName, strSuiteName, strCaseFile, strResultPath, objProductSetting):
        self._strTitle = ''
        self._strName = strCaseName
        self._strTestsuite = strSuiteName
        self._strTestCaseDir = os.path.dirname(strCaseFile)
        self._strTestCaseFile = strCaseFile
        self._dicSteps = {}
        self._strResultBase = strResultPath
        self._strTestResultDir = os.path.join(
            strResultPath, strSuiteName, strCaseName)
        if not os.path.exists(self._strTestResultDir):
            os.makedirs(self._strTestResultDir)
        self._objProductSetting = objProductSetting
        self._isFailed = False
        self.resumed = False

    def getStepsCount(self):
        return sum(map(len, self._dicSteps.values()))

    def setup(self):
        # can be overwritten by sub-class.
        return True

    def tearDown(self):
        # can be overwritten by sub-class.
        return True

    def load(self):
        NotImplementedError("%s.load() must be implemented." %
                            self.__class__.__name__)

    def isSyntaxCorrect(self):
        # can be overwritten by sub-class
        return True

    def getAllAttr(self):
        lst = [('Suite', self._strTestsuite), ('Title',
                                               self._strTitle), ('DataFile', self._strTestCaseFile)]
        return lst

    def getTestResultDir(self):
        return self._strTestResultDir

    def getTestCaseDir(self):
        return self._strTestCaseDir

    def addSetup(self, objRunnable, lstArgs, strDestIp='localhost', objResultInspector=None, inFront=0):
        return self._addStep(self.STAGE_SETUP, objRunnable, lstArgs, strDestIp, objResultInspector, inFront)

    def addTearDown(self, objRunnable, lstArgs, strDestIp='localhost', objResultInspector=None, inFront=0):
        return self._addStep(self.STAGE_TEARDOWN, objRunnable, lstArgs, strDestIp, objResultInspector, inFront)

    def addTest(self, objRunnable, lstArgs, strDestIp='localhost', objResultInspector=None, inFront=0):
        return self._addStep(self.STAGE_TEST, objRunnable, lstArgs, strDestIp, objResultInspector, inFront)

    def getSetupSteps(self):
        return self._getStep(self.STAGE_SETUP)

    def getTestSteps(self):
        return self._getStep(self.STAGE_TEST)

    def getTearDownSteps(self):
        return self._getStep(self.STAGE_TEARDOWN)

    def _addStep(self, strStage, objRunnable, lstArgs, strDestIp, objResultInspector, inFront=0):
        if not isinstance(strDestIp, (str, unicode)):
            raise ValueError('strDestIp must be string type but get %s' %
                             strDestIp)
        if not objResultInspector:
            objResultInspector = ResultInspector()
        objTestStep = TestStep(
            objRunnable, lstArgs, strDestIp, objResultInspector)
        lst = self._dicSteps.setdefault(strStage, [])
        if inFront:
            lst.insert(0, objTestStep)
        else:
            lst.append(objTestStep)
        return objResultInspector

    def _getStep(self, strStage):
        for objTestStep in self._dicSteps.get(strStage, []):
            yield objTestStep

    def getAllSteps(self):
        for objTestStep in self._dicSteps.get(self.STAGE_SETUP, []):
            yield objTestStep
        for objTestStep in self._dicSteps.get(self.STAGE_TEST, []):
            yield objTestStep
        for objTestStep in self._dicSteps.get(self.STAGE_TEARDOWN, []):
            yield objTestStep

    def getName(self):
        return self._strName

    def getTestsuite(self):
        return self._strTestsuite

    def getProductSetting(self, strKey=None, default=None):
        '''
        This method will return the instance of ProductSetting if caller doesn't pass any parameter.
        '''
        if not strKey:
            return self._objProductSetting
        return self._objProductSetting.get(strKey, default)

    def fail(self):
        self._isFailed = True

    def isFailed(self):
        return self._isFailed

    def resume(self, lstSetupStepsResult, lstTestStepsResult, lstTeardownStepsResult):
        self.resumed = True
        for objTestStep in self.getSetupSteps():
            try:
                objTestStep.verifyResult(lstSetupStepsResult.pop(0), '')
            except IndexError:
                break
        for objTestStep in self.getTestSteps():
            try:
                objTestStep.verifyResult(lstTestStepsResult.pop(0), '')
            except IndexError:
                break
        for objTestStep in self.getTearDownSteps():
            try:
                objTestStep.verifyResult(lstTeardownStepsResult.pop(0), '')
            except IndexError:
                break

    def setTitle(self, strTitle):
        self._strTitle = strTitle

    def getTitle(self):
        return self._strTitle


class ITestCaseFactory:
    def createTestCase(self, strCaseName, strSuiteName, strCasePath, strResultPath, objProductSetting):
        NotImplementedError("%s.createTestCase() must be implemented." %
                            self.__class__.__name__)
