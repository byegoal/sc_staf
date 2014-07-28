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

import unittest
from sclib.sc.administration import Timezone, License
from tests.unit.sc import SCBaseTestCase

class SCAdministrationTest(SCBaseTestCase):
    def setUp(self):
        SCBaseTestCase.setUp(self)

        #===== implement initial code here for each test =====

    def testListTimezone(self):
        timezones = self.connection.listTimezone()
        self.assertNotEqual(timezones.__len__, 0)

        # put validation code here

    def testServiceStatus(self):
        #status = self.connection.getServiceStatus()
        status = self.connection.getEntrypoint()
        self.assertEqual(status, 200)
 
    def testGetLicense(self):
        license = self.connection.getLicense()
        self.assertNotEqual(license, None)
        if license:
            self.assertEqual(license.verifyStatus, 'VALID')

    def testListLanguages(self):
        langs = self.connection.listLanguages()
        self.assertNotEqual(langs, None)
        if langs:
            for i in langs:
                # test for default value
                if i.languageCode == 'en                  ':
                    self.assertEqual(i.isDefault, 'true')
                else:
                    self.assertEqual(i.isDefault, 'false')


if __name__ == '__main__':
    unittest.main()