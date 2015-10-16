#!/usr/bin/env python

"""
Description: This script is to initialize the L3/HA scale test deployment
Developer: gopal@onecloudinc.com
"""

from neutronclient.v2_0 import client
from credentials import get_credentials
from config import NETWORK_NAME_PREFFIX, NETWORK_COUNT, EXTERNAL_NETWORK, \
    print_scale_test_config
from networks import create_network

credentials = get_credentials()
neutron = client.Client(**credentials)


def main():
    """
    This method will initialize the scale test deployment based on the global \
    config parameters mentioned on config.py file
    """

    print "\n\n"
    print_scale_test_config()
    print "\n\n"
    print "Starting Scale Test Deployment"
    router_detail = neutron.create_router({'router': {
        'name': NETWORK_NAME_PREFFIX+'_router'}})
    router = router_detail['router']
    neutron.add_gateway_router(router['id'], {
        'network_id': neutron.list_networks(
            name=EXTERNAL_NETWORK)['networks'][0]['id']})

    print('   - Created Router %s' % router['name'])
    for i in range(NETWORK_COUNT):
        i += 1
        network_name = NETWORK_NAME_PREFFIX+'_'+str(i)
        network_cidr = str(i)+"."+str(i)+"."+str(i)+".0/24"
        create_network(router['id'], network_name, network_cidr)
    print "="*50
    print "\n\n"
    print "Scale Test Deployment Completed"
    print "\n\n"


if __name__ == '__main__':
    main()
