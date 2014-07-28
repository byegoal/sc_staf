import PySTAF


class StafQueue:
    strGetCmd = ''

    def __init__(self, stafHandle, strLocation):
        self._handle = stafHandle
        self._strLocation = strLocation

    def get(self, strType, intTimeout, isPeek=0):
        if isPeek:
            strRequest = "PEEK TYPE %s WAIT" % strType
        else:
            strRequest = "GET TYPE %s WAIT" % strType
        if intTimeout:
            strRequest += ' %s' % (int(intTimeout * 1000))
        stafResult = self._handle.submit(
            self._strLocation, 'QUEUE', strRequest)
        if not stafResult.isOk():
            return stafResult, {}
        dic = stafResult.getResult()
        return stafResult, dic['message']

    def peek(self, strType, intTimeout):
        return self.get(strType, intTimeout, 1)

    def send(self, strType, strMsg, intRemoteHandle=None):
        if intRemoteHandle:
            strHandle = 'HANDLE %s' % intRemoteHandle
        else:
            strHandle = ''
        strRequest = 'QUEUE %s TYPE %s MESSAGE %s' % (
            strHandle, strType, PySTAF.wrapData(strMsg))
        stafResult = self._handle.submit(
            self._strLocation, 'QUEUE', strRequest)
        return  stafResult
