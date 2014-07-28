import os
import logging
import pywintypes
import registryUtil
import winVerUtil


def is64bit():
    '''
    This function will return 0 if the current system is 64-bit OS.
    '''
    if os.name == 'nt':
        from platform import machine
        strMachine = machine()
        if strMachine == "AMD64":
            return 0
        else:
            return 2
##        import win32api,win32con
##        try:
##            win32api.RegOpenKey(win32con.HKEY_LOCAL_MACHINE, "Software\\Wow6432Node")
##            return 0
##        except pywintypes.error,e:
##            return 2
    else:
        raise RuntimeError(
            'This Function only support windows platform currently.')


def isWin2000():
    '''
    This function will return True if the current system is Windows 2000 platform.
    '''
    if winVerUtil.getWindowsVersion().find('Windows 2000') >= 0:
        return True
    else:
        return False


def isWin2003():
    '''
    This function will return True if the current system is Windows Server 2003 platform.
    '''
    if winVerUtil.getWindowsVersion().find('Server 2003') >= 0:
        return True
    else:
        return False


def isWinXp():
    '''
    This function will return True if the current system is Windows XP platform.
    '''
    if winVerUtil.getWindowsVersion().find('Windows XP') >= 0:
        return True
    else:
        return False

isWin64 = is64bit() == 0


def getWindowsCookiePath():
    '''
    Get the directory path in which Windows save all cookies.
    '''
    strKey = r'HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Explorer\Shell Folders'
    obj = registryUtil.WinRegistry(strKey)
    value, vType = obj.getValue('Cookies')
    return value


def registerPstools(strName):
    '''
    Register pstools to prevent it poping up EULA dialog. For example, registerPstools("PsList")
    @param strName: tool name in pstools. Ex. PsList, PsKill, PsInfo
    @return: 0 means success; 1 means fail
    '''
    strBaseKey = 'HKEY_CURRENT_USER\\Software\\Sysinternals'
    if not registryUtil.isKeyExist(strBaseKey):
        logging.info('create registry key: "%s"', strBaseKey)
        if registryUtil.createKey('HKEY_CURRENT_USER\\Software', 'Sysinternals', None, None, None):
            return 1
    strKey = os.path.join(strBaseKey, strName)
    if not registryUtil.isKeyExist(strKey) or registryUtil.valueExist(strKey, 'EulaAccepted') == 2:
        logging.info('create registry key: "%s"', strKey)
        return registryUtil.createKey(strBaseKey, strName, 'EulaAccepted', 1, 'REG_DWORD')
    return 0


def getPlatformIdInSctm():
    '''
    win2k_pro       Win 2000 Pro
    win2k_srv       Win 2000 Server
    winxp_pro       WinXP Professional
    winxp_pro64     WinXP Professional(x64)
    win2k3_std      Win2k3 Standard
    win2k3r2_ent64  Win2k3 R2 Enterprise(x64)
    winvista_bus    WinVista Business
    winvista_ult64  WinVista Ultimate(x64)
    win2k8_ent      Win2008 Enterprise
    win2k8_ent64    Win2008 Enterprise(x64)
    win7_ult32      Windows 7 Ultimate
    win7_ult64      Windows 7 Ultimate(x64)
    win2k8R2_ent    Windows Server 2008 R2 Enterprise
    win2k8R2_ent64  Windows Server 2008 R2 Enterprise(x64)
    '''
    strVer = winVerUtil.getWindowsVersion().lower()
    if strVer.find('2000 pro') >= 0:
        return 'win2k_pro'
    elif strVer.find('2000 server') >= 0:
        return 'win2k_srv'
    elif strVer.find(' xp(x64)') >= 0:
        return 'winxp_pro64'
    elif strVer.find(' xp ') >= 0:
        return 'winxp_pro'
    elif strVer.find('server 2003 standard') >= 0:
        return 'win2k3_std'
    elif strVer.find('server 2003 r2 enterprise(x64)') >= 0:
        return 'win2k3r2_ent64'
    elif strVer.find('vista business') >= 0:
        return 'winvista_bus'
    elif strVer.find('vista ultimate(x64)') >= 0:
        return 'winvista_ult64'
    elif strVer.find('2008 enterprise(x64)') >= 0:
        return 'win2k8_ent64'
    elif strVer.find('2008 enterprise ') >= 0:
        return 'win2k8_ent'
    elif strVer.find('windows 7 ultimate(x64)') >= 0:
        return 'win7_ult64'
    elif strVer.find('windows 7 ultimate') >= 0:
        return 'win7_ult32'
    elif strVer.find('2008 r2 enterprise(x64)') >= 0:
        return 'win2k8R2_ent64'
    elif strVer.find('2008 r2 enterprise') >= 0:
        return 'win2k8R2_ent'
    return 'unknow'

#still provide reboot function in this module is for backward compatibility
from staf.util import reboot


def Test():
    is64bit()

if __name__ == "__main__":
    Test()
