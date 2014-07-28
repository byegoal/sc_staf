#!/usr/bin/env python

"Test basic connection"
import unittest
import logging

from tests.unit import logging
from tests.unit.sc import SCBaseTestCase
from sclib.sc.device import Device
from sclib.sc.user import User

class SCConnectionTest(SCBaseTestCase):
    def setUp(self):
        SCBaseTestCase.setUp(self)

        #===== implement initial code here for each test =====
        pass
             
    def testListAllUsers(self):
        userlist = self.connection.listAllUsers()
        for user in userlist:
            xml_pretty = user.niceFormat()
            logging.debug(xml_pretty)
            
    def testListAllSecurityGroup(self):
        policylist = self.connection.listAllSecurityGroup()
        for policy in policylist:
            xml_pretty = policy.niceFormat()
            logging.debug(xml_pretty)

if __name__ == '__main__':
    unittest.main()