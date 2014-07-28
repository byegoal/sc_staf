"Test basic connection"
import unittest
import logging
import base64
import random
import sclib

from tests.unit.sc import SCBaseTestCase
from tests.unit.sc.connectionfilter import SCConnectionFilter
from sclib.sc.device import Device
from sclib.sc.user import User, UserRight, UserRole, Account

class SCUserTest(SCBaseTestCase):
    def setUp(self):
        SCBaseTestCase.setUp(self)
        self.users = self.connection.listAllUsers()

    def testCreateUser(self):

        users = []
        for i in range(1, 20):
            email = 'unittest+%s@securecloud.com' % i
            password = 'P@ssw0rd'
            auth = 'localuser'
            name = 'unit%s' % i
            first = 'test%s' % i
            roles = ['Administrator', 'Security Administrator', 
                     'Auditor', 'Key Approver', 'Data Analyst']
            MFA = ['true', 'false']

            user = self.connection.createUser( email,
                                               password,
                                               auth,
                                               name,
                                               first,
                                               email,
                                               roles[random.choice(range(1, len(roles)))],
                                               MFA[random.choice(range(1, len(MFA)))])
            self.assertNotEqual(user, None)
            if user:
                user.firstName = 'Updated'
                user.lastName = roles[random.choice(range(1, len(roles)))]
                user.setRole( roles[random.choice(range(1, len(roles)))],
                              MFA[random.choice(range(1, len(MFA)))] )
                res = user.update()
                self.assertNotEqual(res, None)

                # add into list
                users.append(user)

        # delete all user
        for u in users:
            res = u.delete()
            self.assertEqual(res, True)
  
    def testGetUser(self):      
        for user in self.users:  
            u = self.connection.getUser(user.id)
            self.assertNotEqual(u, None)
            self.assertEqual(user.id, u.id)
            
        # testGet current user
        current = self.connection.getUser(self.connection.authentication.id)
        self.assertEqual(current.id, self.connection.authentication.id)

    def testChangePassword(self):

        # update passoword and validate
        email = sclib.__config__.get('authentication', 'AUTH_NAME')
        oldPassword = sclib.__config__.get('authentication', 'AUTH_PASSWORD')
        newPassword = '1qaz@WSX'
        res = self.connection.changeUserPassword(oldPassword, newPassword)
        self.assertNotEqual(res, None)

        # reset original password
        res = self.connection.changeUserPassword(newPassword, oldPassword)
        self.assertNotEqual(res, None)

    def testGetRights(self):      
        rights = self.connection.getUserRights()
        for right in rights:  
            self.assertNotEqual(right.right, None)

    def testValidateAccount(self):
        account = self.connection.getAccount()
        self.assertEqual(account.id, self.connection.account.id)
        self.assertEqual(account.name, self.connection.account.name)
        self.assertEqual(account.passphrase, self.connection.account.passphrase)

    def testUpdateAccount(self):
        test_passphrase = '12345678'
        account = self.connection.account
        account.sessionTimeout = '30'
        account.update()
        # temporaliy failed, because not merge with 
        self.assertEqual(account.sessionTimeout, '30')

    def testSetPassphrase(self):
        test_passphrase = '12345678'
        account = self.connection.account
        account.passphrase = test_passphrase
        account.setPassphrase(test_passphrase)
        # temporaliy failed, because not merge with 
        self.assertEqual(account.passphrase, test_passphrase)


if __name__ == '__main__':
    unittest.main()