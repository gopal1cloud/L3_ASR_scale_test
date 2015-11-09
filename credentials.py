"""
Description: This script is to map the environment variables to credentials \
             dict based on the client service API
Developer: gopal@onecloudinc.com
"""

import os
from config import OS_USERNAME, OS_TENANT_NAME, OS_PASSWORD, OS_AUTH_URL


def get_credentials():
    """
    This method is used for authorization with keystone clients
    """

    d = {}
    d['username'] = OS_USERNAME
    d['password'] = OS_PASSWORD
    d['auth_url'] = OS_AUTH_URL
    d['tenant_name'] = OS_TENANT_NAME
    return d


def get_nova_credentials():
    """
    This method is used for authorization with nova clients
    """

    d = {}
    d['username'] = OS_USERNAME
    d['api_key'] = OS_PASSWORD
    d['auth_url'] = OS_AUTH_URL
    d['project_id'] = OS_TENANT_NAME
    return d
