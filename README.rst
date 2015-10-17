L3/HA Scale Test Deployment Script V1
-------------------------------------
Developer: gopal@onecloudinc.com

Description:
------------
This script will create Networks, Subnets, Router with External Gateway, VMS, Floating IPs based on global configuration parameters specified on the config.py file.


Stepts to run the scale test deployment:
========================================

Step :: 1
---------

==> Add the Keystone Credentials in 'openrc' file.

export OS_USERNAME=admin
export OS_TENANT_NAME=admin
export OS_PASSWORD=admin123
export OS_AUTH_URL=http://10.1.25.134/v2.0/


Step :: 2
---------

==> Define the Scale Test Configuration for the global parameters in 'config.py' file.

NETWORK_NAME_PREFFIX = 'TEST'
NETWORK_COUNT = 2
VM_COUNT = 2
EXTERNAL_NETWORK = 'public'
FLOATING_IP_POOL = 'public'


Step :: 3
---------

==> Load the Environment variables into your current shell with the Bash source built-in command.

[onecloud@localhost ]$ source openrc 


Step :: 4
---------

==> Intialize the scale test deployment by running the 'initialize_deploy.py' python script.

[onecloud@localhost ]$ python initialize_deploy.py

This script will create Networks, Subnets, Router with External Gateway, VMS, Floating IPs based on global configuration parameters specified for a single tenant.

.. image:: https://raw.githubusercontent.com/gopal1cloud/L3_ASR_scale_test/l3_asr_develop/Scale_Test_Deployment_Per_Tenant_Screenshot.png
    :alt: Topology
    :width: 679
    :height:781
    :align: center

Step :: 5
---------

==> Destroy the scale test deployment by running the 'destroy_deploy.py' python script.

[onecloud@localhost ]$ python destroy_deploy.py

This script will delete Networks, Subnets, Router with External Gateway, VMS, Floating IPs based on global configuration parameters specified for a single tenant.

Thats It.


I have given the same console output in a text file named 'Sample_Scale_Test_Deployment_Console_Output.txt', 'Sample_Destroy_Scale_Test_Deployment_Console_Output.txt' and
sample openstack network topology named 'Scale_Test_Deployment_Per_Tenant_Screenshot.png' in the script folder for reference.

Thanks!!!
