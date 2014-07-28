from PySTAF import *


class StafService:

    def __init__(self):
        #get staf handle
        try:
            self.handle = STAFHandle("deployScript")
        except STAFException, e:
            print "Error registering with STAF, RC: %d" % e.rc
            import sys
            sys.exit(e.rc)

    def callStafService(self, host, service, cmd):
        #ex. result = handle.submit("local", "ping", "ping")
        result = self.handle.submit(host, service, cmd)
        if (result.rc != 0):
            print "Error submitting request, RC: %d, Result: %s" % (
                result.rc, result.result)
            return 1
        return 0

    def __del__(self):
        #destroy staf handle
        rc = self.handle.unregister()
