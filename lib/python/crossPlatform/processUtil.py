import subprocess
import os


class TmProcess(subprocess.Popen):
    def __init__(self, *lstArgs, **dicArgs):
        self.stdoutReaded = 0
        self._strBuf = ''
        if 'stdin' not in dicArgs:
            dicArgs['stdin'] = subprocess.PIPE
        if 'stdout' not in dicArgs:
            dicArgs['stdout'] = subprocess.PIPE
        if 'stderr' not in dicArgs:
            dicArgs['stderr'] = subprocess.STDOUT
        if 'universal_newlines' not in dicArgs:
            dicArgs['universal_newlines'] = 1
        if 'executable' in dicArgs and dicArgs['executable']:
            strExecutable = dicArgs['executable']
        else:
            if isinstance(lstArgs[0], (list, tuple)):
                strExecutable = lstArgs[0][0]
            else:
                strExecutable = lstArgs[0]
        if 'shell' in dicArgs and isinstance(lstArgs[0], (list, tuple)):
            lstTmp = ['"%s"' % subprocess.list2cmdline(lstArgs[0])]
            lstTmp.extend(lstArgs[1:])
            lstArgs = tuple(lstTmp)
        try:
            super(TmProcess, self).__init__(*lstArgs, **dicArgs)
        except OSError, e:
            if e.errno in (2, 3):
                e.strerror += ' "%s"' % strExecutable
                raise e
            else:
                raise
        except:
            import sys
            print sys.exc_info()[:2]

    def readStdout(self):
        if self.stdoutReaded:
            s = self._strBuf
            self._strBuf = ''
            return s
        return self.stdout.read()

    def wait(self):
        if not self.stdoutReaded:
            self._strBuf = self.stdout.read()
            self.stdoutReaded = 1
        return super(TmProcess, self).wait()


def killByName(strMatchStr, noError=1):
    '''
    Kill the process according to strMatchStr. This function use partial match to find the specified process.

    @param strMatchStr: Specify matching string.
    @param noError: Specify if you want to ignore "process not found" error. Default is True.
    @return:
        0 means kill process successfully.
        1 means process is not found.
    '''
    #get process id's for the given process name
    if os.name == 'nt':
        import winProcessUtil
        return winProcessUtil.killByName(strMatchStr, noError)
    else:
        raise NotImplementedError('Does NOT support non-windows platform yet!')

##def checkProcessExist(strMatchStr, intTimeout=1):
##    '''
##    Check if the process exists according to strMatchStr. This function use partial match to find the specified process.
##    You can assign a timeout value to wait until process appeared.
##
##    @param strMatchStr: Specify matching string.
##    @param intTimeout:
##    @return:
##        0 means process exists.
##        2 means process is not found.
##    '''
##    raise NotImplementedError()
##
##def createProcess(lstArgs,waitProcessExit=0,strPidFile=''):
##    '''
##    Launch an external program. Executable should be placed in the front of lstArgs.
##    If you need to dump PID into a file, specify a full file path in strPidFile
##
##    @return: Always return 0 if waitProcessExit=0 otherwise it will return the exit code after process exits.
##    '''
##    raise NotImplementedError()
##
##def terminateProcess(strPidFile,removePidFile=0):
##    '''
##    Terminate process by PID file
##    @strPidFile: PID file name
##    @Return "0" if launch successfully; Return "2" if otherwise
##    '''
##    raise NotImplementedError()
