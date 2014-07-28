import sclib
import os
import io
import datetime
import tests
import copy
import StringIO
import urllib

from sclib.client.connection import SCClientConnection
from time import gmtime, strftime

class SCClientConnectionFilter(SCClientConnection):
    #-------------------------------------------------------------------------------
    # filter connection class for agent/provisioning service
    #-------------------------------------------------------------------------------
    #===========================================================================
    # A filter connection class to simulate request. 
    # The class also capture Request and Response into specified result folder.
    #===========================================================================
    def __init__( self, host_base, broker_name=None, broker_passphase=None, 
                  sample_path=None, result_path=None):
        SCClientConnection.__init__(self, host_base, broker_name, broker_passphase)

        # pseudo sample path
        self.sample_path = sample_path
        self.result_path = result_path
        
        if os.path.isdir(self.result_path) == False:
            os.makedirs(self.result_path)

        
    def make_request(self, action='', params=None, headers=None, data='', method='GET'):

        # local var
        fake = None

        if self.sample_path:
            reqfile = action.replace('/', '^')
            reqfile = os.path.join(self.sample_path, '[Response]%s.xml' % (reqfile) )
            rf = io.open(reqfile, 'r')
            fake = urllib.addinfourl(rf, 'Fake info', regfile, 400)
            return fake
        
        else:
            reqfile = action.replace('/', '^')
            reqfile = os.path.join(self.result_path, '[Request(%s)]%s.xml' % (method, reqfile ) )
            resfile = action.replace('/', '^')
            resfile = os.path.join(self.result_path, '[Response]%s.xml' % (resfile) )

            # serialize Request data
            rf = io.open(reqfile, 'w')
            if (data is not None) and (len(data) != 0):
                rf.write(self.nice_format(data))
            rf.close()

            # make request to securecloud
            response = SCClientConnection.make_request(self, action, params, headers, data, method)
            if response:
                body = response.read()
                
                #make fake response
                resfp = StringIO.StringIO(body)
                fake = urllib.addinfourl(resfp, response.info(), response.geturl(), response.getcode())
                
                # serialize Response data
                f = io.open(resfile, 'w')
                if (body is not None) and (len(body) != 0):
                    f.write(self.nice_format(body))
                f.close()
                return fake

        return fake
