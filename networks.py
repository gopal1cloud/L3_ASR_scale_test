#!/usr/bin/env python
"""
Description: This script is to create network, subnets, router with \
             external gateway mapping.
Developer: gopal@onecloudinc.com
"""

import os
from neutronclient.v2_0 import client
from credentials import get_credentials
from config import NETWORK_NAME_PREFFIX, NETWORK_COUNT, VM_COUNT, \
    OS_TENANT_NAME
from vm_instances import launch_vm_on_network, terminate_vm_on_network
from floating_ips import release_all_floating_ips

credentials = get_credentials()
neutron = client.Client(**credentials)


def create_network(router, network_name, network_cidr):
    """
    This method is used to create network, subnets, interfaces on router with \
    external gateway mapping for the given network name and CIDR.
    """

    try:
        print "\n"
        print "=" * 50
        print "   Initiated Network Creation for " + network_name
        print "=" * 50
        print "\n"

        body_sample = {'network': {'name': network_name,
                                   'admin_state_up': True}}
        try:
            net = neutron.create_network(body=body_sample)
            net_dict = net['network']
            network_id = net_dict['id']
            network_vlan = net_dict['provider:segmentation_id']
            print('   - Network %s created' % net_dict['name'])
            net_status = True
        except Exception:
            net_dict = {}
            net_status = False

        subnet_name = network_name + "_subnet"
        try:
            body_create_subnet = {'subnets': [{'name': network_name + "_subnet",
                                               'cidr': network_cidr,
                                               'ip_version': 4,
                                               'network_id': network_id}]}
            subnet_detail = neutron.create_subnet(body=body_create_subnet)
            subnet = subnet_detail['subnets'][0]
            print('   - Created subnet %s' % subnet['name'])
            net_status = True
        except Exception:
            subnet = {}
            net_status = False

        neutron.add_interface_router(router['id'], {'subnet_id': subnet['id']})
        print('   - Created interface between %s' % subnet['name'])

    finally:
        print "\n"
        msg = "<== Completed Network Creation with External Gateway "
        msg += "Successfully ==>"
        print msg
    print "\n"
    print "=" * 50
    print "   Initiated VM Deployment " + network_name
    print "=" * 50
    print "\n"

    ins_data = []
    for i in range(1, VM_COUNT + 1):
        vm_name = net_dict['name'] + '_VM_' + str(i)
        ins_data.append(launch_vm_on_network(vm_name, network_id))

    print "\n"
    msg = "<== Completed VM Launch on Network with Floating IP Allocation "
    msg += "Successfully ==>"
    print msg

    result = {'network_data': {'tenant_name': OS_TENANT_NAME,
                               'network_name': network_name,
                               'network_cidr': network_cidr,
                               'subnet_name': subnet_name,
                               'network_id': network_id,
                               'network_vlan_id': network_vlan,
                               'status': net_status},
              'instance_data': ins_data}
    return result


def delete_network():
    """
    This method is used to delete vms, network, subnets, interfaces on router \
    with external gateway mapping for the given network name and CIDR.
    """
    network_list = []
    router_list = []
    router_list.append(NETWORK_NAME_PREFFIX + '_router')
    for i in range(NETWORK_COUNT):
        i += 1
        network_list.append(NETWORK_NAME_PREFFIX + '_' + str(i))
    for network_name in network_list:
        print "\n"
        print "=" * 50
        print "   Terminating VM launched on " + network_name
        print "=" * 50
        print "\n"
        for i in range(1, VM_COUNT + 1):
            vm_name = network_name + '_VM_' + str(i)
            terminate_vm_on_network(vm_name, network_name)
        print "\n"
        print("<== Completed VM Termination on Network ==>")
    networks = neutron.list_networks()['networks']
    routers = neutron.list_routers()['routers']
    print "\n"
    print "=" * 50
    print "   Initiated Network Deletion "
    print "=" * 50
    print "\n"
    for router in routers:
        if router['name'] in router_list:
            tenant_id = router['tenant_id']
            for network in networks:
                if network['name'] in network_list:
                    subnets = neutron.list_subnets(
                        network_id=network['id'])['subnets']
                    for subnet in subnets:
                        ports = neutron.list_ports(
                            subnet_id=subnet['id'],
                            tenant_id=tenant_id)['ports']
                        for port in ports:
                            try:
                                neutron.delete_port(port['id'])
                            except:
                                pass
                            try:
                                neutron.remove_interface_router(
                                    router['id'], {'subnet_id': subnet['id']})
                            except:
                                pass

                        neutron.delete_subnet(subnet['id'])
                    neutron.delete_network(network['id'])
                    print "   Deleted " + network['name']
            print "\n"
            neutron.remove_gateway_router(router['id'])
            try:
                neutron.delete_router(router['id'])
            except:
                pass
            print "   Deleted " + router['name']
    print "\n"
    msg = "<== Completed Network, Router Deletion from External Gateway "
    msg += "Successfully ==>"
    print msg
    release_all_floating_ips()
    print "\n"
    print("<== Released all Floating IPs Successfully ==>")
    return True
