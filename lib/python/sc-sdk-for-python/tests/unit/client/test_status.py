#!/usr/bin/env python

"Test basic connection"
import unittest
import logging
import os
import tests

from tests.unit import config, logging
from tests.unit.sc.connectionfilter import SCClientConnectionFilter


class SCClientConnectionTest(unittest.TestCase):
        
    def setUp(self):
        self.connection = None

        # make sample path
        self.sample_path = os.path.join(os.path.dirname(os.path.abspath(tests.__file__ )), 'unit', 'sample')
        # make result path
        self.result_path = os.path.join(os.path.dirname(os.path.abspath(tests.__file__ )), 'unit', 'result')

        if not self.connection:
            self.connection = SCClientConnectionFilter( config.get('client', 'agent_service'),
                                                        result_path=self.result_path)
            self.assertNotEqual(self.connection, None)

    def testStatus(self):
        response = self.connection.status()
        self.assertNotEqual(response, None)
 

if __name__ == '__main__':
    unittest.main()