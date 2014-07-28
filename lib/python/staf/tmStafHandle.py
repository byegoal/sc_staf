import PySTAF

# g_dicStafErr is based on STAF 3.2.2
g_dicStafErr = {
    0: 'No error',
    1: 'Invalid API',
    2: 'Unknown service',
    3: 'Invalid handle',
    4: 'Handle already exists',
    5: 'Handle does not exist',
    6: 'Unknown error',
    7: 'Invalid request string',
    8: 'Invalid service result',
    9: 'REXX Error',
    10: 'Base operating system error',
    11: 'Process already complete',
    12: 'Process not complete',
    13: 'Variable does not exist',
    14: 'Unresolvable string',
    15: 'Invalid resolve string',
    16: 'No path to endpoint',
    17: 'File open error',
    18: 'File read error',
    19: 'File write error',
    20: 'File delete error',
    21: 'STAF not running',
    22: 'Communication error',
    23: 'Trusteee does not exist',
    24: 'Invalid trust level',
    25: 'Insufficient trust level',
    26: 'Registration error',
    27: 'Service configuration error',
    28: 'Queue full',
    29: 'No queue element',
    30: 'Notifiee does not exist',
    31: 'Invalid API level',
    32: 'Service not unregisterable',
    33: 'Service not available',
    34: 'Semaphore does not exist',
    35: 'Not sempahore owner',
    36: 'Semaphore has pending requests',
    37: 'Timeout',
    38: 'Java error',
    39: 'Converter error',
    40: 'Not used',
    41: 'Invalid object',
    42: 'Invalid parm',
    43: 'Request number not found',
    44: 'Invalid asynchronous option',
    45: 'Request not complete',
    46: 'Process authentication denied',
    47: 'Invalid value',
    48: 'Does not exist',
    49: 'Already exists',
    50: 'Directory Not Empty',
    51: 'Directory Copy Error',
    52: 'Diagnostics Not Enabled',
    53: 'Handle Authentication Denied',
    54: 'Handle Already Authenticated',
    55: 'Invalid STAF Version',
    56: 'Request Cancelled',
    57: 'Create thread error',
    5001: 'Process exit with error'}


class TmStafHandle(PySTAF.STAFHandle):
    '''Usage:
        h=TmStafHandle('test', handleType = 0)
        result=h.submit('localhost','PING','ping',h.Synchronous)
    handleType= 0:Standard | 1:Static
    '''

    Synchronous = PySTAF.STAFHandle.Synchronous
    FireAndForget = PySTAF.STAFHandle.FireAndForget
    Queue = PySTAF.STAFHandle.Queue
    Retain = PySTAF.STAFHandle.Retain
    QueueRetain = PySTAF.STAFHandle.QueueRetain

    def __init__(self, *argv, **karg):
        try:
            PySTAF.STAFHandle.__init__(self, *argv, **karg)
        except PySTAF.STAFException, e:
            raise RuntimeError('(%s, %s, %s)' % (e.rc, g_dicStafErr.get(
                e.rc, 'Unknown error'), e.result))
        self.setDoUnmarshallResult(0)

    def __del__(self):
        if self.handle:
            self.unregister()

    def submit(self, location, service, request, mode=PySTAF.STAFHandle.Synchronous):
        '''mode = Synchronous | FireAndForget | Queue | Retain | QueueRetain
        '''
        stafResult = PySTAF.STAFHandle.submit(
            self, location, service, request, mode)
        return TmStafResult(stafResult.rc, stafResult.result, location, service, request)


class TmStafResult(PySTAF.STAFResult):

    TmProcessExitWithError = 5001

    def __init__(self, rc, result, location='', service='', request=''):
        PySTAF.STAFResult.__init__(self, rc, result, 0)
        self.location = location
        self.service = service
        self.request = request

    def __str__(self):
        if self.rc == 0:
            return repr(self.getResult())
        else:
            if self.result:
                if PySTAF.isMarshalledData(self.result):
                    self.result = PySTAF.unmarshall(
                        self.result).getRootObject()
                return '(RC:%s, %s: %s)' % (self.rc, g_dicStafErr.get(self.rc, 'Service specific error'), self.result)
            else:
                return '(RC:%s, %s)' % (self.rc, g_dicStafErr.get(self.rc, 'Service specific error'))

    def getResult(self):
        if self.rc == 0 and PySTAF.isMarshalledData(self.result):
            try:
                return PySTAF.unmarshall(self.result).getRootObject()
            except:
                import logging
                import os
                import time
                strDumpFile = os.path.join(os.getcwd(), time.strftime(
                    'tmStafResult_dump_%Y%m%d%H%M%S.txt'))
                logging.error('unmarshall result failed! dump result to "%s"',
                              strDumpFile)
                open(strDumpFile, 'wb').write(self.result)
                raise
        return self.result

    def isOk(self):
        return self.rc == self.Ok

    def isTimeout(self):
        return self.rc == self.Timeout

    def isNotExist(self):
        return self.rc == self.DoesNotExist

if __name__ == '__main__':
    h = TmStafHandle("test")
    r = h.submit('local', 'ping', 'ping')
    print r
    print h.submit('192.168.100.255', 'ping', 'ping')
    print h.submit('local', 'test', 'test')
    print h.submit('local', 'log', 'test')
