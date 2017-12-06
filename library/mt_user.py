# -*- coding: utf-8 -*-
DOCUMENTATION = '''
module: mt_user
author:
  - "Valentin Gurmeza"
version_added: "2.4"
short_description: Manage mikrotik user endpoints
requirements:
  - mt_api
description:
  - Generic mikrotik user module.
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
      - sub endpoint for mikrotik user
    required: True
    options:
      - user
      - active
      - aaa
  settings:
    description:
      - All Mikrotik compatible parameters for this particular endpoint.
        Any yes/no values must be enclosed in double quotes
  state:
    description:
      - absent or present
'''

EXAMPLES = '''
- mt_user:
    hostname:    "{{ inventory_hostname }}"
    username:    "{{ mt_user }}"
    password:    "{{ mt_pass }}"
    parameter:   user
    settings:
      name:  test1
      group: read
'''

from ansible.module_utils.mt_common import clean_params, MikrotikIdempotent
from ansible.module_utils.basic import AnsibleModule



def main():
  module = AnsibleModule(
    argument_spec = dict(
      hostname  = dict(required=True),
      username  = dict(required=True),
      password  = dict(required=True),
      settings  = dict(required=False, type='dict'),
      parameter = dict(
        required  = True,
        choices   = ['user', 'active', 'aaa'],
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

  idempotent_parameter = None
  params = module.params
  idempotent_parameter = 'name'

  if params['parameter'] == 'group':
    params['parameter'] = 'user/group'
  mt_obj = MikrotikIdempotent(
    hostname         = params['hostname'],
    username         = params['username'],
    password         = params['password'],
    state            = params['state'],
    desired_params   = params['settings'],
    idempotent_param = idempotent_parameter,
    api_path         = '/' + str(params['parameter']),
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
