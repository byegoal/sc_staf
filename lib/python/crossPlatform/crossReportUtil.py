"""
This is report module to create html report for email notify used.
"""


class LineWriter:
    """
    Output final data to file.
    """
    def __init__(self, writer):
        self.writer = writer

    def write(self, strLine):
        """
        Output line data to file
        """
        self.writer.write(strLine)
        self.writer.write('\r\n')

    def write2(self, strLine):
        """
        Output line data to file
        """
        self.writer.write(strLine)

    def __getattr__(self, name):
        return getattr(self.writer, name)


class CrossSummaryReport:
    """
    Class summary data report.
    """
    def __init__(self):
        self.lstHeader = []
        self.lstResultSummary = []
        self.lstFailedSummary = []
        self.lstCrashSummary = []
        self.lstFailedMachine = []

    def addHeaderInfo(self, strTitle, strContent):
        """
        Append header data into Header list.
        """
        self.lstHeader.append((strTitle, strContent))

    def writeHeaderBlock(self, objfile):
        """
        Write Header Block
        """
        if not self.lstHeader:
            return
        objfile.write('<table border="0" cellpadding="3" cellspacing="0" width="70%">')
        for strTitle, strContent in self.lstHeader:
            objfile.write('<tr><td width="6%%"><b>%s:</b></td><td>%s</td></tr>'
                          % (strTitle, strContent))
        objfile.write('</table>')

    def addResultSummary(self, strComputerName, strPlatform, strIP,
                         strNumOfCase, strPass, strFail, strCrash,
                         strElapsedTime, strStablePass, strStableFail):
        """
        Append Result into list
        """
        self.lstResultSummary.append((strComputerName, strPlatform, strIP,
                                      strNumOfCase, strPass, strStablePass, strFail, strStableFail, strCrash,
                                      strElapsedTime))

    def writeResultSummary(self, objfile):
        """
        Write summy result
        """
        objfile.write('<table border="1" cellpadding="5" cellspacing="0" width="500px">')
        objfile.write('<tr><td>Computer Name</td>'
                      '<td>Platform</td>'
                      '<td>IP</td>'
                      '<td>Total</td>'
                      '<td>Passes<br />(Stable/Developing)</td><td>Fails<br />(Stable/Developing)</td><td>Crashes</td><td>Elapsed Time</td></tr>')
        for strComputerName, strPlatform, strIP, strNumOfCase, strPass, strStablePass, strFail, \
            strStableFail, strCrash, strElapsedTime in self.lstResultSummary:
            if strCrash == "Unavailable":
                objfile.write2('<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td align="right">%s (Unavailable)</td>/'
                        % (strComputerName, strPlatform, strIP, strNumOfCase, strPass))

            else:
                objfile.write2('<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td><td align="right">%s (<FONT COLOR="blue">%s</FONT>/'
                        % (strComputerName, strPlatform, strIP, strNumOfCase, strPass, strStablePass))
                objfile.write('<font color="green">%s</font>)</td>' %
                    int(int(strPass) - int(strStablePass)))
            if int(strFail):
                objfile.write2('<td align="right"><font color="red">%s </font>(' % strFail)
                if strCrash == "Unavailable":
                    objfile.write('Unavailable)</td>')
                elif (strStableFail):
                    objfile.write('<font color="red">%s</font>/<font color="green">%s</font>)</td>' % (strStableFail, (int(strFail) - int(strStableFail))))
                else:
                    objfile.write('%s/<font color="green">%s</font>)</td>' % (strStableFail, (int(strFail) - int(strStableFail))))
            else:
                objfile.write('<td align="right">%s</td>' % strFail)
            if (strCrash):
                objfile.write('<td><font color="blue">%s</font></td>' %
                    strCrash)
            else:
                objfile.write('<td>%s</td>' % strCrash)
            objfile.write('<td>%s</td>' % (strElapsedTime))
            objfile.write('</tr>')
        objfile.write('</table><br>')

    def addFailSummary(self, failedCases, failedCount, failedCaseDescription, lstFailedMachine):
        self.lstFailedSummary.append((failedCases, failedCount,
            failedCaseDescription, lstFailedMachine))

    def addCrashSummary(self, failedCases, failedCount, failedCaseDescription, lstFailedMachine):
        self.lstCrashSummary.append((failedCases, failedCount,
            failedCaseDescription, lstFailedMachine))

    def writeFailSummary(self, f, lstSummary):
        f.write('<table border="1" cellpadding="5" cellspacing="0" width="500px">')
        f.write('<tr><td>failedCase</td><td>Count</td><td>Description</td><td>failedMachine</td></tr>')
        for failedCases, failedCount, failedCaseDescription, lstFailedMachine in lstSummary:
            f.write('<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td>' % (failedCases, failedCount, failedCaseDescription, lstFailedMachine))
            f.write('</tr>')
        f.write('</table><br>')

    def addFailedMachine(self, strMachineName, strPlatform):
        """
        Add fail machine info fail machine list
        """
        self.lstFailedMachine.append((strMachineName, strPlatform))

    def writeFailMachine(self, objfile):
        """
        Output fail machine to report
        """
        lstOutput = []
        for strMachineName, strPlatform in self.lstFailedMachine:
            lstOutput.append('<div class="failed-machine"><font color="red">&nbsp;&nbsp;%s</font> &nbsp;&nbsp;%s </div>' % (strMachineName, strPlatform))
        if not lstOutput:
            return
        objfile.write('<div class="title">Unavailable machine list:</div>')
        for item in lstOutput:
            objfile.write(item)
        objfile.write('<br><br>')

    def writeCss(self, objfile):
        """
        Output CSS to report
        """
        objfile.write('''<style>
        body {font-family: "Verdana", "Arial", "Helvetica", "sans-serif"; font-size: 10pt;}
        td {white-space: nowrap; font-size: 10pt;}
        .smallWord {font-size: 8pt;}
        .largeWord {font-size: 12pt;}
        .title {margin-bottom:10pt;}
        .icon-sample {margin-right:10pt; white-space: nowrap; font-size: 8pt;}
        .failed-machine {white-space: nowrap; font-size: 10pt;}
        </style>''')

    def write(self, writer):
        """
        Output data to report
        """
        objfile = LineWriter(writer)
        objfile.write('<html><body>')
        self.writeCss(objfile)
        self.writeHeaderBlock(objfile)
        objfile.write('<br>')
        self.writeResultSummary(objfile)
        objfile.write('<hr><br>')
        self.writeFailSummary(objfile, self.lstFailedSummary)
        objfile.write('<hr><br>')
