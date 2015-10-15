#!/usr/bin/env python
"""
Description: This script is to allocate & associate the floating IP.
Developer: gopal@onecloudinc.com
"""



import os
import time
import novaclient.v1_1.client as nvclient
from credentials import get_credentials, get_nova_credentials
from config import *

credentials = get_nova_credentials()
nova = nvclient.Client(**credentials)
if not nova.keypairs.findall(name="admin"):
    with open(os.path.expanduser('~/.ssh/id_rsa.pub')) as fpubkey:
        nova.keypairs.create(name="admin", public_key=fpubkey.read())

def add_floating_ip_for_vm(instance):
    """
    This method is used to allocate & associate floating IP to the given VM\
    based on the availability from the defined pool.
    """

    floating_ip = nova.floating_ips.create(FLOATING_IP_POOL)
    instance.add_floating_ip(floating_ip)
    print "   - Assigned Floating IP: "+str(floating_ip.ip)
    return True
