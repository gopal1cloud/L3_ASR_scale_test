#!/usr/bin/env python

"""
Description: This script is to initialize the L3/HA scale test deployment
Developer: gopal@onecloudinc.com
"""

from neutronclient.v2_0 import client
from credentials import get_credentials
from config import OS_TENANT_NAME, NETWORK_NAME_PREFFIX, NETWORK_COUNT, \
    EXTERNAL_NETWORK, print_scale_test_config, DEPLOYMENT_ID, \
    ASR_HOST, ASR_USER, ASR_PASSWORD
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
                    'Subnet Name', 'Status'])
    y.align["Tenant_Name"] = "l"   # Left align source tenant values
    y.padding_width = 1
    for entry in test_data:
        y.add_row([entry['network_data']['tenant_name'],
                  entry['network_data']['network_name'],
                  entry['network_data']['network_cidr'],
                  entry['network_data']['subnet_name'],
                  entry['network_data']['status']])
    return y


def print_instance_info(test_data):
    z = PrettyTable(['Tenant Name', 'Instance Name', 'Status'])
    z.align["Tenant Name"] = "l"   # Left align source tenant values
    z.padding_width = 1
    for data in test_data:
        z.add_row([data['network_data']['tenant_name'],
                  data['instance_data']['instance_name'],
                  data['instance_data']['status']])
    return z


def asr_router_vrf_info(router_name, router_data):
    x = PrettyTable(['Tenant Name', 'Router Name', 'Router VRF Name',
                    'Interfaces', 'Status'])
    x.align["Tenant Name"] = "l"   # Left align source tenant values
    x.padding_width = 2
    x.add_row([OS_TENANT_NAME, router_name, router_data['vrfname'], ', '.join(router_data['interfaces']), router_data['status']])
    return x


def asr_network_vrf_info(router_name, interface_data):
    y = PrettyTable(['Tenant Name', 'Router Name', 'Interface VRF Name',
                    'Interface VRF Description',
                    'Internet Address', 'Vlan ID', 'Interfaces Status', 'Status'])
    y.align["Tenant Name"] = "l"   # Left align source tenant values
    y.padding_width = 2
    for entry in interface_data:
        y.add_row([OS_TENANT_NAME, router_name, entry['interface_name'],
                  entry['description'], entry['ip_address'],
                  entry['vlan_id'], entry['interface_status'], entry['status']])
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
    vrfname = "nrouter"+'-'+vrf_router_id+'-'+DEPLOYMENT_ID

    asr_verify_cmd = GetASRCmd(asr_host=ASR_HOST,
                                     asr_host_port=22,
                                     asr_user=ASR_USER,
                                     asr_password=ASR_PASSWORD,
                                     asr_slots=["0"])

    router_data = asr_verify_cmd.get_router_detail(vrfname)
    interface_data = []
    for interface in router_data['interfaces']:
        interface_data.append(asr_verify_cmd.get_network_interface_detail(vrfname, interface))

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

    print "           OpenStack-ASR Router VRF Verification Results               "
    print asr_router_vrf_info(router_name, router_data)
    print "\n"

    print "           OpenStack-ASR Network VRF Verification Results              "
    print asr_network_vrf_info(router_name, interface_data)
    print "\n"


if __name__ == '__main__':
    main()
