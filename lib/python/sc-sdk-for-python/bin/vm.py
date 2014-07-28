#!/usr/bin/python
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


import sys
import os
from optparse import OptionParser

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))

import sclib


def printVM(vm):
    print 'VM Name: %s' % (vm.imageName)
    print 'VM ID: %s' % (vm.imageID)
    print 'VM GUID: %s' % (vm.imageGUID)
    print 'Encrypted Devices: %s' % (vm.encryptedDeviceCount)
    print 'Devices:\n'
    for device in vm.devices:
        print '%s\t%s' % (device.name, device.id)
    print ''


def listAllVM():
    vms = conn.listAllVM()

    # list all virtual machines
    print 'Virtual Machines:'
    print '------------------------------------------'
    for vm in vms:
        print "%s" % vm.__dict__
        print vm.securecloudAgent.__dict__
        print vm.provider.__dict__
        print vm.platform
        #printVM(vm)


def listVM(id):
    vm = conn.getVM(id)    
    if vm:
        printVM(vm) 
        
    return vm


def list_vm_by_agent_version(ver):
    vms = conn.listAllVM()
    filtered_result = []
    for vm in vms:
        if vm.securecloudAgent.agentVersion == ver:
            filtered_result.append(vm)
            print ("{image_name:<35} {provider_name:<11} {agent_status:<8} {agent_ver:<10} {last_heartbeat:<15}".format(
                image_name=vm.imageName,
                provider_name=vm.provider.name,
                agent_status=vm.securecloudAgent.agentStatus,
                agent_ver=vm.securecloudAgent.agentVersion,
                last_heartbeat=vm.securecloudAgent.lastHeartbeat))

    return filtered_result


if __name__ == '__main__':

    # commands
    parser = OptionParser(usage="vm [-l] [-i vm_id]")
    parser.add_option("-i", "--vm_id", help="", dest="id", default='', action='store')
    parser.add_option("-l", "--list", help="", dest='list', default=False, action='store_true')
    parser.add_option('-q', '--query', dest='agent_ver', default='', action='store',
                      help='list vm by agent version X.Y.Z.OOOO')

    (options, args) = parser.parse_args()

    conn = sclib.connect_sc(sclib.__config__.get_value('connection', 'MS_HOST'),
                            sclib.__config__.get_value('connection', 'MS_BROKER_NAME'),
                            sclib.__config__.get_value('connection', 'MS_BROKER_PASSPHASE'))
    if conn:
        auth = conn.basicAuth(sclib.__config__.get_value('authentication', 'AUTH_NAME'),
                              sclib.__config__.get_value('authentication', 'AUTH_PASSWORD'))

        if options.id:
            # list information of securityGroup
            policy = listVM(options.id)
    
        # dump all vm from your account
        elif options.list:
            listAllVM()

        elif options.agent_ver:
            vm_list = list_vm_by_agent_version(options.agent_ver)
            print "vm count: %d" % len(vm_list)

        else:
            listAllVM()


