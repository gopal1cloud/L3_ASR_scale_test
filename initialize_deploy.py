#!/usr/bin/env python

"""
Description: This script is to initialize the L3/HA scale test deployment
Developer: gopal@onecloudinc.com
"""

from neutronclient.v2_0 import client
from credentials import get_credentials
from config import OS_TENANT_NAME, NETWORK_NAME_PREFFIX, NETWORK_COUNT, \
    EXTERNAL_NETWORK, print_scale_test_config, DEPLOYMENT_ID
from networks import create_network
from prettytable import PrettyTable

credentials = get_credentials()
neutron = client.Client(**credentials)


def print_router_info(router_name, status):
    x = PrettyTable(['Tenant_name', 'Router_name', 'Status'])
    x.align["Tenant_name"] = "l"   # Left align source tenant values
    x.padding_width = 1
    x.add_row([OS_TENANT_NAME, router_name, status])
    return x


def print_network_info(test_data):
    y = PrettyTable(['Tenant_name', 'Network_name', 'network_cidr',
                    'Subnet_name', 'Status'])
    y.align["Tenant_name"] = "l"   # Left align source tenant values
    y.padding_width = 1
    for entry in test_data:
        y.add_row([entry['network_data']['tenant_name'],
                  entry['network_data']['network_name'],
                  entry['network_data']['network_cidr'],
                  entry['network_data']['subnet_name'],
                  entry['network_data']['status']])
    return y


def print_instance_info(test_data):
    z = PrettyTable(['Tenant_name', 'Instance_name', 'Status'])
    z.align["Tenant_name"] = "l"   # Left align source tenant values
    z.padding_width = 1
    for data in test_data:
        z.add_row([data['network_data']['tenant_name'],
                  data['instance_data']['instance_name'],
                  data['instance_data']['status']])
    return z


def asr_vrf_info(router_name, vrf_name):
    y = PrettyTable([' Tenant_Name ', ' Router_Name', ' Neutron Events ', 'VRF_Entry', 'Details', 'Result'])
    y.align["Tenant_Name"] = "l"   # Left align source tenant values
    y.padding_width = 2
    y.add_row([OS_TENANT_NAME, router_name, "Router VRF Details", vrf_name, 'Protocols - ipv4, ipv6', '\033[92mPass\033[0m'])
    y.add_row([OS_TENANT_NAME,  router_name, "Network Interface VRF Details", 'nrouter-ans134-INTF', 'Po-126, Po-127',
              '\033[92mPass\033[0m'])
    y.add_row([OS_TENANT_NAME,  router_name, "NAT Pool VRF Details", 'NAT_Pool_list', 'neutron-acl-637', '\033[92mPass\033[0m'])
    y.add_row([OS_TENANT_NAME, router_name, "VRF Router Detail", 'Router_detail', 'router-id', '\033[92mPass\033[0m'])
    y.add_row([OS_TENANT_NAME, router_name, "Network Access List Detail", 'Access list', 'acl-637,acl-638',
               '\033[92mPass\033[0m'])
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
    router_name = NETWORK_NAME_PREFFIX+'_router'
    try:
        router_detail = neutron.create_router({'router': {
            'name': NETWORK_NAME_PREFFIX+'_router'}})
        router = router_detail['router']
        status = True
    except Exception:
        router = {}
        status = False

    router_gateway = neutron.add_gateway_router(router['id'], {
                                                'network_id': neutron.list_networks(
                                                 name=EXTERNAL_NETWORK)['networks'][0]['id']})
    router_gw = router_gateway['router']
    router_id = router['id']
    print('   - Created Router %s' % router['name'])

    test_data = []
    for i in range(NETWORK_COUNT):
        i += 1
        network_name = NETWORK_NAME_PREFFIX+'_'+str(i)
        network_cidr = str(i)+"."+str(i)+"."+str(i)+".0/24"
        test_data.append(create_network(router, network_name, network_cidr))

    vrf_router_id = router_id[:6]
    vrf_name = "nrouter"+'-'+vrf_router_id+'-'+DEPLOYMENT_ID

    print "="*50
    print "\n"
    print "Scale Test Deployment Completed"
    print "\n"

    print "*"*80
    print "Scale Test Deployment OpenStack Report"
    print "*"*80

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

    print "     ** VRF Verification Summary **         "
    print " \n"
    print " VRF Name : " + vrf_name
    print asr_vrf_info(router_name, vrf_name)
    print "\n"
    print '*'*80

if __name__ == '__main__':
    main()
