import sys
import getopt
import logging
import ConfigParser
import cStringIO
import re
import struct
import binascii
import os
import codecs
import locale
import urllib
import win32api
import win32con
import pywintypes
import win32event
import misc
import processUtil

g_dicKeyRoot = {'HKEY_CLASSES_ROOT': win32con.HKEY_CLASSES_ROOT,
                'HKEY_CURRENT_USER': win32con.HKEY_CURRENT_USER,
                'HKEY_LOCAL_MACHINE': win32con.HKEY_LOCAL_MACHINE,
                'HKEY_USERS': win32con.HKEY_USERS}

g_dicValueType = {win32con.REG_BINARY: 'REG_BINARY',
                  win32con.REG_DWORD: 'REG_DWORD',
                  win32con.REG_DWORD_LITTLE_ENDIAN: 'REG_DWORD_LITTLE_ENDIAN',
                  win32con.REG_DWORD_BIG_ENDIAN: 'REG_DWORD_BIG_ENDIAN',
                  win32con.REG_EXPAND_SZ: 'REG_EXPAND_SZ',
                  win32con.REG_LINK: 'REG_LINK',
                  win32con.REG_MULTI_SZ: 'REG_MULTI_SZ',
                  win32con.REG_NONE: 'REG_NONE',
                  win32con.REG_RESOURCE_LIST: 'REG_RESOURCE_LIST',
                  win32con.REG_SZ: 'REG_SZ'
                  }


class WinRegistry:
    def __init__(self, strKeyPath, intAccessMask=None):
        if strKeyPath[0] == '\\':
            strKeyPath = strKeyPath[1:]
        self.strKey = strKeyPath
        strRoot, strKey = strKeyPath.split('\\', 1)
        if strRoot not in g_dicKeyRoot:
            raise KeyError(strRoot)
        intRoot = g_dicKeyRoot[strRoot]
        if intAccessMask is None:
            intAccessMask = win32con.KEY_QUERY_VALUE | win32con.KEY_ENUMERATE_SUB_KEYS | win32con.KEY_NOTIFY
        self._h = win32api.RegOpenKeyEx(intRoot, strKey, 0, intAccessMask)
        self._intNumOfSubKey, self._intNumOfValue, self._intTimeStamp = win32api.RegQueryInfoKey(self._h)
        self._strKeyPath = strKeyPath
        self._intAccessMask = intAccessMask

    def __del__(self):
        try:
            win32api.RegCloseKey(self._h)
        except:
            pass

    def getValue(self, strValueName, default=None):
        '''
        @return: (value,value_type)
        '''
        try:
            value, vType = win32api.RegQueryValueEx(self._h, strValueName)
        except pywintypes.error, e:
            if str(e.args[0]) == '2':  # value name doesn't exist
                if strValueName == '':
                    return None, win32con.REG_NONE
                if default is not None:
                    return default, None
            raise
        return value, vType

    def setValue(self, strValueName, value, vType):
        win32api.RegSetValueEx(self._h, strValueName, 0, vType, value)

    def delValue(self, strValueName):
        win32api.RegDeleteValue(self._h, strValueName)

    def enumValue(self):
        # return (value_name,value,value_type)
        lstTmp = []
        for i in range(self._intNumOfValue):
            lstTmp.append(win32api.RegEnumValue(self._h, i)[0])
        lstTmp.sort()
        for name in lstTmp:
            yield (name,) + win32api.RegQueryValueEx(self._h, name)

    def enumSubKey(self):
        # return WinRegistry instance
        for i in range(self._intNumOfSubKey):
            yield WinRegistry(os.path.join(self._strKeyPath, win32api.RegEnumKey(self._h, i)), self._intAccessMask)

    def waitValueChange(self, intTimeout):
        '''
        @return: 0 means some value is changed
            258 means timeout
        '''
        logging.debug('Monitor value changes under registry key "%s"...' %
                      (self._strKeyPath))
        hEvent = win32event.CreateEvent(None, 1, 0, None)
        win32api.RegNotifyChangeKeyValue(self._h, 0,
                                         win32api.REG_NOTIFY_CHANGE_LAST_SET, hEvent, 1)
        try:
            RC = win32event.WaitForSingleObject(hEvent, intTimeout * 1000)
        finally:
            win32api.CloseHandle(hEvent)

        if RC == win32event.WAIT_OBJECT_0:
            logging.debug('Adding or deleting a value, or changing an existing value.')
            return 0
        elif RC == win32event.WAIT_TIMEOUT:
            raise RuntimeError('Monitor registry timeout. Key=%s' %
                               self._strKeyPath)
        else:
            raise RuntimeError('Monitor registry failed, RC=%s. Key=%s' %
                               (RC, self._strKeyPath))


