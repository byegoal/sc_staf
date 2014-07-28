import os
import sys
import stat
import subprocess
import time
import socket
import shutil
from staf import tmLogger
#from thirdParty.iniparse import INIConfig
from config_obj import ConfigObj
from subprocess import Popen
import inspect
import logging


def module_sleep(sleep_time):
    print "test sleep=", sleep_time
    #logging.debug('test sleep')
    time.sleep(sleep_time)
    return 0


def is_socket_available(inTestMachineIP, inTestMachinePort):  # bool func, return 1 if socket success, else return 0
    cmdstr = "test -null -test\n"
    try:
        result = send_socket_to_testmanager(
            inTestMachineIP, inTestMachinePort, cmdstr)
        result = 1
    except:
        result = 0
    return int(result)


def launch_framework(inInstallpath, inExecutionName, inWaitSecs=20):

    #preparation
    #write log
    logging.debug('Start launch uniclient framework\n')

    #if inInstallpath is "", get setting from ini file
    #get setting from ini file
    objGetIniSetting = GetIniSetting()
    if inInstallpath == "":
        inInstallpath = objGetIniSetting.getIniVar('global', 'InstallPath')
    if inExecutionName == "":
        inExecutionName = objGetIniSetting.getIniVar('global', 'ExecutionName')

    #change working directory
    os.chdir(inInstallpath)
    #create sub process
    objSubprocess = subprocess.Popen([inInstallpath + inExecutionName])
    #wait framework loading

    time.sleep(inWaitSecs)
    #write pid to file to record it
    file_handle = open(AMSPPATH + TMPFILE, 'w')
    file_handle.write(str(objSubprocess.pid))
    return 0


def terminate_framework():

    #terminate framework launched by launch_frameWork(inInstallpath, inExecutionName)

    #preparation

    import win32api
    import win32con
    #terminate sub process
    #this part is for windows only, need cross platform in the future
    logging.debug('terminate uniclient process')

    try:
        os.system("taskkill /F /IM coreFrameworkHost.exe")
        time.sleep(2)
    except:
        logging.debug('terminate uniclient process fail')
        return 1
    return 0


def send_socket_to_testmanager(inTestMachineIP, inTestMachinePort, inCmd):

    ################################################################
    #preparation
    #write log
    #get setting from ini file
    ################################################################
    #set timeout for every socket
    socket.setdefaulttimeout(300)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((inTestMachineIP, int(inTestMachinePort)))
    #time.sleep(1)
    #sock.send('ScmManager -QueryInterface -name=QueryTestpluginInterface -module=50 -interface=501\n')
    #sock.send('ScmManager -QueryInterface -name=QueryTestpluginInterface -module=50 -interface=501\n')
    sock.send(inCmd)
    strReturn = sock.recv(1024)
    #result is #=> xxxx, we need to get xxxx
    strFilterReturn = strReturn[(strReturn.find(' ') + 1):-1]
    #print "ret is :"+strFilterReturn+'\n'
    sock.close()
    return strFilterReturn


def force_remove_tree(top):
    # Delete everything reachable from the directory named in 'top',
    # assuming there are no symbolic links.
    # CAUTION:  This is dangerous!  For example, if top == '/', it
    # could delete all your disk files.
    try:
        for root, dirs, files in os.walk(top, topdown=False):
            if (top != 'c:\\'):
                for name in files:
                    filename = os.path.join(root, name)
                    os.chmod(filename, stat.S_IWRITE)
                    os.remove(os.path.join(root, name))
                for name in dirs:
                    os.rmdir(os.path.join(root, name))
        os.rmdir(top)
    except:
        print 'remove file fail'
    return 0


def modify_InstallDir_in_REG(value):
    import _winreg
    try:
        uniclient_root = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,
                                         r"SOFTWARE\TrendMicro\AMSP", 0, _winreg.KEY_ALL_ACCESS)
        _winreg.SetValueEx(
            uniclient_root, "InstallDir", None, _winreg.REG_SZ, value)
        _winreg.CloseKey(uniclient_root)
        return 0
    except WindowsError, data:
        logging.error("modify_installDir_in_REG: Modify registry fail,%s" %
                      data)
        return 1


def restore_InstallDir_in_REG():
    import _winreg
    try:
        uniclient_root = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,
                                         r"SOFTWARE\TrendMicro\AMSP", 0, _winreg.KEY_ALL_ACCESS)
        _winreg.SetValueEx(uniclient_root, "InstallDir", None,
                           _winreg.REG_SZ, AMSPPATH)
        _winreg.CloseKey(uniclient_root)
        return 0
    except WindowsError, data:
        logging.error("modify_installDir_in_REG: Modify registry fail,%s" %
                      data)
        return 1

