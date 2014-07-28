import optparse
import logging
import os
import processUtil

if os.name == 'nt':
    STR_7ZA_EXE = os.path.join(
        os.path.dirname(__file__) or os.getcwd(), '7za.exe')
    if not os.path.exists(STR_7ZA_EXE):
        STR_7ZA_EXE = '7za.exe'


def unzipFile(strZipFile, strDestPath, strPassword=""):
    '''
    Call 7za.exe to decompress the input file
    @return: 0 means success; 2 means fail.
    '''
    if not os.path.exists(strDestPath):
        os.makedirs(strDestPath)
    if not os.path.exists(strZipFile):
        logging.error('Cannot find archive: "%s"' % strZipFile)
        return 2
    if os.name == 'nt':
        lstCmd = [STR_7ZA_EXE, 'x', '-aoa', '-o%s' % strDestPath,
                  '-p%s' % strPassword, strZipFile]
    else:
        lstCmd = ['unzip', '-P', strPassword, '-o', strZipFile,
                  '-d', strDestPath]
    logging.debug("Unzip command: %s", lstCmd)
    logging.info('Start to unzip "%s" ...' % strZipFile)
    objP = processUtil.TmProcess(lstCmd)
    strStdout = objP.readStdout()
    intReturnCode = objP.wait()
    if intReturnCode != 0:
        if intReturnCode == 1 and os.uname()[0].lower() == 'darwin' and os.uname()[2][:2] == '8.':
            #unzip 5.51 in MacOS 10.4.11 will return error 1 in some situation even though unzip file successfully
            return 0
        logging.error("Unzip failed. stdout:\n%s", strStdout)
        return 2
    else:
        if os.name == 'nt' and strStdout.find("Ok") == -1:
            logging.error("Unzip failed. stdout:\n%s", strStdout)
            return 2
        return 0


def zipFolder(strFolder, strArchivePath):
    '''
    Use 7za.exe or zip to compress a folder. For example: zipFolder('c:\result','result001.zip')
    '''
    if not os.path.exists(strFolder):
        raise RuntimeError("%s doesn't exist!" % strFolder)
    if os.path.exists(strArchivePath):
        os.remove(strArchivePath)
    strCwd = os.getcwd()
    try:
        if os.name == 'nt':
            lstCmd = [STR_7ZA_EXE, 'a', '-ssw', strArchivePath, strFolder]
        else:
            strPath, strFolder = os.path.split(strFolder)
            os.chdir(strPath)
            lstCmd = ['zip', '-q', '-r', strArchivePath, strFolder]
        logging.info('Compress command "%s"' % lstCmd)
        objP = processUtil.TmProcess(lstCmd)
        strStdout = objP.readStdout()
        intReturnCode = objP.wait()
        if intReturnCode == 0:
            if strStdout:
                logging.debug(strStdout)
        else:
            if strStdout:
                logging.info(strStdout)
    finally:
        os.chdir(strCwd)
    return intReturnCode


def main():
    import sys
    logging.basicConfig(level=logging.DEBUG, format='%(message)s')
    args = sys.argv[1:]
    strUsage = '\nUsage:\n zipUtil.py unzip ZipFile DestPath [Password] \n zipUtil.py zip ZipFolder ArchivePath'
    if len(args) == 0:
        logging.info(strUsage)
        return
    if args[0] == 'unzip':
        if len(args) == 3:
            intResult = unzipFile(args[1], args[2])
            logging.info("Unzip result: %s", intResult)
        elif len(args) == 4:
            intResult = unzipFile(args[1], args[2], args[3])
            logging.info("Unzip result: %s", intResult)
        else:
            logging.info(strUsage)
    elif args[0] == 'zip':
        if len(args) == 3:
            intResult = zipFolder(args[1], args[2])
            logging.info("Unzip result: %s", intResult)
        else:
            logging.info(strUsage)
    else:
        logging.info(strUsage)


if __name__ == '__main__':
    main()