def createKey(strKey, strSubKey, strValueName, strValue, strType):
    '''
    @param strKey: Specify registry key path. Ex. HKEY_LOCAL_MACHINE\SOFTWARE
    @param strSubKey: Specify the key you want to create. Ex. MyApp
    @param srValueName: Specify registry value name which you want to create. Ex. Name
    @param strValue: Specify new registry value. Ex. camge
    @param strType: Specify value type. It's value should be: REG_BINARY,REG_DWORD,REG_SZ
    @return: 0 means success
    '''
    if strKey[0] == '\\':
        strKey = strKey[1:]
    strRoot, strKey = strKey.split('\\', 1)
    intRoot = g_dicKeyRoot[strRoot]
    try:
        h = win32api.RegOpenKeyEx(intRoot, strKey, 0, win32con.KEY_ALL_ACCESS)
        h2 = win32api.RegCreateKey(h, strSubKey)
        if strValue and not strValueName:
            win32api.RegSetValue(h2, None, win32con.REG_SZ, strValue)
        if strValueName:
            intType = getattr(win32con, strType)
            if intType == win32con.REG_DWORD:
                value = int(strValue)
            else:
                value = strValue
            win32api.RegSetValueEx(h2, strValueName, 0, intType, value)
    except pywintypes.error, e:
        logging.error(
            'createKey failed! Error %s: %s' % (e.args[0], e.args[2]))
        return 1
    win32api.RegCloseKey(h)
    win32api.RegCloseKey(h2)
    return 0


def isKeyExist(strKey):
    '''
    Check if the specify registry key exists.
    @param strKey: Key path. Ex. 'HKEY_LOCAL_MACHINE\\SOFTWARE\\MyApp'
    @return: 1 means exist; 0 means key does NOT exist.
    '''
    try:
        WinRegistry(strKey, win32con.KEY_QUERY_VALUE)
    except pywintypes.error, e:
        if str(e.args[0]) == '2':
            return 0
        raise
    return 1


def deleteKey(strKey, includeAllSubKey=0):
    '''
    Delete a registry key. This function will fail if strKey has sub keys.
    But set includeAllSubKey to 1, it can remove strKey that has sub keys.
    @param strKey: Specify registry key path. Ex. HKEY_LOCAL_MACHINE\SOFTWARE\test123
    @param includeAllSubKey: default value is 0. Set to 1 will remove all sub keys
    @return: 0 means success or the strKey does not exist.
    '''
    if not isKeyExist(strKey):
        return 0

    if strKey[0] == '\\':
        strKey = strKey[1:]
    lstKey = []
    if includeAllSubKey:
        lstKey = enumAllSubKey(strKey)
        lstKey.reverse()
    lstKey.append(strKey)
    for strTmpKey in lstKey:
        strRoot, strTmpKey = strTmpKey.split('\\', 1)
        intRoot = g_dicKeyRoot[strRoot]
        try:
            win32api.RegDeleteKey(intRoot, strTmpKey)
        except pywintypes.error, e:
            logging.error('deleteKey %s failed! Error %s: %s' %
                          (repr(strTmpKey), e.args[0], e.args[2]))
            return 1
    return 0


def enumAllSubKey(strKey):
    lstKey = []
    objKey = WinRegistry(strKey)
    lstObjKey = [objKey]
    while True:
        try:
            objKey = lstObjKey.pop()
        except:
            break
        lstKey.append(objKey.strKey)
        for objSubKey in objKey.enumSubKey():
            lstObjKey.append(objSubKey)
    return lstKey[1:]