#def force_remove_tree(inFileRoot):
#    # Delete everything reachable from the directory named in 'inFileRoot',
#    # assuming there are no symbolic links.
#    # CAUTION:  This is dangerous!  For example, if inFileRoot == '/', it
#    # could delete all your disk files.zz
#    try:
#        for root, dirs, files in os.walk(inFileRoot, inFileRootdown=False):
#            if (inFileRoot != 'c:\\'):
#                for name in files:
#                    filename=os.path.join(root, name)
#                    os.chmod (filename, stat.S_IWRITE)
#                    os.remove(os.path.join(root, name))
#                    fff=os.path.join(root, name)
#                    print 'nameInfile',fff
#                for name in dirs:
#                    os.rmdir(os.path.join(root, name))
#                    fff=os.path.join(root, name)
#                    print 'nameindir',fff
#        os.rmdir(inFileRoot)
#    except:
#        print 'remove file fail'


class GetIniSetting:
    """
    ini opoeration module
    """
    def __init__(self, filename=None):
        self._cfgpath = filename
        self._cfgfile = ConfigObj(self._cfgpath)
        self._cfgfile2 = None

    def addSection(self, inCategory):
        '''
        Add section to the opened ini file
        @param inCategory: the Section value
        '''
        self._cfgfile[inCategory] = {}
        self._cfgfile.write()

    def getSection(self, inCategory):
        """
        Get section all data into a dictionary
        @param inCategory: the Section value
        @return: a dictionary include all key-value pairs
        """
        return self._cfgfile[inCategory]

    def setSection(self, inCategory, inSectionValue):
        """
        Upadte a Section with another Section key/value pairs
        @param inCategory: the Section value
        @param inSectionValue: key/pairs
        """
        self.addSection(inCategory)
        self._cfgfile[inCategory].update(inSectionValue)
        try:
            self._cfgfile.write()
            return
        except:
            logging.error(str(
                "Set section [%s] in ini file fail" % inCategory))
            logging.error(traceback.format_exc())
            pass

    def getIniVar(self, inCategory, inVarName):
        """
            Get ini Key value in Section
            @param inCategory: section name
            @param inVarName: key name
        """
        try:
            return self._cfgfile[inCategory][inVarName]
        except:
            pass
        #try to get setting from machine.ini
        try:
            return self._cfgfile2[inCategory][inVarName]
        except:
            pass
        logging.debug(str("Can't get [%s][%s] to ini file"
                          % (inCategory, inVarName)))

    def setIniVar(self, inCategory, inVarName, inVarValue):
        '''
            Write ini setting to the uniclient.ini
            @param inCategory: section name
            @param inVarName: key name
            @param inVarValue: value
        '''
        self._cfgfile[str(inCategory)][str(inVarName)] = inVarValue

        try:
            self._cfgfile.write()
            return
        except:
            logging.error(str("Set [%s][%s] in ini file fail"
                          % (inCategory, inVarName)))
            logging.error(traceback.format_exc())

    def delIniVar(self, inCategory, inVarName):
        """
        Delete key in Section
        @param inCategory: the Section
        @param inVarName: the Key
        """
        self._cfgfile[str(inCategory)].pop(str(inVarName))
        try:
            self._cfgfile.write()
            return
        except:
            logging.error(str("Delete [%s][%s] in ini file fail"
                              % (inCategory, inVarName)))
            logging.error(traceback.format_exc())

    def iterSection(self, inCategory):
        """
        Got the all keys in section
        @param inCategory: the Section data
        @return: the keys list
        """
        return self._cfgfile[str(inCategory)].iteritems()

##class GetIniSetting:
##    def __init__(self, filename = None):
##        #load ini from relative path
##        self._pypath = inspect.currentframe().f_code.co_filename
##        if(filename == None):
##            self._cfgpath = self._pypath[0:(self._pypath.find('lib')-1)] + "\\testsuites\VIZOR_OEM\VIZOR_OEM.ini"
##            self._cfgfile = ConfigObj(self._cfgpath)
##            try:
##                self._cfgpath2 = self._pypath[0:(self._pypath.find('lib')-1)] + "\\testsuites\VIZOR_OEM\machine.ini"
##                self._cfgfile2 = ConfigObj(self._cfgpath2)
##            except:
##                pass
##        else:
##            #self._cfgpath = self._pypath[0:(self._pypath.find('lib')-1)] + "\\testsuites\VIZOR_OEM\\" + filename
##            self._cfgpath = filename
##            self._cfgfile = ConfigObj(self._cfgpath,options={'create_empty':True})
##            self._cfgfile2 = None
##
##    def addSection(self, inCategory):
##        ''' Add section to the opened ini file
##        '''
##        self._cfgfile[inCategory] = {}
##        self._cfgfile.write()
##
##    def getIniVar(self, inCategory, inVarName):
##
##        #global setting has high priority
##        try:
##            return self._cfgfile[inCategory][inVarName]
##        except:
##            pass
##        #try to get setting from machine.ini
##        try:
##            return self._cfgfile2[inCategory][inVarName]
##        except:
##            pass
##        logging.debug("utility.getIniVar: Can't get [%s][%s] to ini file"%(inCategory,inVarName))
##
##    def setIniVar(self, inCategory, inVarName , inVarValue):
##        ''' Write ini setting to the uniclient.ini
##            inCategory - section name
##            inVarName - key name
##            inVarValue - value
##        '''
##        self._cfgfile[str(inCategory)][str(inVarName)] = inVarValue
##
##        try:
##            self._cfgfile.write()
##            return
##        except:
##            pass
##        logging.debug("uniclient_utility.setIniVar: Can't write [%s][%s] to ini file"%(inCategory,inVarName))

