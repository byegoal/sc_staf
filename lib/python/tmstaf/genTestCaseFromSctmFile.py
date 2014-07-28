'''
How to generate .py test case file:
1. Login SCTM
2. Open the left panel and go to [Help]->[Tools]->[SCTM Import/Export Tool]
3. Login "SilkCentral Test Manager Import/Export System"
4. Choose Project -> Choose Test Container -> Choose Folders
5. Press "ExportOnly" button and save the excel file
6. Save the excel file as "Tab-separated" txt file.
7. Run lib\python\tmstaf\genTestCaseFromSctmFile.py
8. It will parse the input txt file and create all test cases in output directory.

Note: Your test case must add a custom parameter, DefineID, first.
'''
import logging
import sys
import os
import re
import util

g_lstFields = [
    'Parent ID',
    'NodeID',
    'Name',
    'Description',
    'Test Type',
    'Attribute',
    'Parameter',
    'Test Type Properties'
]


class TestCase:
    def __init__(self, lstFields):
        self.strParentId = lstFields[0]
        self.strNodeId = lstFields[1]
        self.strName = lstFields[2]
        self.strDescription = util.removeHtmlTag(lstFields[3])
        self.strTestType = lstFields[4]
        self.strAttribute = lstFields[5]
        self.strParameter = lstFields[6]
        self.strProperties = lstFields[7]

    def createFile(self, strModulePath, strOutputDir):
        objRex = re.search('DefineID[\s]*=[\s]*(\w*)', self.strParameter)
        if not objRex:
            objRex = re.search('Defined ID[\s]*=[\s]*(\w*)', self.strParameter)
            if not objRex:
                raise RuntimeError('Test case "%s" does NOT contain DefineID' %
                                   self.strName)
        self.strDefineId = obj = objRex.group(1)
        strPath = os.path.join(strOutputDir, '%s.py' % self.strDefineId)
        f = open(strPath, 'wb')
        f.write('"""\r\n')
        f.write(self.strDescription)
        f.write('\r\n\r\n')
        f.write('"""\r\n')
        f.write("self.setModule(r'%s')\r\n" % strModulePath)
        f.write("self.setTitle(r'''%s''')\r\n\r\n" % self.strName)
        f.write("#self.setScenario('_xxx.py')\r\n\r\n")
        f.write("#DefineID=%s\r\n\r\n" % self.strDefineId)
        f.close()
        logging.debug('create %s', strPath)


def parseHeaderLine(f):
    logging.info('Project: %s', f.readline()[:-2].split('\t')[2])
    logging.info('Test Container: %s', f.readline()[:-2].split('\t')[2])
    strLine = f.readline()[:-2]
    lstFields = strLine.split('\t')
    if len(lstFields) != len(g_lstFields):
        raise RuntimeError('Number of fields does NOT match')


def readOneRecord(intFieldCount, f):
    lstBuf = []
    lstFields = []
    insideDoubleQuote = 0
    for line in f:
        index = 0
        while index < len(line):
            if insideDoubleQuote:
                obj = re.search('[^"]*"\t', line[index:])
                if obj:
                    offset = index + obj.end() - 1
                    insideDoubleQuote = 0
                else:
                    obj = re.search('[^"]"\r\n', line[index:])
                    if obj:
                        offset = index + obj.end() - 2
                        insideDoubleQuote = 0
                    else:
                        offset = -1
            else:
                offset = line.find('\t', index)
                if len(lstFields) + 1 == intFieldCount and line[index:] == '\r\n':
                    lstFields.append('')
                    return lstFields
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


def trimDQuote(s):
    s = s.strip()
    s = s.strip('"')
    return s.replace('""', '"')


def generate(strInputFile, strOutputDir):
    inFile = open(strInputFile, 'rb')
    parseHeaderLine(inFile)
    strModulePath = ''
    intCount = 0
    while 1:
        lstFields = readOneRecord(len(g_lstFields), inFile)
        if not lstFields:
            break
        objTestCase = TestCase(lstFields)
        if objTestCase.strTestType == 'Test Folder':
            strModulePath = objTestCase.strName
            logging.debug('[Test Folder] %s', strModulePath)
            continue
        elif objTestCase.strTestType == 'WshTest':
            try:
                objTestCase.createFile(strModulePath, strOutputDir)
            except RuntimeError, e:
                logging.error('%s' % e)
                continue
            intCount += 1
        elif objTestCase.strTestType == '':
            continue
        else:
            logging.error('Unknown type:\r\n%s' % ('\r\n'.join(
                ['  ' + repr(s) for s in lstFields])))
            continue
    logging.info('--\r\nTotal test cases: %s', intCount)


def main():
    logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    if len(sys.argv) != 3:
        logging.info('Syntax:\r\n python %s <INPUT_FILE> <OUTPUT_DIR>' %
                     __file__)
        sys.exit(1)
    strInputFile = sys.argv[1]
    strOutputDir = sys.argv[2]
    if not os.path.exists(strOutputDir):
        os.makedirs(strOutputDir)
    generate(strInputFile, strOutputDir)

if __name__ == '__main__':
    main()
