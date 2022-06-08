# -*- coding: utf-8 -*-
DOCUMENTATION = '''
module: mt_ppp_server
author:
  - "Colin Zwiebel"
version_added: "2.3.1"
short_description: Manage mikrotik ppp servers 
requirements:
  - mt_api
description:
  - Manage ppp servers and their settings.
options:
  hostname:
    description:
      - hostname of mikrotik router
    required: True
  username:
    description:
      - username used to connect to mikrotik router
    required: True
  password:
    description:
      - password used for authentication to mikrotik router
    required: True
  server_type:
    description:
      - VPN server type to manage
    required: True
    options:
      - l2tp
      - ovpn
      - pptp
      - sstp
  settings:
    description:
      - All Mikrotik compatible parameters for this type of vpn server.
        Any yes/no values must be enclosed in double quotes
'''

EXAMPLES = '''
- mt_ppp_server:
    hostname:      "{{ inventory_hostname }}"
    username:      "{{ mt_user }}"
    password:      "{{ mt_pass }}"
    server_type:   pptp
    settings:
      disabled:        no
      max-mtu:         1420
      authentication:  mschap2
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.mt_common import clean_params, MikrotikIdempotent


def main():
  module = AnsibleModule(
    argument_spec = dict(
      hostname  = dict(required=True),
      username  = dict(required=True),
      password  = dict(required=True, no_log=True),
      settings  = dict(required=False, type='dict'),
      server_type = dict(
        required  = True,
        choices   = ['l2tp', 'ovpn', 'pptp', 'sstp'],
        type      = 'str'
      ),
    ),
    supports_check_mode=True
  )

  params = module.params
  mt_obj = MikrotikIdempotent(
    hostname         = params['hostname'],
    username         = params['username'],
    password         = params['password'],
    state            = None,
    desired_params   = params['settings'],
    idempotent_param = None,
    api_path         = '/interface/{}-server/server'.format(params['server_type']),
    check_mode       = module.check_mode
  )

  mt_obj.sync_state()

  if mt_obj.failed:
    module.fail_json(
      msg = mt_obj.failed_msg
    )
  elif mt_obj.changed:
    module.exit_json(
      failed=False,
      changed=True,
      msg=mt_obj.changed_msg,
      diff={ "prepared": {
        "old": mt_obj.old_params,
        "new": mt_obj.new_params,
      }},
    )
  else:
    module.exit_json(
      failed=False,
      changed=False,
      msg=params['settings'],
    )
if __name__ == '__main__':
  main()
