import unittest
from tests.unit import config


class SCAuthConnectionTest(unittest.TestCase):
    def setUp(self):
        from sclib.connection import SCAuthConnection
        self.connection = SCAuthConnection( config.get('connection', 'MS_HOST'),
                                            config.get('connection', 'MS_BROKER_NAME'), 
                                            config.get('connection', 'MS_BROKER_PASSPHASE') )

    def testGetRequest(self):
        response = self.connection.make_request('PublicCertificate')
        self.assertNotEqual(response, None)
  
        
if __name__ == "__main__":
    unittest.main()

    