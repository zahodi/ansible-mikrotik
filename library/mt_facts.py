#!/usr/bin/python
# -*- coding: utf-8 -*-

ANSIBLE_METADATA = {'metadata_version': '1.0',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = '''
---
module: mt_facts
short_description: Gather facts for mikrotik devices.
description:
     - This module fetches data from the Mikrotik API
author: "kollyma"
options:
  filter:
    description:
      - Filter for a specific fact.
    choices:
      - interface_ethernet
      - system_ntp_client
      - system_routerboard
      - ip_route
      - ip_dns
      - ip_address

requirements: [ 'yaml' ]
'''

RETURN = '''
---
interface_ethernet:
  description: Return list of Mikrotik Interfaces
  returned: success
  type: list
  sample:  interface_ethernet [ {
                "mac_address": "4C:5E:0C:F4:BF:44",
                "master_port": "none",
                "mtu": "1500",
                "name": "ether1",
                "default_name": "ether1",
                "disabled": "false",
                ...
            } ]
system_routerboard:
  description: Return Mikrotik System Information
  returned: success
  type: dict
  sample:  "system_routerboard": {
            "current_firmware": "3.19",
            "factory_firmware": "3.19",
            "firmware_type": "ar9344",
            "model": "951G-2HnD",
            "routerboard": "true",
            "serial_number": "557E04B12525",
            "upgrade_firmware": "3.41"
        }
system_ntp_client:
  description: Return NTP Client Information
  returned: success
  type: dict
  sample:  "system_ntp_client": {
            "active_server": "5.148.175.134",
            "enabled": "true",
            "last_adjustment": "1ms538us",
            "last_update_before": "6m19s560ms",
            "last_update_from": "5.148.175.134",
            "mode": "unicast",
            "poll_interval": "15m",
            "primary_ntp": "213.251.53.234",
            "secondary_ntp": "5.148.175.134",
            "server_dns_names": ""
        },
ip_route:
  description: Return Mikrotik IP Routes
  returned: success
  type: dict
  sample:  "ip_route": {
                "active": "true",
                "distance": "1",
                "dst_address": "0.0.0.0/0",
                "dynamic": "true",
                "gateway": "8.8.8.8",
                "static": "true",
                "vrf_interface": "ether1"
            }
ip_address:
  description: Return Mikrotik IP addresses
  returned: success
  type: list
  sample:  "ip_address": [
                {
                    ".id": "*1",
                    "actual-interface": "bridge",
                    "address": "192.168.88.1/24",
                    "comment": "defconf",
                    "disabled": "false",
                    "dynamic": "false",
                    "interface": "bridge",
                    "invalid": "false",
                    "network": "192.168.88.0"
                }, ]
'''


import re
from ansible.module_utils import mt_api
from ansible.module_utils.basic import AnsibleModule


class MikrotikFacts(object):

    def __init__(self, hostname, username, password):

        self.hostname = hostname
        self.username = username
        self.password = password
        self.login_success = False
        self.current_params = {}
        self.mk = None
        self.failed_msg = None
        self.login()

    def run(self):
        param = dict()
        filter = module.params.get('filter')
        self.current_params = self.mk.api_print(base_path='/' + re.sub('_', '/', filter))

        if len(self.current_params) > 2:
            param[filter] = []
            for current_param in self.current_params[:-1]:
                param[filter].append(current_param[1])
        else:
            param[filter] = dict()
            for key, value in self.current_params[0][1].items():
                key = re.sub('-', '_', key)
                param[filter][key] = value

        return param

    def login(self):
        self.mk = mt_api.Mikrotik(
            self.hostname,
            self.username,
            self.password,
          )
        try:
            self.mk.login()
            self.login_success = True
        except:
            self.failed_msg = "Could not log into Mikrotik device, check the username and password."


def main():
    global module
    module = AnsibleModule(
      argument_spec = dict(
        filter=dict(default='system_routerboard', choices=[
                'interface_ethernet',
                'system_ntp_client',
                'system_routerboard',
                'ip_route',
                'ip_dns',
                'ip_address',
        ]),
        hostname=dict(required=True),
        username=dict(required=True),
        password=dict(required=True, no_log=True),
      ),
      supports_check_mode=True
    )

    params = module.params
    device = MikrotikFacts(params['hostname'], params['username'], params['password'])
    mt_facts = device.run()
    mt_facts_result = dict(changed=False, ansible_facts=mt_facts)
    module.exit_json(**mt_facts_result)

if __name__ == '__main__':
    main()
