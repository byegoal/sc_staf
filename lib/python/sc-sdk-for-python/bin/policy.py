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
from optparse import OptionParser

import sclib
from sclib.sc.connection import SCConnection
from sclib.sc.securitygroup import SecurityGroup, SecurityGroupAction
from sclib.sc.instance import VirtualMachine

def printPolicy(policy):
    print 'Name\t\t\t: %s' % (policy.name)
    print 'Policy ID\t\t: %s' % (policy.id)
    print 'Integrity Check\t\t: %s' % (policy.EnableIC)
    print 'Number of VM\t\t: %s' % (policy.imageCount)
    if len(policy.vmList):
        print 'VM List\t\t\t:'
        for vm in policy.vmList:
            print '%s\t%s' % (vm.imageGUID, vm.imageID)
    print ''

def listAllSecurityGroup():
    policy_list = conn.listAllSecurityGroup()

    # list all virtual machines
    print 'Policies:'
    print '------------------------------------------'
    for policy in policy_list:
        printPolicy(policy)

def listSecurityGroup(id):
    policy = conn.getSecurityGroup(options.id)    
    if policy:
        printPolicy(policy) 
        
    return policy   

def addVM(policy, vmid):

    # add new vm into a Policy
    if isinstance(policy, SecurityGroup):
        new = VirtualMachine(policy.connection)
        new.imageGUID = vmid
        policy.addVM(new)
        policy.update()
        printPolicy(policy) 

def createPolicy(name):
    policy = conn.createSecurityGroup(name, SecurityGroupAction.Approve, SecurityGroupAction.Deny)
    if policy:
        printPolicy(Policy)

    return policy

if __name__ == '__main__':

    # commands
    parser = OptionParser(usage="policy [-c name] [-i policy_id] [-l] [-a vm_id]")
    parser.add_option("-a", "--add_vm", help="Add a virtual machine to Policy", dest="vm", default=False, action='store')
    parser.add_option("-c", "--create", help="Create new Policy", dest="create", default=None, action='store')
    parser.add_option("-i", "--policy_id", help="", dest="id", default='', action='store')
    parser.add_option("-l", "--list", help="", dest='list', default=False, action='store_true')
    (options, args) = parser.parse_args()


    # begin connection
    conn = sclib.connect_sc( sclib.__config__.get_value('connection', 'MS_HOST'), 
                             sclib.__config__.get_value('connection', 'MS_BROKER_NAME'), 
                             sclib.__config__.get_value('connection', 'MS_BROKER_PASSPHASE'))
    if conn:
        auth = conn.basicAuth( sclib.__config__.get_value('authentication', 'AUTH_NAME'),
                               sclib.__config__.get_value('authentication', 'AUTH_PASSWORD'))

        if options.create:
            policy = createPolicy(options.create)

        if options.id:
            # list information of securityGroup
            policy = listSecurityGroup(options.id)

            # add a vm into securityGroup (aka policy)
            if options.vm:
                addVM(policy, options.vm)

    
        # dump all securityGroup from your account
        elif options.list:
            listAllSecurityGroup()
        else:
            listAllSecurityGroup()
