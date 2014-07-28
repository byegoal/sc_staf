import sys
import os
import platform
import re
import subprocess


def isWindows():
    if os.name == 'nt':
        return True
    return False


def isMac():
    if sys.platform == 'darwin':
        return True
    return False


def isLinux():
    if sys.platform == 'linux2':
        return True
    return False

if isWindows():
    import win32api
    import win32con
    import pywintypes

    class WinRegistry:
        dicKeyRoot = {'HKEY_CLASSES_ROOT': win32con.HKEY_CLASSES_ROOT,
                      'HKEY_CURRENT_USER': win32con.HKEY_CURRENT_USER,
                      'HKEY_LOCAL_MACHINE': win32con.HKEY_LOCAL_MACHINE,
                      'HKEY_USERS': win32con.HKEY_USERS}

        def __init__(self, strKeyPath):
            if strKeyPath[0] == '\\':
                strKeyPath = strKeyPath[1:]
            self.strKey = strKeyPath
            strRoot, strKey = strKeyPath.split('\\', 1)
            if strRoot not in self.dicKeyRoot:
                raise KeyError(strRoot)
            intRoot = self.dicKeyRoot[strRoot]
            self._h = win32api.RegOpenKeyEx(
                intRoot, strKey, 0, win32con.KEY_QUERY_VALUE)

        def __del__(self):
            try:
                win32api.RegCloseKey(self._h)
            except:
                pass

        def getValue(self, strValueName, default=None):
            try:
                value = win32api.RegQueryValueEx(self._h, strValueName)[0]
            except pywintypes.error, e:
                if str(e.args[0]) == '2':  # value name doesn't exist
                    if strValueName == '':
                        return None
                    if default is not None:
                        return default
                raise
            return value

    def getRegValue(strKey, strValueName, default=None):
        obj = WinRegistry(strKey)
        return obj.getValue(strValueName, default)

    def getWindowsVersion():
        obj = WinRegistry(r'HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Windows NT\CurrentVersion')
        strProductName = obj.getValue('ProductName', '')
        strCurrentVersion = obj.getValue('CurrentVersion', '')
        strCSDVersion = obj.getValue('CSDVersion', '')
        if strCurrentVersion == '5.0':
            obj = WinRegistry(r'HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\ProductOptions')
            strProductType = obj.getValue('ProductType').lower()
            if strProductType == 'winnt':
                strProductName += ' Pro.'
            elif strProductType == 'servernt':
                strProductName += ' Server'
            elif strProductType == 'lanmannt':
                strProductName += ' Advanced Server'
        elif strProductName.find('Server 2003') >= 0 or strProductName.find('Server 2008') >= 0:
            obj = WinRegistry(r'HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\ProductOptions')
            strProductSuite = obj.getValue('ProductSuite')[0].lower()
            if strProductSuite == 'enterprise' and strProductName.lower().find('enterprise') < 0:
                strProductName += ' Enterprise'
            elif strProductSuite == 'terminal server':
                strProductName += ' Standard'
        obj = WinRegistry(r'HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\ProductOptions')
        lstValue = obj.getValue('ProductSuite')
        if ' '.join(lstValue).lower().find('embeddednt') != -1:
            strProductName += ' Embedded'
        try:
            win32api.RegOpenKey(win32con.HKEY_LOCAL_MACHINE, "Software\\Wow6432Node\\Microsoft\\Windows NT\\CurrentVersion")
            strVersion = '%s (x64) %s' % (strProductName, strCSDVersion)
        except pywintypes.error:
            strVersion = '%s %s' % (strProductName, strCSDVersion)

        strVersion = strVersion.replace('Microsoft', '').strip()
        strVersion = strVersion.replace('(R) ', '').strip()
        strVersion = strVersion.replace('(TM) ', '').strip()
        strVersion = strVersion.replace('Service Pack ', 'SP').strip()
        return strVersion


def getMacVersion():
    from processUtil import TmProcess
    objP = TmProcess(['system_profiler', 'SPSoftwareDataType'])
    strBuf = objP.readStdout()
    objRex = re.search('System Version:[\s]*([^\n]*)', strBuf)
    if objRex:
        # Mac OS X 10.4.11 (8S165)
        strVersion = objRex.group(1)
    else:
        strVersion = '%s %s' % (platform.uname()[0], platform.uname()[2])
    strVersion = re.sub(' \(.*\)', '', strVersion)
    strVersion = re.sub('Mac OS X', 'MacOS X', strVersion)
    strCpuInfo = getMacCpuInfo()
    if strCpuInfo:
        strVersion += ' %s' % strCpuInfo
    return strVersion


def getMacCpuInfo():
    from tmstaf.processUtil import TmProcess
    objP = TmProcess(['system_profiler', 'SPHardwareDataType'])
    strBuf = objP.readStdout()
    objRex = re.search('CPU Type:[\s]*([^\n]*)', strBuf)
    if objRex:
        strCpuInfo = objRex.group(1).split(' ')[0]
    else:
        strCpuInfo = ''
    return strCpuInfo


def isMacCaseSensitive():
    '''
    Use "diskutil info /" to check if current file system is case-sensitive
    @return: 1 means case-sensitive; 0 means NOT case-sensitive
    '''
    from tmstaf.processUtil import TmProcess
    objP = TmProcess(['diskutil', 'info', '/'])
    strStdout = objP.readStdout()
    intRc = objP.wait()
    if re.search('Mount Point:[\s]+([\S]*)\n', strStdout).group(1) != '/':
        raise RuntimeError('get disk info failed! stdout:\n%s', strStdout)
    strFileSystem = re.search(
        'File System:[\s]+([^\n]*)\n', strStdout).group(1)
    if re.search('case-sensitive', strFileSystem, re.I):
        return 1
    else:
        return 0


def isMacTiger():
    if re.search(re.escape('Mac OS X 10.4'), getMacVersion(), re.I):
        return 1
    return 0


def isMacLeopard():
    if re.search(re.escape('Mac OS X 10.5'), getMacVersion(), re.I):
        return 1
    return 0


def isMacSnowLeopard():
    if re.search(re.escape('Mac OS X 10.6'), getMacVersion(), re.I):
        return 1
    return 0


def isCentOs():
    if isLinux():
        strF = '/etc/redhat-release'
        if os.path.exists(strF):
            if re.search('CentOS', open(strF).read(), re.I):
                return 1
        else:
            obj = subprocess.Popen(["rpm", "-q",
                                    "cenos-release"], stdout=subprocess.PIPE)
            if obj.wait() == 0 and obj.stdout.rea().find(' not ') == -1:
                return 1
    return 0


def getPlatformInfo():
    if isWindows():
        s = getWindowsVersion()
    elif isMac():
        if isMacCaseSensitive():
            strOtherInfo = ' Case-Sensitive'
        else:
            strOtherInfo = ' Non-Case-Sensitive'
        s = getMacVersion() + strOtherInfo
    else:
        s = '%s %s' % (platform.uname()[0], platform.uname()[2])
    return s
