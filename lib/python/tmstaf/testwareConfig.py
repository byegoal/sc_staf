import ConfigParser
import re
import logging


class EmailNotifyConfig:
    strSmtpServer = 'msa.hinet.net'
    strSmtpFrom = 'cpm_automation@msa.hinet.net'
    strSender = '"TMSTAF_Admin" <chienchih_lo@trend.com.tw>'
    lstTo = []
    lstCc = []
    isIncludeReport = 1

    def debugPrint(self):
        lst = []
        for s in dir(self):
            if callable(getattr(self, s)):
                continue
            if s[:2] == '__': continue
            lst.append('  EmailNotifyConfig.%s = %s' % (s, getattr(self, s)))
        return '\n'.join(lst)


class TestwareConfig:
    def __init__(self):
        self.strConfigFile = ''
        self.strProductName = ''
        self.strFileServer = 'local'
        self.strTestCaseRootFolder = ''
        self.strTestResultFolder = ''
        self.strProductSettingFile = ''
        self.strTestRunnerClass = ''
        self.lstTargetTestCase = []
        self.lstTargetTestSuite = []
        self.lstExcludedTestSuite = []
        self.lstExcludedTestCase = []
        self.isDryRun = False
        self.intLogLevel = logging.DEBUG
        self.isRealTimeReport = 1
        self.isEmailNotifyEnable = 0
        self._objEmailNotifyConfig = EmailNotifyConfig()
        self.isBypassSyntaxCheck = 0
        self.strTestRunName = ''
        self.strUser = ''

    def loadFromIniFile(self, strIniPath):
        self.strConfigFile = strIniPath
        c = ConfigParser.ConfigParser()
        c.optionxform = str  # option name will be "case sensitive"
        c.readfp(open(strIniPath))
        dicTestwareConfig = {}
        for strOption in c.options('TestwareConfig'):
            dicTestwareConfig[strOption] = c.get(
                'TestwareConfig', strOption).strip()
        self.strProductName = dicTestwareConfig['ProductName'].strip()
        self.strTestCaseRootFolder = dicTestwareConfig[
            'TestCaseRootFolder'].strip()
        self.strTestResultFolder = dicTestwareConfig[
            'TestResultFolder'].strip()

        for strTestSuite in dicTestwareConfig.get('TestSuites', '').split(','):
            strTestSuite = strTestSuite.strip()
            if strTestSuite:
                self.lstTargetTestSuite.append(strTestSuite)

        for strTestCaseId in dicTestwareConfig.get('TestCases', '').split(','):
            strTestCaseId = strTestCaseId.strip()
            if strTestCaseId:
                self.lstTargetTestCase.append(strTestCaseId)

        for strTestSuite in dicTestwareConfig.get('TestSuitesExcluded', '').split(','):
            strTestSuite = strTestSuite.strip()
            if strTestSuite:
                self.lstExcludedTestSuite.append(strTestSuite)

        for strTestCaseId in dicTestwareConfig.get('TestCasesExcluded', '').split(','):
            strTestCaseId = strTestCaseId.strip()
            if strTestCaseId:
                self.lstExcludedTestCase.append(strTestCaseId)

        self.strProductSettingFile = dicTestwareConfig.get(
            'ProductSettingFile', '').strip()
        self.strTestRunnerClass = dicTestwareConfig.get(
            'TestRunnerClass', '').strip()

        self._setValue(dicTestwareConfig, 'EnableRealTimeReport',
                       'isRealTimeReport', int)
        self._setValue(dicTestwareConfig, 'BypassSyntaxCheck',
                       'isBypassSyntaxCheck', int)

        if c.has_section('EmailNotify'):
            self._loadEmailNotifySection(c)

    def _setValue(self, dic, key, attr, handler=None):
        value = dic.get(key, '').strip()
        if value:
            if handler:
                value = handler(value)
            setattr(self, attr, value)

    def debugPrint(self):
        lst = []
        for s in dir(self):
            if callable(getattr(self, s)):
                continue
            if isinstance(getattr(self, s), EmailNotifyConfig):
                lst.append(getattr(self, s).debugPrint())
                continue
            if s[:2] == '__': continue
            lst.append('  %s = %s' % (s, getattr(self, s)))
        return '\n'.join(lst)

    def _loadEmailNotifySection(self, objConfigParser):
        '''
        [EmailNotify]
        Enable=0
        SmtpServer=msa.hinet.net
        SmtpFrom=cpm_automation@msa.hinet.net
        Sender="CPM_Automation" <aaa@abc.com.tw>
        To=aaa@abc.com.tw;abc@gmail.com
        Cc=aaa@bbb.com;bbb@ccc.com
        Subject=[CPM Automation] Build %(build)s-%(platform)s  (%(fail)s/%(total)s)
        IncludeReport=1
        '''
        dicTmp = {}
        for strOption in objConfigParser.options('EmailNotify'):
            dicTmp[strOption] = objConfigParser.get(
                'EmailNotify', strOption, raw=True).strip()
        self._setValue(dicTmp, 'Enable', 'isEmailNotifyEnable', int)

        strBuf = dicTmp.get('SmtpServer', '').strip()
        if strBuf:
            self._objEmailNotifyConfig.strSmtpServer = strBuf

        strBuf = dicTmp.get('SmtpFrom', '').strip()
        if strBuf:
            self._objEmailNotifyConfig.strSmtpFrom = strBuf

        strBuf = dicTmp.get('Sender', '').strip()
        if strBuf:
            self._objEmailNotifyConfig.strSender = strBuf

        strBuf = dicTmp.get('IncludeReport', '').strip()
        if strBuf:
            self._objEmailNotifyConfig.isIncludeReport = int(strBuf)

        strBuf = dicTmp.get('To', '').strip()
        if strBuf:
            self._objEmailNotifyConfig.lstTo = [x.strip(
            ) for x in re.split(',|;', strBuf) if x.strip()]

        strBuf = dicTmp.get('Cc', '').strip()
        if strBuf:
            self._objEmailNotifyConfig.lstCc = [x.strip(
            ) for x in re.split(',|;', strBuf) if x.strip()]

    def getEmailNotifyConfig(self):
        return self._objEmailNotifyConfig
