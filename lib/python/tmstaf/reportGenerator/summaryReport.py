import cgi

FOOTER = 'Powerd by TMSTAF<br>TMSTAF Support: Chien-Chih Lo'


class LineWriter:
    def __init__(self, writer):
        self.writer = writer

    def write(self, s):
        self.writer.write(s)
        self.writer.write('\r\n')

    def __getattr__(self, name):
        return getattr(self.writer, name)


class HtmlSummaryReport:

    def __init__(self, strFooter=FOOTER):
        self.strFooter = strFooter
        self.lstHeader = []
        self.intNumOfCase, self.intPass, self.intFail, self.intCrash, self.intElapsedTime = 0, 0, 0, 0, 0
        self.lstResult = []

    def addHeaderInfo(self, strTitle, strContent):
        self.lstHeader.append((strTitle, strContent))

    def writeHeaderBlock(self, f):
        if not self.lstHeader:
            return
        f.write('<table border="0" cellpadding="3" cellspacing="0" width="70%">')
        for strTitle, strContent in self.lstHeader:
            f.write('<tr><td width="6%%"><b>%s:</b></td><td>%s</td></tr>' %
                    (cgi.escape(strTitle), cgi.escape(strContent)))
        f.write('</table>')

    def setResultSummary(self, intNumOfCase, intPass, intFail, intCrash, intElapsedTime):
        self.intNumOfCase, self.intPass, self.intFail, self.intCrash, self.intElapsedTime = intNumOfCase, intPass, intFail, intCrash, intElapsedTime

    def writeResultSummary(self, f):
        f.write('<table border="1" cellpadding="5" cellspacing="0" width="350px">')
        f.write('<tr><td>Total</td><td>Passes</td><td>Fails</td><td>Crashes</td><td>Elapsed Time</td></tr>')
        f.write('<tr><td>%s</td>' % self.intNumOfCase)
        f.write('<td>%s</td>' % self.intPass)
        if self.intFail:
            f.write('<td><font color="red">%s</font></td>' % self.intFail)
        else:
            f.write('<td>%s</td>' % self.intFail)
        if self.intCrash:
            f.write('<td><font color="blue">%s</font></td>' % self.intCrash)
        else:
            f.write('<td>%s</td>' % self.intCrash)
        f.write('<td>%s</td>' % self._getStrTime(self.intElapsedTime))
        f.write('</tr></table><br>')

    def addTestResult(self, strSuiteName, strCaseName, dicResult):
        self.lstResult.append((strSuiteName, strCaseName, dicResult))

    def writeTestResult(self, f):
        f.write('''<div>
        <span class="icon-sample">&radic;:&nbsp;Pass</span>
        <span class="icon-sample"><font color="red">X</font>:&nbsp;Fail</span>
        <span class="icon-sample"><font color="blue">C</font>:&nbsp;Crash</span>
        </div>''')
        f.write('<hr>')
        f.write('<table border="0" cellpadding="4" cellspacing="0" width="70%">')
        f.write('<tr>')
        f.write('<td width="5%">#</td><td width="10%">Result</td><td width="20%">Name</td><td width="5%">Elapsed Time</td><td>Title</td></tr>')
        count = 0
        for strSuiteName, strCaseName, dicResult in self.lstResult:
            count += 1
            strName = '%s\\%s' % (
                cgi.escape(strSuiteName), cgi.escape(strCaseName))
            if dicResult['passes']:
                strResult = '&radic;'
            elif dicResult['fails']:
                strResult = '<font color="red">X</font>'
                strName = '<font color="red">%s</font>' % strName
            elif dicResult['crashes']:
                strResult = '<font color="blue">C</font>'
                strName = '<font color="blue">%s</font>' % strName
            f.write('<tr>')
            strTitle = cgi.escape(dicResult['title'].replace('\n', '. '))
            for v in (count, strResult):
                f.write('<td align="middle" class="smallWord">%s</td>' % v)
            for v in (strName, self._getStrTime(dicResult['elapsedTime']), strTitle):
                f.write('<td class="smallWord">%s</td>' % v)
            f.write('</tr>')
        f.write('</table>')

    def _getStrTime(self, intSeconds, showMsecs=0):
        i = int(intSeconds)
        s = '%.2d:%.2d:%.2d' % (i / 3600, (i % 3600) / 60, i % 60)
        if showMsecs:
            msecs = (intSeconds - long(intSeconds)) * 1000
            s += '.%03d' % msecs
        return s

    def writeFailCases(self, f):
        lstOutput = []
        for strSuiteName, strCaseName, dicResult in self.lstResult:
            strName = '%s\\%s' % (
                cgi.escape(strSuiteName), cgi.escape(strCaseName))
            if dicResult['fails']:
                lstOutput.append('<div class="failed-case"><font color="red">&nbsp;&nbsp;%s</font>&nbsp;&nbsp;%s</div>' % (strName, dicResult['title']))
            if dicResult['crashes']:
                lstOutput.append('<div class="failed-case"><font color="blue">&nbsp;&nbsp;%s</font>&nbsp;&nbsp;%s</div>' % (strName, dicResult['title']))
        if not lstOutput:
            return
        f.write('<div class="title">Failed test cases:</div>')
        for s in lstOutput:
            f.write(s)
        f.write('<br><br>')

    def writeCss(self, f):
        f.write('''<style>
        body {font-family: "Verdana", "Arial", "Helvetica", "sans-serif"; font-size: 10pt;}
        td {white-space: nowrap; font-size: 10pt;}
        .smallWord {font-size: 8pt;}
        .largeWord {font-size: 12pt;}
        .title {margin-bottom:10pt;}
        .icon-sample {margin-right:10pt; white-space: nowrap; font-size: 8pt;}
        .failed-case {white-space: nowrap; font-size: 8pt;}
        .footer {font-size: 8pt;}
        </style>''')

    def writeFooter(self, f):
        f.write('<div class="footer">%s</div>' % self.strFooter)

    def write(self, writer):
        f = LineWriter(writer)
        f.write('<html><body bgcolor="#ffffff">')
        self.writeCss(f)
        self.writeHeaderBlock(f)
        f.write('<br>')
        self.writeResultSummary(f)
        f.write('<hr><br>')
        self.writeFailCases(f)
        self.writeTestResult(f)
        f.write('<hr><br>')
        self.writeFooter(f)
        f.write('</body></html>')
        f.close()


