import os
import logging


class ITestCaseLoader:
    def __init__(self, strRootPath):
        self.strRootPath = strRootPath
        self._dicSuites = {}
        self._dicTestCases = {}
        self._load()
        self._dicExcludeTestSuite = {}
        self._dicExcludeTestCase = {}

    def setExcludeList(self, lstTestSuite, lstTestCase):
        for strSuite in lstTestSuite:
            self._dicExcludeTestSuite[strSuite] = 1
        for strTestCase in lstTestCase:
            self._dicExcludeTestCase[strTestCase] = 1

    def _load(self):
        lstSuite = os.listdir(self.strRootPath)
        for strSuite in lstSuite:
            strPath = os.path.join(self.strRootPath, strSuite)
            if not os.path.isdir(strPath):
                continue
            if self.ignore(strSuite):
                continue
            dicOutput = self._loadTestSuite(strSuite, strPath)
            self._dicSuites[strSuite] = dicOutput

    def _loadTestSuite(self, strSuite, strSuitePath):
        dicOutput = {}
        lstName = os.listdir(strSuitePath)
        lstName.sort()
        for strName in lstName:
            if self.ignore(strName):
                continue
            strName, strCasePath = self.getTestCase(strSuitePath, strName)
            if strCasePath:
                dicOutput[strName] = strCasePath
                self._dicTestCases[strName] = strSuite
        return dicOutput

    def get(self, lstTargetTestSuite=(), lstTargetTestCase=()):
        if not lstTargetTestSuite and not lstTargetTestCase:
            lstSuites = self._dicSuites.keys()
            lstSuites.sort()
            for strSuite in lstSuites:
                if strSuite in self._dicExcludeTestSuite:
                    logging.debug('"%s" excluded by user', strSuite)
                    continue
                lstTestCases = self._dicSuites[strSuite].keys()
                lstTestCases.sort()
                for strName in lstTestCases:
                    if strName in self._dicExcludeTestCase:
                        logging.debug('"%s" excluded by user', strName)
                        continue
                    strPath = self._dicSuites[strSuite][strName]
                    yield strSuite, strName, os.path.join(self.strRootPath, strSuite, strPath)
        else:
            for strSuite in lstTargetTestSuite:
                if strSuite in self._dicExcludeTestSuite:
                    logging.debug('"%s" excluded by user', strSuite)
                    continue
                if strSuite not in self._dicSuites:
                    raise RuntimeError('test suite "%s" does NOT exist.' %
                                       strSuite)
                lstTestCases = self._dicSuites[strSuite].keys()
                lstTestCases.sort()
                for strName in lstTestCases:
                    if strName in self._dicExcludeTestCase:
                        logging.debug('"%s" excluded by user', strName)
                        continue
                    strPath = self._dicSuites[strSuite][strName]
                    yield strSuite, strName, os.path.join(self.strRootPath, strSuite, strPath)
            for strTestCase in lstTargetTestCase:
                if strTestCase not in self._dicTestCases:
                    raise RuntimeError('test case "%s" does NOT exist.' %
                                       strTestCase)
                if strTestCase in self._dicExcludeTestCase:
                    logging.debug('"%s" excluded by user', strTestCase)
                    continue
                strSuite = self._dicTestCases[strTestCase]
                if strSuite in lstTargetTestSuite:
                    continue
                if strSuite in self._dicExcludeTestSuite:
                    logging.debug('"%s" excluded by user', strSuite)
                    continue
                strPath = self._dicSuites[strSuite][strTestCase]
                yield strSuite, strTestCase, os.path.join(self.strRootPath, strSuite, strPath)

    def ignore(self, strName):
        '''
        This method can be overwrited by sub-class
        '''
        return False

    def getTestCase(self, strSuitePath, strCaseName):
        raise NotImplementedError('%s.getTestCase() must be implemented.' %
                                  self.__class__.__name__)


class PythonTestCaseLoader(ITestCaseLoader):
    _dicExclusion = {'CVS': 'CVS Folder', '.svn': 'SVN Folder'}

    def ignore(self, strName):
        if strName[:1] == '_' or strName in self._dicExclusion:
            return True
        return False

    def getTestCase(self, strSuitePath, strCaseName):
        strPath = os.path.join(strSuitePath, strCaseName)
        if os.path.isdir(strPath) and os.path.exists('%s/%s.py' % (strPath, strCaseName)):
            return strCaseName, os.path.join(strCaseName, strCaseName + '.py')
        else:
            strName, strExt = os.path.splitext(strCaseName)
            if strExt.lower() == '.py':
                return strName, strCaseName
        return None, None


def test():
    import sys
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(levelname)-8s %(message)s',
                        datefmt='%m-%d %H:%M')
    lstSuites = []
    lstCases = []
    if len(sys.argv) > 2:
        lstSuites = [s for s in sys.argv[2].split(',') if s]
    if len(sys.argv) > 3:
        lstCases = sys.argv[3].split(',')
    obj = PythonTestCaseLoader(sys.argv[1])
    count = 0
    for strSuite, strName, strPath in obj.get():
        print strSuite, strName, strPath
        count += 1
    print count
    raw_input('press Enter')

    obj.setExcludeList(['ZPFW_01', 'ZPFW_02', 'ZPFW_08'], [
        'AU_CL_03_0050', 'AU_CL_03_0080'])
    count = 0
    for strSuite, strName, strPath in obj.get():
        print strSuite, strName, strPath
        count += 1
    print count
    raw_input('press Enter')

    count = 0
    for strSuite, strName, strPath in obj.get(lstSuites, lstCases):
        print strSuite, strName, strPath
        count += 1
    print count
if __name__ == '__main__':
    test()
