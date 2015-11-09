"""
Description: Define the Scale Test Configuration with the below global \
             parameters.
Developer: gopal@onecloudinc.com
"""

OS_USERNAME = 'admin'
OS_TENANT_NAME = 'scaletest1'
OS_PASSWORD = 'admin123'
OS_AUTH_URL = 'http://10.1.25.136:5000/v2.0/'
NETWORK_NAME_PREFFIX = OS_TENANT_NAME
NETWORK_COUNT = 2
VM_COUNT = 1
EXTERNAL_NETWORK = 'public'
FLOATING_IP_POOL = 'public'

ENABLE_ASR_VERIFICATION = True
DEPLOYMENT_ID = 'ans136'
ASR_HOST = '10.10.10.10'
ASR_USER = 'admin'
ASR_PASSWORD = 'admin'


"""
Test Configuration Ends Here with the global parameters.
"""


def print_scale_test_config():
    """
    This method is used to print the current test configuration on scale test \
    deployment initialization.
    """
    print '=' * 70
    print "    Configuration for this Scale Test"
    print '=' * 70

    print " Network will be created with prefix                        : " \
        + NETWORK_NAME_PREFFIX
    print " No of Networks                                             : " \
        + str(NETWORK_COUNT)
    print " No of VMs per Network                                      : " \
        + str(VM_COUNT)
    print " Name of the External Network with be connected with Router : " \
        + EXTERNAL_NETWORK
    print " Name of the Floating IP Pool will be used for Allocation   : " \
        + FLOATING_IP_POOL
    print '=' * 70
