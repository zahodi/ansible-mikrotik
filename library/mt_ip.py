# -*- coding: utf-8 -*-
DOCUMENTATION = '''
module: mt_ip
author:
  - "Valentin Gurmeza"
  - "Shaun Smiley"
version_added: "2.3"
short_description: Manage mikrotik ip endpoints
requirements:
  - mt_api
description:
  - enable, disable, or modify a ip endpoint settings
options:
  hostname:
    description:
      - hotstname of mikrotik router
    required: True
  username:
    description:
      - username used to connect to mikrotik router
    required: True
  password:
    description:
      - password used for authentication to mikrotik router
    required: True
  parameter:
    description:
      - sub endpoint for mikrotik snmp
    required: True
    options:
      - netwatch
      - e-mail
  settings:
    description:
      - All Mikrotik compatible parameters for this particular endpoint.
        Any yes/no values must be enclosed in double quotes
  state:
    description:
      - absent or present
'''

EXAMPLES = '''
- mt_service:
    hostname:      "{{ inventory_hostname }}"
    username:      "{{ mt_user }}"
    password:      "{{ mt_pass }}"
    disabled:      no
    name:          ftp
    address:       192.168.52.3
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
      parameter = dict(
        required  = True,
        choices   = ['service', 'pool'],
        type      = 'str'
      ),
      state   = dict(
        required  = False,
        choices   = ['present', 'absent'],
        type      = 'str'
      ),
    ),
    supports_check_mode=True
  )

  params = module.params
  idempotent_parameter = 'name'

  mt_obj = MikrotikIdempotent(
    hostname         = params['hostname'],
    username         = params['username'],
    password         = params['password'],
    state            = params['state'],
    desired_params   = params['settings'],
    idempotent_param = idempotent_parameter,
    api_path         = '/ip/' + str(params['parameter']),
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
