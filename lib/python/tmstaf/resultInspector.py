class ResultInspector:

    def __init__(self, isMatchAll=0):
        self._isMatchAll = isMatchAll
        self._lstCompareRule = []
        self._hasResult = 0
        self._result = None
        self._stdout = None
        self._isCompareStdout = False

    def isCompareStdout(self):
        return self._isCompareStdout

    def __str__(self):
        if not self._lstCompareRule:
            return 'N/A'
        lst = []
        for f, data in self._lstCompareRule:
            lst.append('%s' % str(data))
        if self._isMatchAll:
            strResult = ' AND '.join(lst)
        else:
            strResult = ' OR '.join(lst)
        if f == self._isEqual and len(lst) > 1:
            if self._isCompareStdout:
                strResult = 'stdout = ' + strResult
            else:
                strResult = 'Result = ' + strResult
        if f == self._isNotEqual:
            strResult = '!= ' + strResult
        if f == self._isContain:
            if self._isCompareStdout:
                strResult = 'stdout contains "%s"' % (strResult)
            else:
                strResult = 'Result contains "%s"' % (strResult)
        return '%s' % (strResult)

    def failUnlessContain(self, strKeyword):
        self._lstCompareRule.append((self._isContain, strKeyword))

    def failUnlessEqual(self, data):
        self._lstCompareRule.append((self._isEqual, data))

    def failUnlessNotEqual(self, data):
        self._lstCompareRule.append((self._isNotEqual, data))

    def failUnlessStdoutContain(self, strKeyword):
        self._isCompareStdout = True
        self._lstCompareRule.append((self._isContain, strKeyword))

    def failUnlessStdoutEqual(self, data):
        self._isCompareStdout = True
        self._lstCompareRule.append((self._isEqual, data))

    def getCompareRules(self):
        return self._lstCompareRule

    def setResult(self, result):
        self._result = result
        self._hasResult = 1

    def setStdout(self, strStdout):
        self._stdout = strStdout

    def getResult(self):
        if self._isCompareStdout:
            return self._stdout
        else:
            return self._result

    def getStdout(self):
        return self._stdout

    def isPassed(self):
        if not self._lstCompareRule:
            return 1
        if not self._hasResult:
            return 0
        if self._isCompareStdout:
            isSuccess, result = self.handleStdout(self._stdout)
        else:
            isSuccess, result = self.handleResult(self._result)
        if not isSuccess:
            return 0
        if self._isMatchAll:  # AND condition
            for f, s in self._lstCompareRule:
                if not f(s, result):
                    return 0
            return 1
        else:  # OR condition
            for f, s in self._lstCompareRule:
                if f(s, result):
                    return 1
            return 0

    def handleResult(self, result):
        # this method can be overwrited by subclass
        isSuccess = 1
        return isSuccess, result

    def handleStdout(self, strStdout):
        # this method can be overwrited by subclass
        isSuccess = 1
        return isSuccess, strStdout

    def _isContain(self, strKeyword, strTarget):
        if strTarget.find(strKeyword) >= 0:
            return 1
        return 0

    def _isEqual(self, a, b):
        return a == b

    def _isNotEqual(self, a, b):
        return a != b
