#!/usr/bin/env python
# Copyright (c) 2012 Trend Micro, Inc. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish, dis-
# tribute, sublicense, and/or sell copies of the Software, and to permit
# persons to whom the Software is furnished to do so, subject to the fol-
# lowing conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABIL-
# ITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT
# SHALL THE AUTHOR BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS
# IN THE SOFTWARE.
#

"Test basic device"
import unittest
import logging

from sclib.sc.keyrequest import KeyRequest
from tests.unit.sc import SCBaseTestCase

class SCRequestTest(SCBaseTestCase):
    def setUp(self):
        SCBaseTestCase.setUp(self)

        #===== implement initial code here for each test =====
        pass

    def testAllRunningVM(self):

        self.runningVM = self.connection.listAllRunningVM()
        self.assertNotEqual(self.runningVM, None)

        for vm in self.runningVM:
            xml_pretty = vm.niceFormat()
            logging.debug(xml_pretty)
            
            keyRequest = self.connection.listKeyRequest(vm.runningVMKeyRequest.requestID)
            status = keyRequest.run_icm()
            self.assertNotEqual(status, 200)

    

if __name__ == '__main__':
    unittest.main()