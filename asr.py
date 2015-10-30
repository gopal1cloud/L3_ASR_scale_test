import logging
import time
from ncclient import manager
import pprint
from lxml import etree as etree
from xml.etree import ElementTree as et

LOG = logging.getLogger("scale_tester")

formatter = \
    logging.Formatter('%(asctime)s - %(module)s - %(funcName)s - (%(lineno)d) %(levelname)s \n %(message)s')

# All inclusive log
fh = logging.FileHandler("scale_tester_ASR.log")
fh.setFormatter(formatter)
LOG.addHandler(fh)
LOG.setLevel(logging.DEBUG)


GET_RUN_CONFIG = """
<filter type="subtree">
    <config-format-text-cmd>
        <text-filter-spec> | inc FFFFFFFFFFFFFFFF</text-filter-spec>
    </config-format-text-cmd>    
    <oper-data-format-text-block>
        <exec>show run</exec>
    </oper-data-format-text-block>
</filter>
"""

GET_ROUTER_INFO = """
<filter type="subtree">
    <config-format-text-cmd>
        <text-filter-spec> | inc FFFFFFFFFFFFFFFF</text-filter-spec>
    </config-format-text-cmd>    
    <oper-data-format-text-block>
        <exec>show vrf detail %s</exec>
    </oper-data-format-text-block>
</filter>
"""

GET_NETWORK_INTERFACE_INFO = """
<filter type="subtree">
    <config-format-text-cmd>
        <text-filter-spec> | inc FFFFFFFFFFFFFFFF</text-filter-spec>
    </config-format-text-cmd>    
    <oper-data-format-text-block>
        <exec>show interfaces %s</exec>
    </oper-data-format-text-block>
</filter>
"""

GET_SHOW_IP_ROUTE_SUMMARY = """
<filter type="subtree">
    <config-format-text-cmd>
        <text-filter-spec> | inc FFFFFFFFFFFFFFFF</text-filter-spec>
    </config-format-text-cmd>    
    <oper-data-format-text-block>
        <exec>show ip route summary</exec>
    </oper-data-format-text-block>
</filter>
"""

GET_SHOW_IP_ACCESS_LIST_COUNT = """
<filter type="subtree">
    <config-format-text-cmd>
        <text-filter-spec> | inc FFFFFFFFFFFFFFFF</text-filter-spec>
    </config-format-text-cmd>    
    <oper-data-format-text-block>
        <exec>show ip access-lists | count neutron_acl</exec>
    </oper-data-format-text-block>
</filter>
"""


 

def asr_connect(host, port, user, password):
    """
    ncclient manager factory method
    """
    return manager.connect(host=host,
                           port=port,
                           username=user,
                           password=password,
                           # device_params={'name': "csr"},
                           timeout=30
                          )

