import logging
from PySTAF import *
import gettext
_ = gettext.gettext


class StafService:
    def __init__(self):
        #get staf handle
        try:
            self.handle = STAFHandle("deployScript")
        except STAFException, e:
            loggin.info(_("Error registering with STAF, RC: %d") % e.rc)
            sys.exit(e.rc)

    def callStafService(self, host, service, cmd):
        #ex. result = handle.submit("local", "ping", "ping")
        result = self.handle.submit(host, service, cmd)
        if (result.rc != 0):
            logging.info(_("Error submitting request, RC: %d, Result: %s")
                         % (result.rc, result.result))
        else:
            logging.info(_("Ok submitting request"))
        return result.rc

    def __del__(self):
        #destroy staf handle
        rc = self.handle.unregister()