def deleteValue(strKey, strValueName):
    '''
    @param strKey: Specify registry key path. Ex. HKEY_LOCAL_MACHINE\SOFTWARE\MyApp
    @param srValueName: Specify registry value name. Ex. VirusCount
    @return: 0 means success.  1 means value doesn't exist. 2 means value delete fail because access denied, 3 means other exception error
    '''

    try:
        objReg = WinRegistry(strKey, win32con.KEY_ALL_ACCESS)
        objReg.delValue(strValueName)
    except pywintypes.error, e:
        if str(e.args[0]) == '2':
            logging.info('Delete value %s failed, It does not exist.' %
                         (repr(strValueName)))
            return 1
        if str(e.args[0]) == '5':
            logging.error('Delete value %s failed, Access Denied.' %
                          (repr(strValueName)))
            return 2
        else:
            logging.error('Delete value %s failed because %s.',
                          strValueName, e.args[1])
            return 3
    return 0


def retValue(strKey, strValueName):
    '''
    @param strKey: Specify registry key path. Ex. HKEY_LOCAL_MACHINE\SOFTWARE\MyApp
    @param srValueName: Specify registry value name. Ex. VirusCount
    @return: string value
    '''
    objReg = WinRegistry(
        strKey, win32con.KEY_SET_VALUE | win32con.KEY_QUERY_VALUE)
    try:
        value, vType = objReg.getValue(strValueName)
    except pywintypes.error, e:
        if str(e.args[0]) == '2':  # strValueName does not exist
            value, vType = None, None
        else:
            raise
    return value


def addValue(strKey, strValueName, value, strType):
    '''
    @param strKey: Specify registry key path. Ex. HKEY_LOCAL_MACHINE\SOFTWARE\MyApp
    @param srValueName: Specify registry value name. Ex. VirusCount
    @param value: Sepcify new registry value. Ex. 1
    @param strType: Specify value type. It's value should be: REG_BINARY,REG_DWORD,REG_SZ
    @return: 0 means success
    '''
    objReg = WinRegistry(
        strKey, win32con.KEY_SET_VALUE | win32con.KEY_QUERY_VALUE)
    try:
        value, vType = objReg.getValue(strValueName)
        raise RuntimeError('%s already exists.' % strValueName)
    except pywintypes.error, e:
        if str(e.args[0]) != '2':
            raise
    intType = getattr(win32con, strType)
    objReg.setValue(strValueName, value, intType)
    return 0


def setValue(strKey, strValueName, newValue):
    '''
    @param strKey: Specify registry key path. Ex. HKEY_LOCAL_MACHINE\SOFTWARE\MyApp
    @param srValueName: Specify registry value name. Ex. VirusCount
    @param newValue: Sepcify new registry value. Ex. 1
    @return: 0 means success
    '''
    objReg = WinRegistry(
        strKey, win32con.KEY_SET_VALUE | win32con.KEY_QUERY_VALUE)
    try:
        value, vType = objReg.getValue(strValueName)
    except pywintypes.error, e:
        if str(e.args[0]) == '2':  # strValueName does not exist
            value, vType = None, None
        else:
            raise
    if vType is None and newValue is None:
        raise RuntimeError('can NOT assign value "None" to nonexistent registry: "%s\\%s"!' % (strKey, strValueName))
    if vType is not None and value == newValue:
        return 0
    if vType is None:
        if isinstance(newValue, type('')):
            vType = win32con.REG_SZ
        else:
            vType = win32con.REG_DWORD
    objReg.setValue(strValueName, newValue, vType)
    return 0


def verifyRegistry(strRegFile):
    '''
    @return: 0 means all values in I{strRegFile} are identical to system registry.
        >0 means some values in I{strRegFile} are B{not} identical to system registry.
    '''
    dicKeyValue = parseRegFile(strRegFile)
    intResult = 0
    for key, lstValues in dicKeyValue.items():
        intRC = compareReg(key, lstValues)
        intResult += intRC
    return intResult


