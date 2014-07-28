'''
How to generate .py test case file:
1. Use TCMT "Check Out" feature to download the excel file.
2. Change cell format of these three column "Test Case Title", "Description" and "Expected Result" to "General Format"
3. Save the excel file as "Tab-separated" txt file.
4. Run this module to parse the txt file and create all test cases.
5. You can customize createTestCase() as you need.
'''
import logging
import sys
import os
import re

TCID = 'TCID'
TITLE = 'TITLE'
DESCRICTION = 'DESCRICTION'
EXPECTED_RESULT = 'EXPECTED_RESULT'
DEFINED_ID = 'DEFINED_ID'
g_dicTargetFields = {'tcid': TCID, 'test case title': TITLE, 'description': DESCRICTION,
                     'expected result': EXPECTED_RESULT, 'userdefid': DEFINED_ID}


def parseHeaderLine(line):
    lstFields = line.split('\t')[:-1]
    logging.debug('Number of fields: %s', len(lstFields))
    logging.debug(lstFields)
    dicOutput = {}
    index = 0
    for strField in lstFields:
        if strField.lower() in g_dicTargetFields:
            dicOutput[g_dicTargetFields[strField.lower()]] = index
        index += 1
    return len(lstFields), dicOutput


def readOneRecord(intFieldCount, f):
    lstBuf = []
    lstFields = []
    insideDoubleQuote = 0
    for line in f:
        index = 0
        while index < len(line):
            if insideDoubleQuote:
                obj = re.search('[^"]"\t', line[index:])
                if obj:
                    offset = index + obj.end() - 1
                    insideDoubleQuote = 0
                else:
                    offset = -1
            else:
                offset = line.find('\t', index)
            if offset < index:
                break
            if line[offset + 1:offset + 2] == '"':
                insideDoubleQuote = 1
            s = ''.join(lstBuf) + line[index:offset]
            lstBuf = []
            lstFields.append(trimDQuote(s))
            if len(lstFields) == intFieldCount:
                return lstFields
            index = offset + 1
        lstBuf.append(line[index:])
    return lstFields


def createTestCase(strPath, strDefinedId, strModulePath, strTitle, strDesc, strExpectedResult):
    f = open(strPath, 'wb')
    f.write('"""\r\n')
    f.write('Description:\r\n')
    f.write(strDesc)
    f.write('\r\n\r\n')
    f.write('Expected Result:\r\n')
    f.write(strExpectedResult)
    f.write('\r\n\r\n')
    f.write('"""\r\n')
    f.write("self.setModule(r'%s')\r\n" % strModulePath)
    f.write("self.setTitle(r'''%s''')\r\n\r\n" % strTitle)
    f.write("#self.setScenario('_xxx.py')\r\n\r\n")
    f.write("#strIniFile='%s.ini'\r\n" % strDefinedId)
    f.write("strRegFile='%s.reg'\r\n" % strDefinedId)
    f.write("#strSampleVirusFile=''\r\n")
    f.write("#strSampleVirusFilePasswd=''\r\n")
    f.write("#strVirusLogFile='%s_v.log'\r\n" % strDefinedId)
    f.write("#strSpywareLogFile='%s_s.log'\r\n" % strDefinedId)
    f.write("#strSpywareDetailLogFile='%s_sd.log'\r\n" % strDefinedId)
    f.close()


def main(strInputFile, strOutputDir):
    inFile = open(strInputFile, 'rb')
    line = inFile.readline()
    intFieldCount, dicTargetFields = parseHeaderLine(line)
    logging.info('dicTargetFields: %s', dicTargetFields)
    for i in range(39):  # escape first 39 lines
        inFile.readline()
    while 1:
        lstRecord = readOneRecord(intFieldCount, inFile)
        if not lstRecord:
            break
        strTcid = lstRecord[dicTargetFields[TCID]]
        if strTcid[:1] == '[' and strTcid[-1:] == ']':
            strModulePath = lstRecord[dicTargetFields[TITLE]]
            continue
        if not lstRecord[dicTargetFields[DEFINED_ID]]:
            continue
        strDefinedId = lstRecord[dicTargetFields[DEFINED_ID]]
        strTitle = lstRecord[dicTargetFields[TITLE]]
        strDesc = lstRecord[dicTargetFields[DESCRICTION]]
        strExpectedResult = lstRecord[dicTargetFields[EXPECTED_RESULT]]
        strPath = strOutputDir + '/%s.py' % strDefinedId
        createTestCase(strPath, strDefinedId, strModulePath,
                       strTitle, strDesc, strExpectedResult)
        logging.info('create test case: %s' % strDefinedId)


def trimDQuote(s):
    s = s.strip()
    s = s.strip('"')
    return s.replace('""', '"')

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    if len(sys.argv) != 3:
        logging.info('Syntax:\r\n python %s <INPUT_FILE> <OUTPUT_DIR>' %
                     __file__)
        sys.exit(1)
    strInputFile = sys.argv[1]
    strOutputDir = sys.argv[2]
    if not os.path.exists(strOutputDir):
        os.mkdir(strOutputDir)
    main(strInputFile, strOutputDir)