#objGetIniSetting = GetIniSetting()
#AMSPPATH = objGetIniSetting.getIniVar('global','InstallPath')
#TMPFILE = '\\pid.txt'


def deleteIniFile(fileName=None):
    if (None == fileName):
        return

    curModulePath = inspect.currentframe().f_code.co_filename
    filePath = curModulePath[0:(curModulePath.find(
        'lib') - 1)] + "\\testsuites\uniclient\\" + fileName
    os.remove(filePath)


def unittest_configobj():
    iniObj = GetIniSetting()

    # Read from file
    print iniObj.getIniVar('PostOffice', 'paPostOffice_Base_portID')
    # Write to file
    iniObj.setIniVar('PostOffice', 'paPostOffice_Base_portID', 15100)


def uniclient_sleep(sleep_time):
    time.sleep(sleep_time)


def uniclient_copy(srcfile, destfile):
    try:
        shutil.copyfile(srcfile, destfile)
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise


def uniclient_delete(inFilePath):
    try:
        os.remove(inFilePath)
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise


def uniclient_deleteDir(inDirPath):
    try:
        os.system("rd /s /q " + inDirPath)
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise


def uniclient_mkdir(inDirPath):
    try:
        os.mkdir(inDirPath)
    except:
        print "Unexpected error:", sys.exc_info()[0]
        raise

#use this function to change user permission to access registry
#action:grant, deny
#binpath: setacl.exe file position


def unicleint_registry_access(binPath, registry, action, sid):
    targetFile = 'setacl.exe'
    cmdStr = targetFile + ' ' + registry + ' /registry /' + action + \
        ' ' + sid + ' /full /sid'
    os.chdir(binPath)
    Popen(cmdStr)
    return 0


def query_stop_signal_reg():
    import _winreg
    try:
        vizor_root = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,
                                     r"SOFTWARE\TrendMicro\Vizor", 0, _winreg.KEY_ALL_ACCESS)
        keyvalue = _winreg.QueryValueEx(vizor_root, "StopWorking")
        _winreg.CloseKey(vizor_root)
        return keyvalue[0]
    except WindowsError:
        logging.error("check_stop_signal: Query registry StopWorking fail")
        return "0"


def reset_stop_signal_reg():
    import _winreg
    try:
        vizor_root = _winreg.OpenKey(_winreg.HKEY_LOCAL_MACHINE,
                                     r"SOFTWARE\TrendMicro\Vizor", 0, _winreg.KEY_ALL_ACCESS)
        _winreg.SetValueEx(
            vizor_root, "StopWorking", None, _winreg.REG_SZ, '0')
        _winreg.CloseKey(vizor_root)
        return 0
    except WindowsError:
        logging.error("reset_stop_signal_reg: Set registry StopWorking 0 fail")
        return 1

if __name__ == '__main__':
    #unicleint_registry_access(r'C:\STAF\lib\python\uniclient\common\bin', r'MACHINE\SOFTWARE\TrendMicro\UniClient\456\CM_SQ_35','deny','S-1-5-32-544')
    #unicleint_registry_access(r'C:\STAF\lib\python\uniclient\common\bin', r'MACHINE\SOFTWARE\TrendMicro\UniClient\456\CM_SQ_FET_36_sub','grant','S-1-5-32-544')
    #deleteTestManagerDll()
    #prepare_testmanagerdll()
    #launch_framework("","")
    #terminate_framework()
    #unittest_configobj()
    #sys.exit(launch_frameWork())
    #test()
    #uniclient_copy('c:\\abc.txt','c:\\def.txt')
    #launch_framework("", "", 5)
    restore_InstallDir_in_REG()
