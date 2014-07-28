import logging
from tmstaf.util import getException


class TestCaseRunner:

    def __init__(self, intLogLevel):
        self.__intLogLevel = intLogLevel

    def run(self, objTestCase):
        '''
        @return: If this method return 1, the whole testing will be stopped.
        '''
        if not objTestCase.getStepsCount():
            logging.info('%s is empty.' % objTestCase.getName())
            objTestCase.fail()
            return 0
        try:
            if not objTestCase.resumed and not objTestCase.setup():
                objTestCase.fail()
                return 1

            if self.runSetupSteps(objTestCase.getSetupSteps()):
                if not self.runTestSteps(objTestCase.getTestSteps()):
                    objTestCase.fail()
            else:
                objTestCase.fail()

            if not self.runTearDownSteps(objTestCase.getTearDownSteps()):
                objTestCase.fail()
        finally:
            if not objTestCase.tearDown():
                objTestCase.fail()
                return 1
        return 0

    def runSetupSteps(self, lstTestStep):
        for objTestStep in lstTestStep:
            if objTestStep.tested:
                if not objTestStep.isPass:
                    return False
                continue
            logging.info('run "%s" lstArgs=%s machine:%s', objTestStep.objRunnable, objTestStep.lstArgs, objTestStep.strDestIp)
            if not self.runStep(objTestStep):
                return False
        return True

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

    def runTearDownSteps(self, lstTestStep):
        '''
        We should run each tear down steps even though they fail.
        '''
        isPass = True
        for objTestStep in lstTestStep:
            if objTestStep.tested:
                if not objTestStep.isPass:
                    isPass = False
                continue
            logging.info('run "%s" lstArgs=%s machine:%s', objTestStep.objRunnable, objTestStep.lstArgs, objTestStep.strDestIp)
            if not self.runStep(objTestStep):
                isPass = False
        return isPass

    def runStep(self, objTestStep):
        try:
            result, strStdout = objTestStep.objRunnable.run(objTestStep.strDestIp, objTestStep.lstArgs, self.__intLogLevel)
            isPass = objTestStep.verifyResult(result, strStdout)
        except SystemExit:
            isPass = objTestStep.verifyResult(None, '')
            if not isPass:
                logging.error('run %s failed. result=None expect=%s', objTestStep.objRunnable, objTestStep.objResultInspector)
            logging.info('"%s" trigger the system reboot.',
                         objTestStep.objRunnable)
            raise
        except:
            objTestStep.exceptionOccurred()
            isPass = 0
            result = None
            try:
                strStdout = '%s' % getException()
            except:
                strStdout = '%s' % repr(getException())
        if not isPass:
            logging.error('run %s failed. result=%s expect=%s', objTestStep.objRunnable, repr(result), objTestStep.objResultInspector)
            if strStdout:
                logging.error('stdout:\n%s', strStdout)
        else:
            logging.info('"%s" return %s',
                         objTestStep.objRunnable, repr(result))
            if strStdout:
                logging.debug('stdout:\n%s', strStdout)
        return isPass
