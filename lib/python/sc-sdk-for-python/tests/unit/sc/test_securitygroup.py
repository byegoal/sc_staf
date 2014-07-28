"Test basic security group function"
import unittest
import logging
import string
import random

from sclib.sc.securitygroup import SecurityGroup, SecurityGroupAction
from sclib.sc.instance import VirtualMachine
from tests.unit import logging
from tests.unit.sc import SCBaseTestCase

class SCSecurityGroupTest(SCBaseTestCase):
    def setUp(self):
        SCBaseTestCase.setUp(self)
        
        #===== implement initial code here for each test =====
        pass

    def testListAllPolicy(self):
        policys = self.connection.listAllSecurityGroup()
        for policy in policys:
            sec = self.connection.getSecurityGroup(policy.id)
            self.assertEqual(policy.id, sec.id)
            xml_pretty = sec.niceFormat()
            logging.debug(xml_pretty)

            
    def testListAllRuleTypes(self):
        rulelist = self.connection.listAllSecurityRuleTypes()
        for rule in rulelist:
            newrule = self.connection.getSecurityRuleType(rule.id)
            self.assertEqual(rule.id, newrule.id)
            xml_pretty = newrule.niceFormat()
            logging.debug(xml_pretty)

    def testGetPolicy(self):

        target_id = '245e35df-492a-40c8-8543-b07e1e252744'
        policy = self.connection.getSecurityGroup(target_id)    

        self.assertEqual(policy.name, 'Default Policy')
        self.assertEqual(policy.id, target_id)
        self.assertEqual(policy.EnableIC, 'false')


    def testCreatePolicy(self):

        policyName="testCreatePolicy"

        # create policy
        policy = self.connection.createSecurityGroup(policyName)
        self.assertNotEqual(policy, None)
        # validate default
        self.assertEqual(policy.successAction.action, 'ManualApprove')
        self.assertEqual(policy.failedAction.action, 'ManualApprove')
        self.assertEqual(policy.ruleCount, '0')
        self.assertEqual(policy.name, policyName)
        self.assertEqual(policy.EnableIC, 'false')
        self.assertEqual(policy.ICAction, 'Nothing')
        self.assertEqual(policy.PostponeEnable, 'false')
        self.assertEqual(policy.RevokeIntervalNumber, '0')
        self.assertEqual(policy.isNameEditable, 'true')

        # delete created policy 
        res = self.connection.deleteSecurityGroup(policy.id)
        self.assertEqual(res, 204)

    def testAddVM(self):
        policys = self.connection.listAllSecurityGroup()
        self.vms = self.connection.listAllVM()

        default_policy = None
        test_policy = None
        for policy in policys:
            sec = self.connection.getSecurityGroup(policy.id)
            self.assertEqual(policy.id, sec.id)

            if policy.name == 'Default Policy':
                default_policy = sec
            elif policy.name == 'TESTING':
                test_policy = sec

        # move all vm into test policy
        for vm in self.vms:
            new_vm = VirtualMachine(self.connection)
            new_vm.imageGUID = vm.imageGUID
            test_policy.addVM(new_vm)

        response = None
        response = test_policy.update()
        self.assertEqual(response, 200)

        # move all vm back to default policy
        default = self.connection.getSecurityGroup(default_policy.id)
        for vm in self.vms:
            new_vm = VirtualMachine(self.connection)
            new_vm.imageGUID = vm.imageGUID
            default.vmList.append(new_vm)

        response = default.update()
        self.assertEqual(response, 200)
     



if __name__ == '__main__':
    unittest.main()