def parseRegFile(strRegFile):
    '''
    @param strRegFile: .reg file which is exported by regedit.exe
    @return: B{dicOutput}
        C{dicOutput = {key1:[[strValueName,intValueType,value],...], key2=[[strValueName,intValueType,value],...]}}
    '''
    lstEncodings = [None, locale.getdefaultlocale()[1]]
    if open(strRegFile, 'rb').read(2) in (codecs.BOM_UTF16_LE, codecs.BOM_UTF16_BE):
        lstEncodings.insert(0, 'UTF-16')
    elif open(strRegFile, 'rb').read(3) == codecs.BOM_UTF8:
        lstEncodings.insert(0, 'UTF-8')
    for strEncoding in lstEncodings:
        try:
            f = codecs.open(strRegFile, encoding=strEncoding)
            if f.readline() != 'Windows Registry Editor Version 5.00\r\n':
                f = codecs.open(strRegFile, encoding=strEncoding)
            break
        except UnicodeError, e:
            logging.info(e)
    else:
        raise e
    objConfigParser = ConfigParser.ConfigParser()
    objConfigParser.optionxform = str
    objConfigParser.readfp(f)
    f.close()
    dicOutput = {}
    for strKeyPath in objConfigParser.sections():
        dicOutput[strKeyPath] = []
        for option in objConfigParser.options(strKeyPath):
            s = objConfigParser.get(strKeyPath, option)
            lstValue = [option.strip('"')]
            s = s.strip()
            if not s:
                s = '""'
            if s[0] == '"' and s[-1] == '"':
                s = s.strip('"')
                if s:
                    s = s.replace('\\"', '"')
                    s = s.replace('\\\\', '\\')
                lstValue.append(win32con.REG_SZ)
                lstValue.append(s)
            else:
                if re.match('dword:', s, re.I):
                    lstValue.append(win32con.REG_DWORD)
                    lstValue.append(_convertDwordToInt(s.split(':')[1]))
                elif re.match('hex:', s, re.I):
                    lstValue.append(win32con.REG_BINARY)
                    lstValue.append(_hexToBinary(s[4:], 0))
                elif re.match('hex\(2\):', s, re.I):
                    lstValue.append(win32con.REG_EXPAND_SZ)
                    lstValue.append(_hexToBinary(s[7:]))
                elif re.match('hex\(7\):', s, re.I):
                    lstValue.append(win32con.REG_MULTI_SZ)
                    lstValue.append(_hexToBinary(s[7:]))
                else:
                    s = s.replace('\\"', '"')
                    s = s.replace('\\\\', '\\')
                    lstValue.append(win32con.REG_SZ)
                    lstValue.append(s)
            dicOutput[strKeyPath].append(lstValue)
    return dicOutput


def _hexToBinary(strHexString, encode=1):
    lstBuf = []
    for s in strHexString.split(','):
        if len(s) > 2 and s.startswith('\\\n'):
            s = s[2:]
        lstBuf.append(chr(int(s, 16)))
    if not encode:
        return ''.join(lstBuf)
    strCharset = locale.getdefaultlocale()[1]
    strBuf = unicode(''.join(lstBuf), 'utf-16').encode(strCharset)
    if strBuf[-1] == '\0':
        strBuf = strBuf[:-1]
    lst = strBuf.split('\0')
    if len(lst) == 1:
        return lst[0]
    else:
        return lst[:-1]


def _convertDwordToInt(strDword):
    s = binascii.a2b_hex(strDword)
    # "!l" means convert to long integer and use big-endian byte order
    return struct.unpack('!l', s)[0]


def compareReg(strKeyPath, lstReg, enableLog=1):
    '''
    @param strKeyPath: Registry key path. Ex. r"HKEY_LOCAL_MACHINE\SOFTWARE\TrendMicro\PC-cillinNTCorp"
    @param lstReg: lstReg=[[strValueName,intValueType,value],...]
        Ex. C{[['name',win32con.REG_SZ,'test'], ['count',win32con.REG_DWORD,1]]}
    @param enableLog: Specify 0 when you want disable logging. Default value is 1.
    @return: 0 means all registry values inside I{strKeyPath} are identical to I{lstReg}.
        1 means there are some values inside I{strKeyPath} which are not same with that inside I{lstReg}.
    '''
    try:
        obj = WinRegistry(r'%s' % strKeyPath)
    except:
        if enableLog:
            logging.error('Registry key "%s" does not exist.', strKeyPath)
        return 1

    isDifferent = 0
    logging.debug("Check registry values in %s" % strKeyPath)
    for strValueName, intValueType, value in lstReg:
        if enableLog:
            logging.debug('Check "%s"' % strValueName)
        try:
            currentValue, currentType = obj.getValue(strValueName)
        except pywintypes.error, e:
            if str(e.args[0]) == '2':
                if enableLog:
                    logging.error('Value "%s" does not exist.', strValueName)
                isDifferent = 1
                continue
            raise
        if currentType in (win32con.REG_DWORD_BIG_ENDIAN, win32con.REG_DWORD_LITTLE_ENDIAN):
            currentType = win32con.REG_DWORD
        if currentType != intValueType:
            if enableLog:
                logging.error('Value type of "%s" does not match:\nExpected: %s\nCurrent: %s' % (strValueName, g_dicValueType[intValueType], g_dicValueType[currentType]))
            isDifferent = 1
        if currentValue != value:
            if enableLog:
                logging.error('Registry value of "%s" does not match:\nExpected: %s\nCurrent: %s', strValueName, repr(value), repr(currentValue))
            isDifferent = 1
    return isDifferent


