#!/usr/bin/env python

"""
Description: This script is to destory the L3/HA scale test deployment
Developer: gopal@onecloudinc.com
"""

import os
from neutronclient.v2_0 import client
from credentials import get_credentials
from config import TENANT_BASE_INDEX, TENANT_COUNT, TENANT_NAME_PREFIX, \
    print_scale_test_config
from networks import delete_network
from tenants import delete_tenant
from datetime import datetime, timedelta
from pytz import timezone

credentials = get_credentials()
neutron = client.Client(**credentials)
fmt = "%Y-%m-%d %H:%M:%S %Z%z"


def main():
    """
    This method will destory the scale test deployment based on the global \
    config parameters mentioned on config.py file and creates the router with \
    external gateway connectivity to public network.
    """

    print "\n"
    print_scale_test_config()
    print "\n"
    print "Destroying Scale Test Deployment"
    index = TENANT_BASE_INDEX
    for i in range(1, TENANT_COUNT + 1):
        tenant_name = TENANT_NAME_PREFIX + '-' + str(index)
        index += 1
        delete_network(tenant_name)
        start_time = datetime.now(timezone('US/Pacific'))
        delete_tenant(tenant_name)
        end_time = datetime.now(timezone('US/Pacific'))
        print "\n"
        print "-"*65
        print ("    Tenant & User Deletion Time Summary :")
        print "-"*65
        print "\n"
        print('   - Test Started Time   :\t %s' % (start_time.strftime(fmt)))
        print('   - Test Ended Time     :\t %s' % (end_time.strftime(fmt)))

    print "=" * 50
    print "\n"
    print "Cleaned Scale Test Deployment"
    print "\n"


if __name__ == '__main__':
    main_start_time = datetime.now(timezone('US/Pacific'))
    main()
    main_end_time = datetime.now(timezone('US/Pacific'))
    print "-"*65
    print ("    Scale Test Deployment Consolidated Time Summary :")
    print "-"*65
    print "\n"
    print('   - Test Started Time   :\t %s' % (main_start_time.strftime(fmt)))
    print('   - Test Ended Time     :\t %s' % (main_end_time.strftime(fmt)))
    print "\n"
