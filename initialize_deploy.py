#!/usr/bin/env python

"""
Description: This script is to initialize the L3/HA scale test deployment
Developer: gopal@onecloudinc.com
"""

import os
from neutronclient.v2_0 import client
from credentials import get_credentials
from config import OS_TENANT_NAME, NETWORK_NAME_PREFFIX, NETWORK_COUNT, \
    EXTERNAL_NETWORK, print_scale_test_config, DEPLOYMENT_ID, \
    ASR_HOST, ASR_USER, ASR_PASSWORD, ENABLE_ASR_VERIFICATION
from networks import create_network
from prettytable import PrettyTable
from asr import GetASRCmd

credentials = get_credentials()
neutron = client.Client(**credentials)


def print_router_info(router_name, status):
    x = PrettyTable(['Tenant Name', 'Router Name', 'Status'])
    x.align["Tenant Name"] = "l"   # Left align source tenant values
    x.padding_width = 1
    x.add_row([OS_TENANT_NAME, router_name, status])
    return x


def print_network_info(test_data):
    y = PrettyTable(['Tenant Name', 'Network Name', 'Network CIDR',
                    'Vlan ID', 'Subnet Name', 'Status'])
    y.align["Tenant_Name"] = "l"   # Left align source tenant values
    y.padding_width = 1
    for entry in test_data:
        y.add_row([entry['network_data']['tenant_name'],
                  entry['network_data']['network_name'],
                  entry['network_data']['network_cidr'],
                  entry['network_data']['network_vlan_id'],
                  entry['network_data']['subnet_name'],
                  entry['network_data']['status']])
    return y


def print_instance_info(test_data):
    z = PrettyTable(['Tenant Name', 'Instance Name', 'Status'])
    z.align["Tenant Name"] = "l"   # Left align source tenant values
    z.padding_width = 1
    for data in test_data:
        for ins in data['instance_data']:
            z.add_row([data['network_data']['tenant_name'],
                      ins['instance_name'],
                      ins['status']])
    return z


def asr_router_vrf_info(router_name, router_data):
    x = PrettyTable(['Tenant Name', 'Router Name', 'Router VRF Name',
                    'Interfaces', 'Status'])
    x.align["Tenant Name"] = "l"   # Left align source tenant values
    x.padding_width = 2
    x.add_row([OS_TENANT_NAME, router_name, router_data['vrfname'],
              ', '.join(router_data['interfaces']), router_data['status']])
    return x


def asr_ipnat_pool_info(router_name, ipnatpool_data):
    x = PrettyTable(['Tenant Name', 'Router Name', 'Router VRF Name',
                     'NAT Pool Name', 'Start IP', 'End IP', 'Netmask',
                     'Status'])
    x.align["Tenant Name"] = "l"   # Left align source tenant values
    x.padding_width = 2
    x.add_row([OS_TENANT_NAME, router_name, ipnatpool_data['vrfname'],
              ipnatpool_data['nat_pool_name'], ipnatpool_data['start_ip'],
              ipnatpool_data['end_ip'], ipnatpool_data['netmask'],
              ipnatpool_data['status']])
    return x


def asr_iproute_info(router_name, iproute_data):
    x = PrettyTable(['Tenant Name', 'Router Name', 'Router VRF Name',
                     'Prefix', 'Mask', 'Interface', 'Next Hop Address',
                     'Status'])
    x.align["Tenant Name"] = "l"   # Left align source tenant values
    x.padding_width = 2
    x.add_row([OS_TENANT_NAME, router_name, iproute_data['vrfname'],
              iproute_data['prefix'], iproute_data['mask'],
              iproute_data['interface'],
              iproute_data['next_hop_address'], iproute_data['status']])
    return x


def asr_network_vrf_info(router_name, network_vlan, interface_data):
    y = PrettyTable(['Tenant Name', 'Router Name', 'Network Name',
                     'Interface VRF Name', 'Internet Address',
                     'Vlan ID', 'Interfaces Status', 'Status'])
    y.align["Tenant Name"] = "l"   # Left align source tenant values
    y.padding_width = 2
    for entry in interface_data:
        y.add_row([OS_TENANT_NAME, router_name, network_vlan[entry['vlan_id']],
                  entry['interface_name'], entry['ip_address'],
                  entry['vlan_id'], entry['interface_status'],
                  entry['status']])
    return y


def asr_interface_nat_info(router_name, network_vlan, interface_data):
    y = PrettyTable(['Tenant Name', 'Router Name', 'Network Name',
                     'Interface Vlan ID', 'Dynamic NAT Entry',
                     'Access-list Entry', 'Status'])
    y.align["Tenant Name"] = "l"   # Left align source tenant values
    y.padding_width = 2
    for entry in interface_data:
        y.add_row([OS_TENANT_NAME, router_name, network_vlan[entry['vlan_id']],
                  entry['vlan_id'], entry['nat_entry'],
                  entry['access_list_entry'], entry['status']])
    return y


