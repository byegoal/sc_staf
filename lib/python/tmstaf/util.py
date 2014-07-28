import logging
import os
import sys
import traceback
import cStringIO
import socket
import select
import re
import HTMLParser
import htmlentitydefs
import tmstaf.iniparse
import tmstaf.platformUtil


def runRemoteTmstaf(strHost, lstCmd, strWorkingPath, intTimeout=86400, intLoopTimes=60, intInterval=1):
    '''
    Run TMSTAF in a remote machine. This function will restart(resume) TMSTAF if it finds any test step reboots the machine.
    It waits the machine reboot by calling waitReboot().
    @param strHost: the remote machine hostname or IP
    @param lstCmd: TMSTAF command line
    @param strWorkingPath: working path
    @param intTimeout: how long does it wait for TMSTAF finished. Default is 86400 seconds
    @param intLoopTimes: loop how many times to wait remote shutdown and start, default is 60 times
    @param intInterval: sleep how many seconds in each loop of waiting remote shutdown
    @return: 0 means success; otherwise return 1
    '''
    #To prevent TMSTAF depending on STAF, we should not import staf package in module level
    import staf.util
    import staf.processHelper
    while 1:
        strFullCmd = '%s %s' % (os.path.join(
            strWorkingPath, lstCmd[0]), ' '.join(lstCmd[1:]))
        logging.info('run "%s" on %s', strFullCmd, strHost)
        objStafProcess = staf.processHelper.AsyncStafProcess(
            strHost, lstCmd, strWorkingPath, shell=True)
        intRc = objStafProcess.wait(intTimeout)
        strStdout = objStafProcess.readStdout()
        strStderr = objStafProcess.readStderr()
        if strStdout:
            logging.getLogger(strHost).propagate = 0
            logging.getLogger(strHost).debug('stdout:\n%s', strStdout)
            logging.getLogger(strHost).propagate = 1
        if strStderr:
            logging.getLogger(strHost).propagate = 0
            logging.getLogger(strHost).debug('stderr:\n%s', strStderr)
            logging.getLogger(strHost).propagate = 1
        if intRc == staf.util.ERR_REBOOT:
            objStafProcess.disableAutoFree()
            del objStafProcess
            logging.info('%s will be reboot...', strHost)
            if waitReboot(strHost, intLoopTimes, intInterval):
                return 1
            lstCmd = [lstCmd[0], '--resume']
        else:
            logging.info('run "%s" return %s', strFullCmd, intRc)
            return intRc


def waitReboot(strHost, intLoopTimes=60, intInterval=1):
    '''
    Wait remote machine to reboot. The function will ping remote until it shutdown and wait it to start successfully.
    If the machine doesn't shutdown first, it will return fail directly.
    @param strHost: remote host name or IP
    @param intLoopTimes: loop how many times to wait remote shutdown and start, default is 60 times
    @param intInterval: sleep how many seconds in each loop of waiting remote shutdown
    @return: 0 means success; otherwise return 1
    '''
    #To prevent TMSTAF depending on STAF, we should not import staf package in module level
    import staf.util
    logging.info('waiting for %s shutdown in %s seconds ...', strHost,
                 intLoopTimes * intInterval)
    if staf.util.waitStafQuit(strHost, intLoopTimes, intInterval):
        logging.error('wait %s shutdown timeout error!', strHost)
        return 1
    logging.info(
        '%s shutdown successfully; start waiting it to start...', strHost)
    if staf.util.waitStafReady(strHost, intLoopTimes):
        logging.error('wait %s start timeout error!', strHost)
        return 1
    logging.info('%s start successfully', strHost)
    return 0


def getException():
    f = cStringIO.StringIO()
    f.write('Traceback (most recent call last):\n')
    lstTmp = traceback.extract_stack(sys.exc_info()[2].tb_frame)
    lstTmp = lstTmp[:-1]  # remove getException self
    x = traceback.extract_tb(sys.exc_info(
        )[2])  # retrieve exception stack inside "try" statement
    lstTmp.extend(x)
    for lst in lstTmp:
        f.write('  File "%s", line %s, in %s\n' % lst[:3])
        if lst[3]:
            f.write('    %s\n' % lst[3])
    exc_type, exc_value = sys.exc_info()[:2]
    f.write('%s: %s\n' % (exc_type.__name__, exc_value))
    return f.getvalue()


