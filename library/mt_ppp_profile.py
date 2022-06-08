# -*- coding: utf-8 -*-
DOCUMENTATION = '''
module: mt_ppp_profile
author:
  - "Colin Zwiebel"
version_added: "2.4.1"
short_description: Manage mikrotik ppp profiles
requirements:
  - mt_api
description:
  - Generic mikrotik ppp profile management module.
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
  settings:
    description:
      - All Mikrotik compatible parameters for the ppp-profile endpoint.
        Any yes/no values must be enclosed in double quotes
  state:
    description:
      - absent or present
'''

EXAMPLES = '''
- mt_ppp_profile:
    hostname:      "{{ inventory_hostname }}"
    username:      "{{ mt_user }}"
    password:      "{{ mt_pass }}"
    state:         present
    settings:
      name:            example-profile
      local-address:   1.2.3.4
      change-tcp-mss:  "y"
      use-compression: "y"
      use-encryption:  required
'''

from ansible.module_utils.mt_common import clean_params, MikrotikIdempotent
from ansible.module_utils.basic import AnsibleModule


def main():
  module = AnsibleModule(
    argument_spec = dict(
      hostname  = dict(required=True),
      username  = dict(required=True),
      password  = dict(required=True, no_log=True),
      settings  = dict(required=False, type='dict'),
      state   = dict(
        required  = False,
        choices   = ['present', 'absent'],
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
    state            = params['state'],
    desired_params   = params['settings'],
    idempotent_param = 'name',
    api_path         = '/ppp/profile',
    check_mode      = module.check_mode
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
      #msg='',
      msg=params['settings'],
    )

if __name__ == '__main__':
  main()