def genHtmlSummaryReport(fileObj, objTestResult, lstHeaderInfo=None):
    from tmstaf import tmstafMain
    strFooter = 'Powerd by TMSTAF %s<br>TMSTAF Support: Chien-Chih Lo' % tmstafMain.VERSION
    obj = HtmlSummaryReport(strFooter)
    if lstHeaderInfo:
        for k, v in lstHeaderInfo:
            obj.addHeaderInfo(k, v)
    obj.setResultSummary(objTestResult.intNumOfCase, objTestResult.intPassed, objTestResult.intFailed, objTestResult.intCrashed, objTestResult.intElapsedTime)
    for strSuiteName, strCaseName, dicResult in objTestResult.getAllTestCase():
        obj.addTestResult(strSuiteName, strCaseName, dicResult)
    obj.write(fileObj)
    del obj


def test():
    obj = HtmlSummaryReport()
    obj.addHeaderInfo('Product Info', '123')
    obj.addHeaderInfo('Computer Name', '444123')
    obj.setResultSummary(4, 3, 1, 1, 8641)
    obj.addTestResult('test', '0001', {'passes': 1, 'fails': 0,
                                       'crashes': 0, 'elapsedTime': 145, 'title': 'test adfaf'})
    obj.addTestResult('test', '0002', {'passes': 1, 'fails': 0,
                                       'crashes': 0, 'elapsedTime': 5, 'title': 'test adfaf1111'})
    obj.addTestResult('test', '0003', {'passes': 0, 'fails': 1,
                                       'crashes': 0, 'elapsedTime': 245, 'title': 'test adfaf222 ' * 20})
    obj.addTestResult('test', '0004', {'passes': 0, 'fails': 0,
                                       'crashes': 1, 'elapsedTime': 345, 'title': 'test adfaf333'})
    obj.addTestResult('test', '0005', {'passes': 1, 'fails': 0,
                                       'crashes': 0, 'elapsedTime': 45, 'title': '11111'})
    obj.write(open('report.html', 'wb'))


if __name__ == '__main__':
    test()
