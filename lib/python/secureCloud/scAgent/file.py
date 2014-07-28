import logging
import logging.handlers
import ConfigParser
import platform

def setLogFile(logName,strLogLevel,strLog):
        logFile = logging.getLogger(strLog)
        logFile.setLevel(strLogLevel)
        logFile_hdlr = logging.handlers.RotatingFileHandler(logName, maxBytes=10000, backupCount=5)
        formatter = logging.Formatter('%(asctime)s [%(module)s] %(message)s')
        logFile_hdlr.setFormatter(formatter)
        logFile.addHandler(logFile_hdlr)       
        return logFile
def initLogfile(logName,logLevel):
    logger = logging.basicConfig(filename=logName,
                                 level=logLevel,
                                 format='%(asctime)s %(levelname)s : %(message)s -- @(%(lineno)d [%(module)s])'
                                 )

 
 
def write_sctm_report(path,tc_title,testResult):
        logfileName=path+'result.log'
        f = file(logfileName, 'a') # open for 'w'riting
        if testResult==0: 
         result = "P"
        else:
         result = "F"
        f.write('%s %s\n'%(tc_title,result))
         # write text to file
        f.close() # close the file        