import logging
import optparse
import os
import sys
import time
import re
import cPickle
import shutil


MODULE_PATH = os.path.dirname(__file__) or os.getcwd()
TMSTAF_PID_FILE = os.path.join(MODULE_PATH, 'tmstaf.pid')


def addTmstafLibPath():
    sys.path.insert(0, os.path.dirname(MODULE_PATH))


def addStafLibPath():
    #Todo: we should not hardcode this path! 2009-10-14 camge
    if os.name == 'nt':
        sys.path.insert(0, r'C:\staf\bin')

addStafLibPath()
addTmstafLibPath()

import tmstaf.processUtil
from tmstaf.testwareConfig import TestwareConfig
from tmstaf.productSetting import ProductSetting
from tmstaf.testRunner import BaseTestRunner
from tmstaf.util import getException
import threading
VERSION = 'v2.1.0'


class TmstafMain:
    strVersion = VERSION
    strResumeDataFileName = 'resume.dat'
    strResumeDataFile = os.path.join(os.getcwd(), strResumeDataFileName)
    _dicLevel = {'critical': logging.CRITICAL,
                 'error': logging.ERROR,
                 'warning': logging.WARNING,
                 'info': logging.INFO,
                 'debug': logging.DEBUG}

    def __init__(self, intLogLevel=None):
        # set root logger's level to DEBUG
        self.resumed = False
        if intLogLevel:
            logging.getLogger().setLevel(intLogLevel)
        self.strCmdLine = ' '.join(sys.argv)

    def initLogFile(self, strLogFile, intLevel, mode='wb'):
        logFile = logging.FileHandler(strLogFile, mode)
        logFile.setLevel(logging.INFO)
        strFormat = '%(asctime)s %(levelname)s %(thread)s [%(module)s.%(funcName)s] %(message)s'
        logFile.setFormatter(logging.Formatter(strFormat))

        class ThreadFilter(logging.Filter):
            def filter(self, record):
                return record.thread == threading.currentThread().ident
        logFile.addFilter(ThreadFilter())
        # All messages which come from "tmstaf" logger will be written into tmstaf.log
        self.getLogger().addHandler(logFile)

    def getLogger(self):
        return logging.getLogger()
        #return logging.getLogger('tmstaf')

    def initConsoleLog(self, intLevel):
        if logging.getLogger().handlers:
            logging.getLogger().setLevel(intLevel)
            return
        console = logging.StreamHandler(sys.stdout)
        console.setLevel(intLevel)
        console.setFormatter(logging.Formatter('%(asctime)s.%(msecs)d %(levelname)s %(thread)s [%(module)s.%(funcName)s] %(message)s', '%H:%M:%S'))
        logging.getLogger().addHandler(console)

    def getCmdLineParser(self):
        usage = "\n %prog -c FILE [Options]\n %prog -h"
        parser = optparse.OptionParser(usage=usage)
        parser.set_description('TMSTAF %s' % self.strVersion)
        parser.add_option('-c', dest='cfgFile', type='string', metavar='<File>', help=r'Specify TMSTAF configuration file. For example, C:\STAF\testsuites\myProduct\tmstaf.ini')
        parser.add_option('-p', dest='prdSettingFile', type='string', metavar='<File>', help=r'Specify product specific configuration file. For example, C:\STAF\testsuites\myProduct\myProduct.ini')
        parser.add_option('-l', dest='logLvl', type='choice', choices=self._dicLevel.keys(), metavar='<Level>', help='Specify the logging level. LEVEL={%s} [default: info]' % ' '.join(self._dicLevel.keys()))
        parser.add_option('-s', dest='testSuites', type='string', metavar='<TestSuites>', help=r'Specify test suites which you want to run them only and separated them by comma and surround with double quote. For example, "suite1,suite2"')
        parser.add_option('-t', dest='testCases', type='string', metavar='<TestCases>', help=r'Specify test cases which you want to run them only and separated by comma and surround with double quote. For example, "testcase001,testcase002"')
        parser.add_option('-x', dest='excludeTestSuite', type='string', metavar='<TestSuites>', help=r'Specify test suites which you want to exclude them from test and separated them by comma and surround with double quote. For example, "suite1,suite2"')
        parser.add_option('-e', dest='excludeTestCase', type='string', metavar='<TestCases>', help=r'Specify test cases which you want to exclude them from test and separated them by comma and surround with double quote. For example, "testcase001,testcase002"')
        parser.add_option('-f', dest='caseFile', type='string', metavar='<File>', help=r'Specify a text file which contains test case names that you want run. This option will overwrite -s and -t options. File format: separate each test case name by comma or new line.')
        parser.add_option('-o', dest='outputDir', type='string', metavar='<Dir>', help=r'Specify a directory in which TMSTAF will write test result.')
        parser.add_option('-a', dest='mailTo', type='string', metavar='<EmailList>', help=r'Specify email addresses which TMSTAF will send test result to. This option will enable email notify automatically.')
        parser.add_option('-n', dest='testName', type='string', metavar='<TestName>', help=r'Specify a name for this test run. TMSTAF will use a timestamp YYYY-MM-DD-HHMM as default name if user does not specify')
        parser.add_option('-u', dest='user', type='string', metavar='<User>', help=r'Specify a your name for this test run. TMSTAF will put the name in the test result and email notification. Ex. "Camge Lo" or "Camge <chienchih_lo@trend.com.tw>"')
        parser.add_option('--dry-run', dest='dryRun', action="store_true", default=False, help=r'Load test case only. All test steps will not be run.')
        parser.add_option('--disable-realtime-report', dest='disableRealtimeReport', action="store_true", help=r'Disable updating test report in real-time mode.')
        parser.add_option('--disable-email-notify', dest='disableEmailNotify', action="store_true", help=r'Disable email notification after testing finished.')
        parser.add_option('--enable-email-notify', dest='enableEmailNotify', action="store_true", help=r"Enable email notification after testing finished. Its priority is higher than disable-email-notify")
        parser.add_option('--no-email-attachment', dest='noEmailAttachment', action="store_true", help=r'Do not attach full test result zip file when send email report.')
        parser.add_option('--bypass-syntax-check', dest='bypassSyntaxCheck', action="store_true", help=r'Bypass test case syntax check error and continue the subsequent testing.')
        parser.add_option('--resume', dest='resume', action="store_true", default=False, help=r'Resume test execution after machine reboot.')
        parser.set_defaults(logLvl='info')
        parser.set_defaults(testSuites='')
        parser.set_defaults(testCases='')
        parser.set_defaults(excludeTestSuite=None)
        parser.set_defaults(excludeTestCase=None)
        return parser

    def parseCmdLine(self):
        parser = self.getCmdLineParser()
        (options, args) = parser.parse_args()
        return parser, options, args

    def verifyCmdLineOption(self, parser, options):
        if not options.cfgFile:
            parser.error("options -c is not speficied")
            return False
        return True

    def getTestwareConfig(self, strConfigFilePath):
        objCfg = TestwareConfig()
        objCfg.loadFromIniFile(strConfigFilePath)
        strSubFolder = '%s_result_%s' % (
            objCfg.strProductName, time.strftime('%Y-%m-%d_%H%M%S'))
        objCfg.strTestResultFolder = os.path.join(
            objCfg.strTestResultFolder, strSubFolder)
        objCfg.strTestRunName = time.strftime('%Y-%m-%d-%H%M%S')
        return objCfg

    def setup(self):
        parser, options, lstArgs = self.parseCmdLine()
        self.initConsoleLog(self._dicLevel[options.logLvl])
        if lstArgs:
            self.getLogger().error(
                "unknown command line argument: %s" % lstArgs)
            return False
        if not self.verifyCmdLineOption(parser, options):
            return False
        if options.resume:
            self.resumed = 1
            if not os.path.exists(self.strResumeDataFile):
                strPath = os.path.dirname(options.cfgFile)
                self.strResumeDataFile = os.path.join(
                    strPath, self.strResumeDataFileName)
                if os.path.exists(self.strResumeDataFile):
                    os.chdir(strPath)
            objTestwareConfig, self.resumeTestResult, self.dicResumeData = self.__parseResumeDataFile(self.strResumeDataFile)
            shutil.copy(self.strResumeDataFile,
                        objTestwareConfig.strTestResultFolder)
            os.remove(self.strResumeDataFile)
        else:
            objTestwareConfig = self.getTestwareConfig(options.cfgFile)
            objTestwareConfig.intLogLevel = self._dicLevel[options.logLvl]
            self.mergeCmdLineOptions(options, objTestwareConfig)
            if not os.path.exists(objTestwareConfig.strTestResultFolder):
                os.makedirs(objTestwareConfig.strTestResultFolder)
            else:
                raise RuntimeError('"%s" already exists.' %
                                   objTestwareConfig.strTestResultFolder)
        self.objTestwareConfig = objTestwareConfig
        self.initLogFile(os.path.join(objTestwareConfig.strTestResultFolder,
                                      'tmstaf.log'), objTestwareConfig.intLogLevel, 'ab')
        self.initLogFile(os.path.join(objTestwareConfig.strTestResultFolder, 'tmstaf.log'), objTestwareConfig.intLogLevel, 'ab')
        return True
     

    def mergeCmdLineOptions(self, options, objTestwareConfig):
        objTestwareConfig.isDryRun = options.dryRun
        if options.testName:
            objTestwareConfig.strTestRunName = options.testName
        #assign test result folder
        if options.outputDir:
            objTestwareConfig.strTestResultFolder = options.outputDir.strip()
        if options.disableRealtimeReport is not None:
            objTestwareConfig.isRealTimeReport = not options.disableRealtimeReport
        if options.prdSettingFile:
            objTestwareConfig.strProductSettingFile = options.prdSettingFile
        if options.user is not None:
            objTestwareConfig.strUser = options.user
            objTestwareConfig.getEmailNotifyConfig().strSender = options.user
        if options.disableEmailNotify is not None:
            objTestwareConfig.isEmailNotifyEnable = 0
        if options.enableEmailNotify is not None:
            objTestwareConfig.isEmailNotifyEnable = 1
        if options.mailTo:
            lstTo = [x.strip() for x in re.split(
                ',|;', options.mailTo) if x.strip()]
            objTestwareConfig.getEmailNotifyConfig().lstTo = lstTo
            if options.enableEmailNotify is None:  # Enable email notification
                objTestwareConfig.isEmailNotifyEnable = 1
        if options.noEmailAttachment is not None:
            objTestwareConfig.getEmailNotifyConfig().isIncludeReport = 0
        if options.bypassSyntaxCheck is not None:
            objTestwareConfig.isBypassSyntaxCheck = 1
        if options.excludeTestSuite is not None:
            objTestwareConfig.lstExcludedTestSuite = [s.strip() for s in options.excludeTestSuite.split(',') if s.strip()]
        if options.excludeTestCase is not None:
            objTestwareConfig.lstExcludedTestCase = [s.strip() for s in options.excludeTestCase.split(',') if s.strip()]
        if options.caseFile:
            self.getLogger().info('use test cases file: %s', options.caseFile)
            lstTestSuites = []
            lstTestCases = self._handleCaseFile(options.caseFile)
        else:
            lstTestSuites = [s.strip() for s in options.testSuites.split(
                ',') if s.strip()]
            lstTestCases = [s.strip() for s in options.testCases.split(
                ',') if s.strip()]
        if lstTestCases:
            objTestwareConfig.lstTargetTestCase = lstTestCases
            # If user assign test cases, we should reset testsuite to empty first
            objTestwareConfig.lstTargetTestSuite = []
        if lstTestSuites:
            objTestwareConfig.lstTargetTestSuite = lstTestSuites
        return objTestwareConfig

    def _handleCaseFile(self, strFile):
        lstTestCases = []
        for line in open(strFile):
            if line[0] == '#':
                continue
            for s in line.strip().split(','):
                s = s.strip()
                if s:
                    lstTestCases.append(s)
        return lstTestCases

    def run(self):
        if not self.setup():
            return 1
        self.getLogger().info(self.strCmdLine)
        if not self.resumed:
            self.getLogger().info('TMSTAF %s' % self.strVersion)
            self.getLogger().info('%s start test %s' % ('-' * 20, '-' * 20))
            self.getLogger().info('WorkingDirectory = %s', os.getcwd())
            self.getLogger().info('ConfigFile=%s' %
                                  self.objTestwareConfig.strConfigFile)
            self.getLogger().info('DesignatedSuites=%s' %
                                  self.objTestwareConfig.lstTargetTestSuite)
            self.getLogger().info('DesignatedCases=%s' %
                                  self.objTestwareConfig.lstTargetTestCase)
            self.getLogger().info('TestwareConfiguration:\n>>>>\n%s\n<<<<' %
                                  self.objTestwareConfig.debugPrint())
        if not self.objTestwareConfig.lstTargetTestCase and not self.objTestwareConfig.lstTargetTestSuite:
            self.getLogger().info('No Assigned TestCases or TestSuite')
            self.getLogger().info('%s end %s' % ('-' * 20, '-' * 20))
            return 0
        objPrdSetting = ProductSetting()
        if self.objTestwareConfig.strProductSettingFile:
            objPrdSetting.loadFromIni(
                self.objTestwareConfig.strProductSettingFile)

        if self.objTestwareConfig.strTestRunnerClass:
            strModule, strClass = self.objTestwareConfig.strTestRunnerClass.rsplit('.', 1)
            exec 'from %s import %s' % (strModule, strClass)
            klass = eval(strClass)
            objTestRunner = klass(self.objTestwareConfig, objPrdSetting)
        else:
            objTestRunner = BaseTestRunner(
                self.objTestwareConfig, objPrdSetting)

        if self.resumed:
            objTestRunner.objTestResult = self.resumeTestResult
            objTestRunner.intoResumeMode(self.dicResumeData)
            self.getLogger().info('resume the testing from %s',
                                  objTestRunner.strResumeCase)
        try:
            intRC = objTestRunner.run()
        except SystemExit:
            self.__writeResumeDataFile(objTestRunner)
            raise
        except:
            self.getLogger().error('Exception:\n%s' % getException())
            raise
        self.getLogger().info('%s end %s' % ('-' * 20, '-' * 20))
        return intRC

    def __writeResumeDataFile(self, objTestRunner):
        f = open(self.strResumeDataFile, 'wb')
        cPickle.dump(self.objTestwareConfig, f, cPickle.HIGHEST_PROTOCOL)
        cPickle.dump(objTestRunner.objTestResult, f, cPickle.HIGHEST_PROTOCOL)
        dicResumeData = objTestRunner.createResumeData()
        cPickle.dump(dicResumeData, f, cPickle.HIGHEST_PROTOCOL)
        f.close()

    def __parseResumeDataFile(self, strResumeDataFile):
        self.getLogger().info(
            'resume test by using %s' % repr(strResumeDataFile))
        f = open(strResumeDataFile, 'rb')
        objTestwareConfig = cPickle.load(f)
        objTestResult = cPickle.load(f)
        dicResumeData = cPickle.load(f)
        f.close()
        return objTestwareConfig, objTestResult, dicResumeData

    def getTestRunner(self, objTestwareConfig, strProductSettingPath):
        # you can overwrite this method to return your own test runner object
        return BaseTestRunner(objTestwareConfig, strProductSettingPath)


def runTmstaf(*lst):
    # Not run from command line
    lst = list(lst)
    lst.insert(0, __file__)
    sys.argv = lst
    return TmstafMain().run()

if __name__ == '__main__':
    if os.path.exists(TMSTAF_PID_FILE) and int(open(TMSTAF_PID_FILE, 'rb').read()) in tmstaf.processUtil.getAllProcessId():
        strPid = open(TMSTAF_PID_FILE, 'rb').read()
        print 'Another TMSTAF process is running! Its pid is:' % strPid
        print 'If process %s is not TMSTAF process, please remove %s and try again.' % (strPid, TMSTAF_PID_FILE)
        sys.exit(1)
    open(TMSTAF_PID_FILE, 'wb').write('%s' % os.getpid())
    NFSPATH = "\\\\172.18.0.10\\sc"
    NFSUSER = "cloud9user"
    NFSPASS = "P@ssw0rd"
    os.system("net use %s %s /user:%s" % (NFSPATH, NFSPASS, NFSUSER))
    try:
        intRc = TmstafMain(logging.DEBUG).run()
    finally:
        os.remove(TMSTAF_PID_FILE)
    sys.exit(intRc)
