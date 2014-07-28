"Test basic security group function"
import unittest
import logging
import string
import random
import uuid

from sclib.sc.device import Device, Volume
from sclib.sc.securitygroup import SecurityGroup, SecurityGroupAction
from sclib.sc.instance import VirtualMachine
from tests.unit import logging
from tests.unit.sc import SCBaseTestCase
from tests.unit.sc import testlib

class SCTrackerTest(SCBaseTestCase):
    def setUp(self):
        SCBaseTestCase.setUp(self)

    # Some variable
    name = 'template'
    filesystem = 'ext3'
    mountpoint = '/mnt/template'
    RAID_Device1 = '596364df-05f3-48d7-aa86-5223897421d1'
    RAID_Device2 = '31932062-5d64-46a6-b637-ac96dfc0c9e3'

    # ===== Test Cases covers Team Tracker =====
    TestVM_ID = "b2f57910-0543-491e-92d7-ab00a47448de"

    def testCase2903(self):
        newvm = self.connection.getVM(self.TestVM_ID)
        target = VirtualMachine(self.connection)
        target.imageGUID = newvm.imageGUID

        # should be removed
        target.SecurityGroupGUID = newvm.SecurityGroupGUID
        target.autoProvision = newvm.autoProvision

        target.imageName = testlib.RandomString(36)
        updated = target.update()
        self.assertEqual(updated.imageName, target.imageName)

    def testCase2904(self):
        newvm = self.connection.getVM(self.TestVM_ID)
        target = VirtualMachine(self.connection)
        target.imageGUID = newvm.imageGUID

        # should be removed
        target.SecurityGroupGUID = newvm.SecurityGroupGUID
        target.autoProvision = newvm.autoProvision

        target.imageDescription = testlib.RandomString(361)
        updated = target.update()
        self.assertEqual(updated, None)

    def testCase2918(self):
        vm  = self.connection.getVM('8dbf182f-0a1a-43b5-93ae-b4354252059c')
        devicelist = []
        devicelist.append(self.RAID_Device1)
        devicelist.append(self.RAID_Device2)
        deviceID = str(uuid.uuid4())

        # create raid device object
        dev = Device(self.connection)
        dev.name = testlib.RandomString(1025)
        dev.msUID = deviceID
        dev.raidLevel = 'RAID0'
        dev.fileSystem = self.filesystem
        dev.volume = Volume(self.connection)
        dev.volume.mountPoint = self.mountpoint

        for d in devicelist:
            new = Device(self.connection)
            new.msUID = d
            dev.subDevices.append(new)

        # call create RAID API
        ret = self.connection.get_status( 'vm/%s/device/raid/' % (vm.imageGUID), 
                                          Device, data=dev.tostring(), method='POST')
        self.assertEqual(ret, 204)

        ret = vm.deleteDevice(deviceID)
        self.assertEqual(ret, 204)

    def testCase2919(self):
        vm  = self.connection.getVM('8dbf182f-0a1a-43b5-93ae-b4354252059c')
        devicelist = []
        devicelist.append(self.RAID_Device1)
        devicelist.append(self.RAID_Device2)
        deviceID = str(uuid.uuid4())

        # create raid device object
        dev = Device(self.connection)
        dev.name = 'testCase2919'
        dev.description = testlib.RandomString(1025)
        dev.msUID = deviceID
        dev.raidLevel = 'RAID0'
        dev.fileSystem = self.filesystem
        dev.volume = Volume(self.connection)
        dev.volume.mountPoint = self.mountpoint

        for d in devicelist:
            new = Device(self.connection)
            new.msUID = d
            dev.subDevices.append(new)

        # call create RAID API
        ret = self.connection.get_status( 'vm/%s/device/raid/' % (vm.imageGUID), 
                                          Device, data=dev.tostring(), method='POST')
        self.assertEqual(ret, None)

    def testCase2921(self):
        vm  = self.connection.getVM('8dbf182f-0a1a-43b5-93ae-b4354252059c')
        devicelist = []
        devicelist.append(self.RAID_Device1)
        devicelist.append(self.RAID_Device2)
        deviceID = str(uuid.uuid4())

        # create raid device object
        dev = Device(self.connection)
        dev.name = 'testCase2921'
        dev.msUID = deviceID
        dev.raidLevel = 'RAID0'
        dev.fileSystem = self.filesystem
        dev.volume = Volume(self.connection)
        dev.volume.mountPoint = testlib.RandomString(256)

        for d in devicelist:
            new = Device(self.connection)
            new.msUID = d
            dev.subDevices.append(new)

        # call create RAID API
        ret = self.connection.get_status( 'vm/%s/device/raid/' % (vm.imageGUID), 
                                          Device, data=dev.tostring(), method='POST')
        self.assertEqual(ret, None)

    def testCase2922(self):
        vm  = self.connection.getVM('8dbf182f-0a1a-43b5-93ae-b4354252059c')
        devicelist = []
        devicelist.append(self.RAID_Device1)
        devicelist.append(self.RAID_Device2)
        deviceID = str(uuid.uuid4())

        # create raid device object
        dev = Device(self.connection)
        dev.name = 'testCase2921'
        dev.msUID = deviceID
        dev.raidLevel = 'RAID0'
        dev.fileSystem = self.filesystem
        dev.volume = Volume(self.connection)
        dev.volume.mountPoint = testlib.RandomString(256)

        for d in devicelist:
            new = Device(self.connection)
            new.msUID = d
            dev.subDevices.append(new)

        # call create RAID API
        ret = self.connection.get_status( 'vm/%s/device/raid/' % (vm.imageGUID), 
                                          Device, data=dev.tostring(), method='POST')
        self.assertEqual(ret, None)

    def testCase2928(self):
        vm  = self.connection.getVM('8dbf182f-0a1a-43b5-93ae-b4354252059c')
        devicelist = []
        devicelist.append(self.RAID_Device1)
        devicelist.append(self.RAID_Device2)
        deviceID = str(uuid.uuid4())

        # create raid device object
        dev = Device(self.connection)
        dev.name = testlib.RandomString(3000)
        dev.msUID = deviceID
        dev.raidLevel = 'RAID0'
        dev.fileSystem = self.filesystem
        dev.volume = Volume(self.connection)
        dev.volume.mountPoint = self.mountpoint

        for d in devicelist:
            new = Device(self.connection)
            new.msUID = d
            dev.subDevices.append(new)

        # call create RAID API
        ret = self.connection.get_status( 'vm/%s/device/raid/' % (vm.imageGUID), 
                                          Device, data=dev.tostring(), method='POST')
        self.assertEqual(ret, None)


    def testCase2940(self):
        policy = SecurityGroup(self)
        policy.name = "testCase2940"
        # default values
        vm = VirtualMachine(self)
        vm.imageGUID = '245e35df-492a-40c8-8543-b07e1e252744'
        policy.addVM(vm)

        data = policy.tostring()
        policy = self.connection.get_object( '%s/' % (self.connection.REST_SECURITY_GROUP), 
                                             SecurityGroup, data=data, method='POST')

        # create policy
        self.assertEqual(policy, None)

    def testCase2942(self):
        policyName="testCase294229422942294229422942="

        # create policy
        policy = self.connection.createSecurityGroup(policyName)
        self.assertEqual(policy, None)

    def testCase2943(self):
        policy = SecurityGroup(self)
        policy.name = "testCase2943"
        # default values
        policy.description = testlib.RandomString(361)

        data = policy.tostring()
        policy = self.connection.get_object( '%s/' % (self.connection.REST_SECURITY_GROUP), 
                                             SecurityGroup, data=data, method='POST')
        # create policy
        self.assertEqual(policy, None)

    def testCase2944(self):
        policy = SecurityGroup(self)
        policy.name = "testCase2944"
        # default values
        policy.description = ''.join(random.choice("~!@#$%^&*()_+=-`][}{;?><,./)") for x in range(361))

        data = policy.tostring()
        policy = self.connection.get_object( '%s/' % (self.connection.REST_SECURITY_GROUP), 
                                             SecurityGroup, data=data, method='POST')
        # create policy
        self.assertEqual(policy, None)


if __name__ == '__main__':
    unittest.main()