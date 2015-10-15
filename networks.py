#!/usr/bin/env python
"""
Description: This script is to create network, subnets, router with \
             external gateway mapping.
Developer: gopal@onecloudinc.com
"""

from neutronclient.v2_0 import client
from credentials import get_credentials
from config import *
from vm_instances import launch_vm_on_network

credentials = get_credentials()
neutron = client.Client(**credentials)

def create_network(network_name,network_cidr):
    """
    This method is used to create network, subnets, router with \
    external gateway mapping for the given network name and CIDR.
    """

    try:
        print "\n\n"
        print "="*50
        print "   Initiated Network Creation for "+network_name
        print "="*50
        print "\n\n"

        body_sample = {'network': {'name': network_name,'admin_state_up': True}}
        netw = neutron.create_network(body=body_sample)
        net_dict = netw['network']
        network_id = net_dict['id']
        print('   - Network %s created' % net_dict['name'])
        body_create_subnet = {'subnets': [{'name':network_name+"_subnet",'cidr': network_cidr,'ip_version': 4, 'network_id': network_id}]}
        subnet_detail = neutron.create_subnet(body=body_create_subnet)
        subnet = subnet_detail['subnets'][0] 
        print('   - Created subnet %s' % subnet['name'])
        
        router_detail = neutron.create_router( { 'router' : { 'name' : network_name+'_router' } } )
        router = router_detail['router']
        neutron.add_interface_router(router['id'], { 'subnet_id' : subnet['id'] } )
        # neutron.add_gateway_router(router['id'], { 'network_id' : neutron.list_networks(name = EXTERNAL_NETWORK)['networks'][0]['id'] } )

        print('   - Created Router %s' % router['name'])

    finally:
        print "\n\n"
        print("<== Completed Network Creation with External Gateway Successfully ==>")
    
    print "\n\n"
    print "="*50
    print "   Initiated VM Deployment "+network_name
    print "="*50
    print "\n\n"

    for i in range(1,VM_COUNT+1):
        vm_name = net_dict['name']+'_VM_'+str(i)
        launch_vm_on_network(vm_name,network_id)
    print "\n\n"
    print("<== Completed VM Launch on Network with Floating IP Allocation Successfully ==>")
    return True