class GetASRCmd():
    """
    This command will fetch and log the CPU and resource health for a specified ASR router 
    """

    def __init__(self, **kwargs):
        """
        constructor
        """

        # obtain connection information for router
        self.asr_host = kwargs['asr_host']
        self.asr_host_port = kwargs['asr_host_port']
        self.asr_user = kwargs['asr_user']
        self.asr_password = kwargs['asr_password']
        
        self.asr_slots = kwargs.get('asr_slots',None)
        
    
    def init(self):
        LOG.debug("init")
        return True
    
    def get_router_detail(self, vrfname):
        """
        Gets the vrf detail from the designated ASR router,
        invokes show vrf detail 
        """
        LOG.debug("get router detail")

        with asr_connect(self.asr_host,
                         port=self.asr_host_port,
                         user=self.asr_user,
                         password=self.asr_password) as conn:
            interfaces = ""
            try:
                filter_str = GET_ROUTER_INFO % (vrfname)
                rpc_obj = conn.get(filter=filter_str)

                LOG.info("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
                LOG.info("ASR Host %s VRF = %s" % \
                          (self.asr_host,rpc_obj.data_xml))
                tree = etree.XML(rpc_obj.data_xml)
                ns = '{urn:ietf:params:xml:ns:netconf:base:1.0}'
                response = tree.find('{0}cli-oper-data-block/{0}item/{0}response'.format(ns)).text
                # print response
                response_data = iter(response.splitlines())
                for line in response_data:
                    if " Interfaces:" in line:
                        interfaces = next(response_data)
                        interfaces = [x for x in interfaces.split(' ') if x]       
                
                LOG.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")
                status = "Pass"

            except Exception as exc:
                LOG.debug("Caught exception %s" % (exc.message))
                status = "Fail"
            router_vrf_data = {}
            router_vrf_data['vrfname'] = vrfname
            router_vrf_data['interfaces'] = interfaces
            router_vrf_data['status'] = status
        return router_vrf_data

    def get_network_interface_detail(self, vrfname, interfacename):
        """
        Gets the vrf detail from the designated ASR router,
        invokes show interfaces detail 
        """
        LOG.debug("get interface detail")

        with asr_connect(self.asr_host,
                         port=self.asr_host_port,
                         user=self.asr_user,
                         password=self.asr_password) as conn:

            interfaces_status = ''
            desc = ''
            ip = ''
            vlanid = ''

            try:
                filter_str = GET_NETWORK_INTERFACE_INFO % (interfacename)
                rpc_obj = conn.get(filter=filter_str)

                LOG.info("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
                LOG.info("ASR Host %s VRF = %s" % \
                          (self.asr_host,rpc_obj.data_xml))
                tree = etree.XML(rpc_obj.data_xml)
                ns = '{urn:ietf:params:xml:ns:netconf:base:1.0}'
                response = tree.find('{0}cli-oper-data-block/{0}item/{0}response'.format(ns)).text
                # print response
                response_data = iter(response.splitlines())
                interfaces_status = response.splitlines()[1]
                for line in response_data:
                    if " Description:" in line:
                        desc = line.split(' Description: ')[1]
                    if " Internet address is" in line:
                        ip = line.split(' Internet address is ')[1]
                    if " Vlan ID" in line:
                        vlanid = line.split(' Vlan ID  ')[1].split('.')[0]

                status = "Pass"
                LOG.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

            except Exception as exc:
                LOG.debug("Caught exception %s" % (exc.message))
                status = "Fail"

            interface_vrf_data = {}
            interface_vrf_data['vrfname'] = vrfname
            interface_vrf_data['interface_name'] = interfacename
            interface_vrf_data['interface_status'] = interfaces_status
            interface_vrf_data['description'] = desc
            interface_vrf_data['ip_address'] = ip
            interface_vrf_data['vlan_id'] = vlanid
            interface_vrf_data['status'] = status
        return interface_vrf_data

    def get_nat_pool_detail(self, vrfname, interfaceid):
        """
        Gets the vrf detail from the designated ASR router,
        invokes show vrf detail 
        """
        LOG.debug("get router detail")

        with asr_connect(self.asr_host,
                         port=self.asr_host_port,
                         user=self.asr_user,
                         password=self.asr_password) as conn:
            interfaces = ""
            try:
                filter_str = GET_ROUTER_INFO % (vrfname)
                rpc_obj = conn.get(filter=filter_str)

                LOG.info("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<")
                LOG.info("ASR Host %s VRF = %s" % \
                          (self.asr_host,rpc_obj.data_xml))
                tree = etree.XML(rpc_obj.data_xml)
                ns = '{urn:ietf:params:xml:ns:netconf:base:1.0}'
                response = tree.find('{0}cli-oper-data-block/{0}item/{0}response'.format(ns)).text
                # print response
                response_data = iter(response.splitlines())
                for line in response_data:
                    if " Interfaces:" in line:
                        interfaces = next(response_data)
                        interfaces = [x for x in interfaces.split(' ') if x]

                status = "Pass"
                LOG.info(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>")

            except Exception as exc:
                LOG.debug("Caught exception %s" % (exc.message))
                status = "Fail"
            router_vrf_data = {}
            router_vrf_data['vrfname'] = vrfname
            router_vrf_data['interfaces'] = interfaces
            router_vrf_data['status'] = status
        return router_vrf_data
    
    def done(self):
        LOG.debug("done")
        return True
    
    def undo(self):
        LOG.debug("Undo")
        return True
