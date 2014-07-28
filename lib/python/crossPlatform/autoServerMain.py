"""
Automation main module, automatic check task queue, do task prepare,
do set task to central server then trigger testing after all machines
finish test case then collect test result and generate report send to
relative account.
"""
# common module
import os
import time
import logging
import datetime
import shutil
import sys

# cross platform lib
from crossPlatform.errorCode import ErrorautoServerMain as errASM
import crossPlatform.crossPlatformIni as cp_ini
import crossPlatform.crossPlatformUtil as cp_util
import crossPlatform.util

VERSION = 'v1.0.100401'
PROJECTNAME = 'TMSTAF Cross Platform'


def funcAutomationServerMain(strFileConfigIni):
    """
    The main cross platform test flow runnning on automation server.
    @type strFileConfigIni: String
    @param strFileConfigIni: the configure ini file.
    @return:
        errMMS.SUCCESS for ok,
        errMMS.FAIL for error.
    """
    # record start time
    cp_ini.g_strStartTime = str(datetime.datetime.now())
    #cp_ini.g_strModulePath = os.getcwd()

    # Prepare logging file
    logging.basicConfig(level=logging.DEBUG, datefmt='%H:%M:%S',
                        format='%(asctime)s [%(thread)d] %(message)s')

    # load configure ini
    cp_util.funcLoadConfigure(strFileConfigIni)

    # initial log file, the setting value define in above configure ini
    strLogFolder = cp_util.funcGetValue('Global', 'Log_Folder')
    if not os.path.exists(strLogFolder):
        logging.info("create folder [%s]" % strLogFolder)
        os.system(str("md %s" % strLogFolder))
    strLogFile = cp_util.funcGetValue('Global', 'Log_File')
    logFile = os.path.join(strLogFolder, strLogFile)
    cp_util.funcInitLogFile(logFile, True, logFile + '-' +
                            str(datetime.datetime.now().isoformat()).replace(':', '-'))

    logging.info('Start to run the manage machine script')
    # Automation flow start forever if no erorr occurred
    while True:
        # reload configure ini
        cp_util.funcLoadConfigure(strFileConfigIni)

        # set polling period
        intWaitSec = int(cp_util.funcGetValue('Global', 'Polling_Period'))

        # Check stop signal first, if found the STOP signal then normal to
        # stop automation.
        strStop = cp_util.funcGetValue('Global', 'Stop_Signal')
        if strStop is not None and strStop != '':
            logging.info('\n' + '-' * 80 +
                         '\nThe stop signal has been set in ini file.' +
                         '\nStop working!\n' +
                         '-' * 80)
            return errASM.STOP
        #
        logging.info("fetch a task from task folder list")
        lstTaskFolder = cp_util.funcGetValue('Global', 'Task_Folder_List')
        if crossPlatform.util.is_list(lstTaskFolder) == 0:
            lstTaskFolder = [lstTaskFolder]
        cp_ini.g_task = cp_util.funcFetchTask(lstTaskFolder)
        if cp_ini.g_task is not None:
            if funcProcessTask(cp_ini.g_task) != errASM.SUCCESS:
                logging.error(str("process task [%s] fail!" % (cp_ini.g_task)))
                return errASM.STOP
        #
        logging.info("wait %d sec!", intWaitSec)
        time.sleep(intWaitSec)


def funcProcessTask(strTask):
    """
    process task module
    @type strTask: String
    @param strTask: the target task full path and file name
    @return:
        errASM.SUCCESS means prcess task OK
        others means NG, please check the error log
    """
    # record task start time
    cp_ini.g_strStartTime = str(datetime.datetime.now())
    # init log file
    strLogFolder = cp_util.funcGetValue('Global', 'Log_Folder')
    strLogFile = cp_util.funcGetValue('Global', 'Log_File')
    logFile = os.path.join(strLogFolder, strLogFile)
    cp_util.funcInitLogFile(logFile, True, logFile + '-' + str(
        datetime.datetime.now().isoformat()).replace(':', '-'))
    #
    strBaseWorkingFolder = cp_util.funcGetValue('Global', 'Working_Folder')
    logging.info(str("check Auto Srv working folder %s is exist or not!" %
                     (strBaseWorkingFolder)))
    if not os.path.exists(strBaseWorkingFolder):
        logging.info("create folder [%s]" % strBaseWorkingFolder)
        os.system(str("md %s" % strBaseWorkingFolder))

    lstFile = os.path.split(strTask)
    lstFileName = os.path.splitext(lstFile[1])
    cp_ini.working_task = os.path.join(
        strBaseWorkingFolder, lstFileName[0], lstFile[1])
    logging.info(str("move task %s to working folder %s" % (strTask,
                                                            cp_ini.working_task)))
    # note: maybe need to chcek the target loacation exist same file name
    # before move file
    strWorkingFolder = os.path.join(strBaseWorkingFolder, lstFileName[0])
##    if os.path.exists(strWorkingFolder):
##        logging.error(str('the task working folder [%s] is exist!' % strWorkingFolder))
##        return errASM.FOLDER_EXIST
    # if destination folder was existed than append datetime for folder name with '_datetime'
    if os.path.exists(strWorkingFolder):
        logging.info('the task working folder [%s] is exist!' %
                     strWorkingFolder)
        logging.info('Append id for [%s] ...' % strWorkingFolder)
        currentTime = datetime.datetime.now()
        createId = currentTime.strftime("%Y%m%d%H%M%S")
        logging.info('Append id is [%s] ...' % createId)
        appenId = '_' + createId
        strWorkingFolder = strWorkingFolder + appenId
        logging.info('new forder name is [%s] ...' % strWorkingFolder)

    try:
        os.mkdir(strWorkingFolder)
        logging.info('folder [%s] created...' % strWorkingFolder)
        cp_ini.working_task = os.path.join(strWorkingFolder, lstFile[1])
        #cp_ini.working_task = os.path.join(strWorkingFolder, lstFileName[0]+appenId+lstFileName[1])
    except WindowsError, err:
        logging.error(str('%s' % err))

    #
    #logging.info(str('create working folder [%s]' % strWorkingFolder))
    #os.mkdir(strWorkingFolder)
    logging.info(str('move task [%s] to working folder [%s]' % (
        strTask, cp_ini.working_task)))
    shutil.move(strTask, cp_ini.working_task)
    # reload configure setting base on target task ini
    cp_util.funcLoadConfigure(cp_ini.working_task)
    # according the task project setting to load correct working object
    # note: need care the value is valid or not for current support status
    logging.info(str("the task project task class setting = %s" %
                     cp_util.funcGetValue('Global', 'ProjectProcessTaskClass')))
    strProjectProcessTaskClass = cp_util.funcGetValue(
        'Global', 'ProjectProcessTaskClass')
    strModule, strClass = strProjectProcessTaskClass.rsplit('.', 1)
    exec 'from %s import %s' % (strModule, strClass)
    klass = eval(strClass)
    objTask = klass()
    # start to do task test
    objTask.strStartTime = cp_ini.g_strStartTime
    objTask.funcStartProcess(cp_ini.working_task)
    return errASM.SUCCESS

if __name__ == '__main__':
    print sys.argv
    if len(sys.argv) != 2:
        print "error the parameter is none! %s" % sys.argv
        print raw_input('press [ENTER] to exit ...')
    else:
        funcAutomationServerMain(sys.argv[1])