##        self.writeFailSummary(objfile,self.lstCrashSummary)
##        objfile.write('<hr><br>')
        self.writeFailMachine(objfile)
        objfile.write('<hr><br>')
        from crossPlatform import autoServerMain
        objfile.write('<div class="footer"><font size="1">Powerd by %s %s<br>%s Support: OEM QA</font></div>' % (autoServerMain.PROJECTNAME,
                                                                                         autoServerMain.VERSION,
                                                                                         autoServerMain.PROJECTNAME))
        objfile.write('</body></html>')
        objfile.close()


def test():
    """
    test
    """
    obj = CrossSummaryReport()
    obj.addHeaderInfo('Product Info', '123')
    obj.addHeaderInfo('Computer Name', '444123')
    obj.addResultSummary('Machine1', 'WIN XP SP3', '140.113.112.1', 4,
        4, 3, "Unavailable", 0, 0, 8641)
    obj.addResultSummary('Machine2', 'WIN XP SP2', '140.103.13.19', 4,
        3, 2, 1, 1, 1, 10000)
    obj.addResultSummary(
        'Machine3', 'WIN XP SP4', '140.111.12.1', 88, 10, 6, 2, 2, 1, 500)
    obj.addResultSummary(
        'Machine4', 'WIN XP SP5', '140.119.18.1', 100, 3, 3, 1, 1, 4, 22)
    obj.addResultSummary('Machine5', 'WIN XP SP6', '140.113.172.1',
        2000, 4, 4, 3, 1, 1, 1231)
    obj.write(open('TestReport.html', 'wb'))

if __name__ == '__main__':
    test()
