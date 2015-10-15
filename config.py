"""
Description: Define the Scale Test Configuration with the below global parameters.
Developer: gopal@onecloudinc.com
"""

NETWORK_NAME_PREFFIX = 'TEST'
NETWORK_COUNT = 2
VM_COUNT = 2
EXTERNAL_NETWORK = 'public'
FLOATING_IP_POOL = 'public'





"""
Test Configuration Ends Here with the global parameters.
"""

def print_scale_test_config():
    """
    This method is used to print the current test configuration on scale test \
    deployment initialization.
    """
    print '='*50
    print "    Configuration for this Scale Test"
    print '='*50

    print " Network will be created with prefix                        : "+NETWORK_NAME_PREFFIX
    print " No of Networks                                             : "+str(NETWORK_COUNT)
    print " No of VMs per Network                                      : "+str(VM_COUNT)
    print " Name of the External Network with be connected with Router : "+EXTERNAL_NETWORK
    print " Name of the Floating IP Pool will be used for Allocation   : "+FLOATING_IP_POOL
    print '='*50