def valueExist(strKey, strValueName):
    '''
    Check if the specify registry value exists.
    @param strKey: Key path. Ex. 'HKEY_LOCAL_MACHINE\\SOFTWARE\\MyApp'
    @param srValueName: Specify registry value name. Ex. VirusCount
    @return: 2 = Fail (means value doesn't exist.); 0 = Pass (means exist.)
    '''
    objReg = WinRegistry(strKey, win32con.KEY_QUERY_VALUE)
    try:
        value, vType = objReg.getValue(strValueName)
    except pywintypes.error, e:
        if str(e.args[0]) == '2':
            return 2
    return 0


def exportRegKey(strKey, strFilePath):
    '''
    @return: 0 means export the specified registry key successfully.
    '''
    lstRegBackupCmd = ["regedit", "/e", strFilePath, strKey]
    obj = processUtil.TmProcess(lstRegBackupCmd)
    strStdout = urllib.quote(obj.readStdout(), '+?&')
    intReturnCode = obj.wait()
    if strStdout:
        logging.debug("exportRegKey stdout: %s", strStdout)
    if intReturnCode:
        logging.error("exportRegKey return %s", intReturnCode)
    return intReturnCode


def importRegKey(strFilePath):
    '''
    @return: 0 means import registry successfully.
    '''
    lstRegBackupCmd = ["regedit", "/s", strFilePath]
    obj = processUtil.TmProcess(lstRegBackupCmd)
    strStdout = urllib.quote(obj.readStdout(), '+?&')
    intReturnCode = obj.wait()
    if strStdout:
        logging.debug("importRegKey stdout: %s", strStdout)
    if intReturnCode:
        logging.error("importRegKey return %s", intReturnCode)
    return intReturnCode


def test():
    verifyRegistry(r"c:\python26\cpm\VS_RT_01_0060.reg")


def usage():
    print """Usage: python registryUtil.py <cmd> [-k <Key> -s <Key> -n <ValueName> -v <Value> -t <Type>]
    cmd             createKey | delKey | test | enumAllSubKey
    -k <Key>        Specifies the key which new subkey will be append or deleted. Ex. HKEY_LOCAL_MACHINE\Software
    -s <SubKey>     Specifies the key name to be created under the Key
    -n <ValueName>  Specifies the name of the value
    -v <Value>      Specifies the value
    -t <Type>       Specifies the type of value. It's value should be "REG_SZ"|"REG_DWORD"|"REG_BINARY"
    -a              Specifies delete all sub keys
    """


def main():
    try:
        strCmd = sys.argv[1]
        lstOpts, lstArgs = getopt.getopt(sys.argv[2:], "k:s:n:v:t:a")
    except:
        usage()
        return 2
    if strCmd not in ('createKey', 'deleteKey', 'test', 'enumAllSubKey'):
        usage()
        return 3
    dicOpts = {'-n': None, '-v': None, '-t': 'REG_SZ'}
    for o, a in lstOpts:
        dicOpts[o] = a
    try:
        if strCmd == 'createKey':
            strKey, strSubKey = dicOpts['-k'], dicOpts['-s']
        if strCmd == 'deleteKey':
            strKey = dicOpts['-k']
    except KeyError, e:
        usage()
        return 4
    intResult = 1
    if strCmd == 'test':
        test()
    if strCmd == 'createKey':
        intResult = createKey(strKey, strSubKey, dicOpts['-n'],
                              dicOpts['-v'], dicOpts['-t'])
    if strCmd == 'deleteKey':
        if '-a' in dicOpts:
            intResult = deleteKey(strKey, 1)
        else:
            intResult = deleteKey(strKey)
    if strCmd == 'enumAllSubKey':
        for s in enumAllSubKey(dicOpts['-k']):
            print s
    return intResult

if __name__ == '__main__':
    deleteValue(r'HKEY_LOCAL_MACHINE\SOFTWARE\TrendMicro\Vizor\ParentControl',
                'FilterGroupGategory26')
