import unittest
import tests
import sclib
import os

from sclib.sc.connection import SCConnection
from tests.unit.sc.connectionfilter import SCConnectionFilter

class SCBaseTestCase(unittest.TestCase):
    def __init__(self, methodName='runTest'):
        unittest.TestCase.__init__(self, methodName)
        self.connection = None
        self.auth = None
        
        # make sample path
        self.sample_path = os.path.join(os.path.dirname(os.path.abspath(tests.__file__ )), 'unit', 'sample')
        # make result path
        self.result_path = os.path.join(os.path.dirname(os.path.abspath(tests.__file__ )), 'unit', 'result')


    def setUp(self):
        if not self.connection:
            path = os.path.join(self.result_path, '%s.%s' % (self.__class__.__name__, self._testMethodName) )
            if not os.path.exists(path):
                os.makedirs(path)

            logpath = os.path.join(path, 'testCase.log' )
            sclib.set_file_logger(self._testMethodName, logpath, 'DEBUG')
            self.connection = SCConnectionFilter( sclib.__config__.get('connection', 'MS_HOST'),
                                                  sclib.__config__.get('connection', 'MS_BROKER_NAME'), 
                                                  sclib.__config__.get('connection', 'MS_BROKER_PASSPHASE'),
                                                  result_path=path)
            self.assertNotEqual(self.connection, None)

        if self.connection and (not self.auth):        
            self.auth = self.connection.basicAuth( sclib.__config__.get('authentication', 'AUTH_NAME'), 
                                                   sclib.__config__.get('authentication', 'AUTH_PASSWORD'))
            self.assertNotEqual(self.auth, None)
        
    def tearDown(self):
        self.connection.close()
        pass
    
if __name__ == '__main__':
    unittest.main()