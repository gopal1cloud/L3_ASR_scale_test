#!/usr/bin/env python
"""
Description: This script is to launching VMs on the network.
Developer: gopal@onecloudinc.com
"""

import os
import time
import novaclient.v1_1.client as nvclient
from novaclient.base import *
from credentials import get_nova_credentials
from floating_ips import add_floating_ip_for_vm

credentials = get_nova_credentials()
nova = nvclient.Client(**credentials)
if not nova.keypairs.findall(name="admin"):
    with open(os.path.expanduser('~/.ssh/id_rsa.pub')) as fpubkey:
        nova.keypairs.create(name="admin", public_key=fpubkey.read())


def launch_vm_on_network(vm_name, network_id):
    """
    This method is to launch VM on the given network & VM Name.
    """

    image = nova.images.find(name="Cirros")
    flavor = nova.flavors.find(name="m1.tiny")

    try:
        instance = nova.servers.create(name=vm_name, image=image,
                                       flavor=flavor,
                                       key_name="admin",
                                       nics=[{'net-id': network_id}])
        ins_dict = instance['name']
        ins_status = True
    except Exception:
        ins_dict = {}
        ins_status = False

    # Poll at 25 second intervals, until the status is no longer 'BUILD'
    print "  * Instance created on network: " + str(vm_name)
    status = instance.status
    while status == 'BUILD':
        time.sleep(25)
        # Retrieve the instance again so the status field updates
        instance = nova.servers.get(instance.id)
        status = instance.status
    print "   - Current status: %s" % status
    add_floating_ip_for_vm(instance)
    ins_data = {'instance_name': vm_name, 'status': status}
    return ins_data


def terminate_vm_on_network(vm_name, network_name):
    """
    This method is to terminate VM on the given network & VM Name.
    """
    try:
        instance = nova.servers.find(name=vm_name)
        nova.servers.delete(instance.id)
        print "  * Instance terminated on network: " + str(vm_name)
    except exceptions.NotFound:
        print "  * Instance Not Found on network: " + str(vm_name)
        pass
    return True