def main():
    """
    This method will initialize the scale test deployment based on the global \
    config parameters mentioned on config.py file and creates the router with \
    external gateway connectivity to public network.
    """

    print "\n"
    print_scale_test_config()
    print "\n"
    print "Starting Scale Test Deployment"
    router_name = NETWORK_NAME_PREFFIX + '_router'
    try:
        router_detail = neutron.create_router({'router': {
            'name': NETWORK_NAME_PREFFIX + '_router'}})
        router = router_detail['router']
        status = True
    except Exception:
        router = {}
        status = False

    neutron.add_gateway_router(router['id'],
                               {'network_id': neutron.list_networks(
                                   name=EXTERNAL_NETWORK)['networks'][0]
                                   ['id']})
    router_id = router['id']
    print('   - Created Router %s' % router['name'])

    test_data = []
    for i in range(NETWORK_COUNT):
        i += 1
        network_name = NETWORK_NAME_PREFFIX + '_' + str(i)
        network_cidr = str(i) + "." + str(i) + "." + str(i) + ".0/24"
        test_data.append(create_network(router, network_name, network_cidr))

    network_vlan = {}
    for entry in test_data:
        network_vlan[str(entry['network_data']['network_vlan_id'])] = \
            entry['network_data']['network_name']

    if ENABLE_ASR_VERIFICATION:
        vrf_router_id = router_id[:6]
        vrfname = "nrouter" + '-' + vrf_router_id + '-' + DEPLOYMENT_ID

        asr_verify_cmd = GetASRCmd(asr_host=ASR_HOST,
                                   asr_host_port=22,
                                   asr_user=ASR_USER,
                                   asr_password=ASR_PASSWORD,
                                   asr_slots=["0"])
        router_data = {'vrfname': vrfname, 'interfaces': '',
                       'status': ''}
        ipnatpool_data = {'vrfname': vrfname, 'nat_pool_name': '',
                          'start_ip': '', 'end_ip': '',
                          'netmask': '', 'status': ''}
        iproute_data = {'vrfname': vrfname, 'prefix': '', 'mask': '',
                        'interface': '', 'next_hop_address': '', 'status': ''}
        interface_data = []
        nat_data = []
        try:
            router_data = asr_verify_cmd.get_router_detail(vrfname)
            ipnatpool_data = asr_verify_cmd.get_ipnat_pool_detail(vrfname)
            iproute_data = asr_verify_cmd.get_iproute_detail(vrfname)
            for interface in router_detail['interfaces']:
                interface_data.append(
                    asr_verify_cmd.get_network_interface_detail(vrfname,
                                                                interface))
            for interface in interface_data:
                interfaceid = DEPLOYMENT_ID + '_' + interface['vlan_id']
                nat_data.append(
                    asr_verify_cmd.get_interface_nat_access_detail
                    (interface['vlan_id'], interfaceid))
            asr_report = True
        except Exception as exc:
            print "\n"
            print "[ERROR] Caught exception on ASR Verification : %s" % \
                (exc.message)
            print "\n"
            asr_report = False

    print "=" * 50
    print "\n"
    print "Scale Test Deployment Completed"
    print "\n"

    print "*" * 80
    print "Scale Test Deployment OpenStack Report"
    print "*" * 80

    print "\n"
    print "           Router Creation Results      "
    print print_router_info(router_name, status)
    print "\n"

    print "                 Network Creation Results      "
    print print_network_info(test_data)
    print "\n"

    print "            Instance Creation Results      "
    print print_instance_info(test_data)
    print "\n"

    if ENABLE_ASR_VERIFICATION and asr_report:
        print "           OpenStack-ASR Router VRF Verification Results   "
        print asr_router_vrf_info(router_name, router_data)
        print "\n"

        print "           OpenStack-ASR IP NAT Pool Verification Results  "
        print asr_ipnat_pool_info(router_name, ipnatpool_data)
        print "\n"

        print "           OpenStack-ASR IP Route Verification Results     "
        print asr_iproute_info(router_name, iproute_data)
        print "\n"

        print "           OpenStack-ASR Network VRF Verification Results  "
        print asr_network_vrf_info(router_name, network_vlan, interface_data)
        print "\n"

        print "           OpenStack-ASR Network Interface's Dynamic NAT \
            & Access list Entry Verification Results              "
        print asr_interface_nat_info(router_name, network_vlan, nat_data)
        print "\n"


if __name__ == '__main__':
    main()
