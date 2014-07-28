#!/usr/bin/env python
#coding=utf-8

# *************************************************************
# * Title:  txt-to-xml
# * $Revision: 1.0.2(Dev)
# * $Author: Tony Zhang
# *************************************************************
import sys
import os
import shutil
lp = os.linesep
notExecuted = False
# ====================
# Definition name: outPutXML
# Input: String FileName, String DefineID, String targetID
# output: none
# Description: Search the result of assigned defineID and targetID,
#              and generate an ouput.xml with another definition writeXML()
# ====================


def outPutXML(tfile, defineID, targetID, workFolder):
    global notExecuted
    print "Result file is " + tfile
    print "Define ID is " + defineID
    print "Target ID is " + targetID
    print "Work Folder is " + workFolder
    haveResult = False
    result = ""
    # Check if the result file exists
    if not os.path.exists(tfile):
        notExecuted = True
        print "Can't Find Result File"
    # if the result file exists, then parse this file
    else:
        resultFile = file(tfile, "r")
        for eachLine in resultFile.readlines():
            eachLine.strip()
            if eachLine.find(defineID) != -1:
                if targetID == "" or eachLine.find(targetID) != -1:
                    if eachLine.find(":") != -1:
                        lineList = eachLine.split(":")
                        result = lineList[len(lineList) - 1]
                    else:
                        lineList = eachLine.split(",")
                        result = lineList[len(lineList) - 1]
                    haveResult = True
        resultFile.close()
        if haveResult == False:
            result = "NT"
        result = result.strip()
        print eachLine
        print "Result: " + result
        writeXML(defineID, targetID, result, workFolder)

# =====================
# Definition Name: writeXML
# Input: String defineID,String targetID,String result
# Output: None
# Description: Generate an output.xml in the current folder
# =====================


def writeXML(defineID, targetID, result, workFolder):
    global notExecuted
    outFileName = "output.xml"
    errCnt = 0
    warningCnt = 0
    if cmp(result.upper(), "PASS") == 0 or cmp(result.upper(), "P") == 0:
        errCnt = 0
        warningCnt = 0
    elif cmp(result.upper(), "NT") == 0:
        notExecuted = True
    else:
        errCnt = 1
        warningCnt = 0
    outputFile = file(outFileName, "w")
    # Write the output.xml
    if notExecuted == True:
        outputFile.write("<?xml version=\"1.0\" encoding=\"UTF-16\"?>" + lp)
    else:
        outputFile.write("<?xml version=\"1.0\" encoding=\"UTF-8\"?>" + lp)

    outputFile.write("<ResultElement TestItem=\"PerlTest\">" + lp)
    outputFile.write("<ErrorCount>" + repr(errCnt) + "</ErrorCount>" + lp)
    outputFile.write(
        "<WarningCount>" + repr(warningCnt) + "</WarningCount>" + lp)
    outputFile.write("  <Incident>" + lp)
    outputFile.write("    <Message>some unexpected result</Message>" + lp)
    outputFile.write("    <Severity>Error</Severity>" + lp)
    outputFile.write("    <Detail>" + lp)
    outputFile.write("      <TestName>function main()</TestName>" + lp)
    outputFile.write(
        "      <Info>some additional info; eg. stacktrace</Info>" + lp)
    outputFile.write("    </Detail>" + lp)
    outputFile.write("  </Incident>" + lp)
    outputFile.write("  <Incident>" + lp)
    outputFile.write("    <Message>some warning message</Message>" + lp)
    outputFile.write("    <Severity>Warning</Severity>" + lp)
    outputFile.write("    <Detail>" + lp)
    outputFile.write("      <TestName>function main()</TestName>" + lp)
    outputFile.write(
        "      <Info>some additional info; eg. stacktrace</Info>" + lp)
    outputFile.write("    </Detail>" + lp)
    outputFile.write("  </Incident>" + lp)
    outputFile.write("</ResultElement>" + lp)
    outputFile.close()
    # Get the SCTM Result folder
    # SCTMResultFolder=os.getenv("SCTM_EXEC_RESULTSFOLDER")
    SCTMResultFolder = workFolder
    print "SCTMResultFolder is" + SCTMResultFolder
    # Copy the output.xml to SCTM Result folder
    shutil.copy("output.xml", SCTMResultFolder)


if __name__ == '__main__':
    # Get the parameters
    '''if len(sys.argv)<3:
        print "Error: You can't assign enough parameters."
        sys.exit()
    elif len(sys.argv)==5:
        # The first parameter is the name of this script
        tfile=sys.argv[2]
        workFolder=sys.argv[3]
        defineID=sys.argv[4]
        targetID=os.getenv("#sctm_execdef_name")
        outPutXML(tfile,defineID,targetID,workFolder)
    else:
        print "Error: You have assigned too many parameters"
        print sys.argv
        sys.exit()'''
    # resultPath workPath defineID
    tfile = sys.argv[1]
    workFolder = sys.argv[2]
    defineID = sys.argv[3]
    targetID = os.getenv("#sctm_execdef_name")
    outPutXML(tfile, defineID, targetID, workFolder)
