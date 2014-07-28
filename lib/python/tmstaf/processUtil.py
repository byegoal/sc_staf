import subprocess
import os

import platformUtil


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
        if self.stdout:
            return self.stdout.read()
        else:
            return ''

    def wait(self):
        if not self.stdoutReaded:
            if self.stdout:
                self._strBuf = self.stdout.read()
            else:
                self._strBuf = ''
            self.stdoutReaded = 1
        return super(TmProcess, self).wait()


def call(*popenargs, **kwargs):
    """Run command with arguments.  Wait for command to complete, then
    return the returncode attribute.

    The arguments are the same as for the Popen constructor.  Example:

    retcode = call(["ls", "-l"])
    """
    return TmProcess(*popenargs, **kwargs).wait()


def getAllProcessId():
    if platformUtil.isWindows():
        import win32process
        return win32process.EnumProcesses()
    else:
        obj = TmProcess(['ps', 'ax', '-o', 'pid'])
        return [int(s.strip()) for s in obj.readStdout().splitlines() if s.strip().isdigit()]