def upgradeIniFile(strNewVersionIni, strCurrentIni):
    '''
    Upgrade an INI file according to another INI file which has new sections or new options
    @param strNewVersionIni: the INI file which has new sections or new versions
    @param strCurrentIni: the INI file need to be upgraded.
    @return: 0 means success; otherwise raise exception
    '''
    cfgCurrent = tmstaf.iniparse.INIConfig(
        file(strCurrentIni), optionxformvalue=None)
    cfgNew = tmstaf.iniparse.INIConfig(
        file(strNewVersionIni), optionxformvalue=None)
    updated = 0
    for strSection in cfgNew:
        if strSection not in cfgCurrent:
            logging.info('Add new section: %s', strSection)
            for strOption in cfgNew[strSection]:
                logging.info('Add new option: %s.%s=%s', strSection,
                             strOption, cfgNew[strSection][strOption])
                setattr(getattr(cfgCurrent, strSection),
                        strOption, cfgNew[strSection][strOption])
            updated = 1
            continue
        for strOption in cfgNew[strSection]:
            if strOption not in cfgCurrent[strSection]:
                logging.info('Add new option: %s.%s=%s', strSection,
                             strOption, cfgNew[strSection][strOption])
                setattr(getattr(cfgCurrent, strSection),
                        strOption, cfgNew[strSection][strOption])
                updated = 1
    if updated:
        strBuf = str(cfgCurrent)
        del cfgCurrent
        f = open(strCurrentIni, 'wb')
        f.write(strBuf)
        f.close()
    return 0


def getIpList():
    try:
        hostname, aliaslist, ipaddrlist = socket.gethostbyname_ex(
            socket.gethostname())
        return ipaddrlist
    except:
        return ['']


def getHostName():
    if os.name == 'nt':
        return os.environ.get('computername')
    else:
        return socket.gethostname()


def timeoutPrompt(strPrompt, intTimeout=10):
    print ''
    if tmstaf.platformUtil.isWindows():
        import win32event
        import win32console
        import win32api
        h = win32console.GetStdHandle(win32console.STD_INPUT_HANDLE)
        try:
            for i in (range(intTimeout)):
                intRc = win32event.WaitForSingleObject(h, 1 * 1000)
                if intRc == win32event.WAIT_TIMEOUT:
                    print '\r', strPrompt, 'count down %s seconds' % (
                        intTimeout - i),
                else:
                    break
            print ''
            if intRc == win32event.WAIT_TIMEOUT:
                return ''
            elif intRc == win32event.WAIT_OBJECT_0:
                return sys.stdin.read(1)
            else:
                logging.error('win32event.WaitForSingleObject() return error: %s', intRc)
        finally:
            win32api.CloseHandle(h)
    else:
        for i in (range(intTimeout)):
            rlist, _, _ = select.select([sys.stdin], [], [], 1)
            if not rlist:
                print strPrompt + ' count down %s seconds' % (intTimeout - i)
                os.system('tput cuu1')
            else:
                break
        print ''
        if rlist:
            return sys.stdin.read(1)
        else:
            return ''


class HtmlToTextParser(HTMLParser.HTMLParser):
    def __init__(self):
        HTMLParser.HTMLParser.__init__(self)
        self.__lstText = []

    def handle_data(self, data):
        if len(data) > 0:
            data = re.sub('[\r\n]+', '', data)
            data = re.sub('[\t]+', ' ', data)
            self.__lstText.append(data)

    def handle_endtag(self, tag):
        if tag == 'p':
            self.__lstText.append('\r\n\r\n')
        elif tag == 'br':
            self.__lstText.append('\r\n')

    def handle_charref(self, name):
        if name[0] in ['x', 'X']:
            c = int(name[1:], 16)
        else:
            c = int(name)
        self.__lstText.append(unichr(c))

    def handle_entityref(self, name):
        if name.lower() == 'nbsp':
            self.__lstText.append(' ')
        else:
            strBuf = htmlentitydefs.entitydefs[name]
            self.__lstText.append(strBuf)

    def handle_startendtag(self, tag, attrs):
        if tag == 'br':
            self.__lstText.append('\r\n')

    def text(self):
        return ''.join(self.__lstText).strip()


def removeHtmlTag(strHtml):
    '''
    This function will remove all html tag from strHtml. It will replace <p> with \r\n\r\n and <br> with \r\n
    @param strHtml: specify a string that contains html tag
    @return: a string without html tag
    '''
    parser = HtmlToTextParser()
    parser.feed(strHtml)
    parser.close()
    return parser.text()
