#!/usr/bin/env python

"""
Description: This script is to destory the L3/HA scale test deployment
Developer: gopal@onecloudinc.com
"""

from neutronclient.v2_0 import client
from credentials import get_credentials
from config import *
from networks import delete_network

credentials = get_credentials()
neutron = client.Client(**credentials)


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

    delete_network()

    print "=" * 50
    print "\n"
    print "Scale Test Deployment Completed"
    print "\n"


if __name__ == '__main__':
    main()
