# -*- coding: utf-8 -*-
DOCUMENTATION = '''
module: mt_system_scheduler
author:
  - "Valentin Gurmeza"
version_added: "2.3"
short_description: Manage mikrotik system scheduler
requirements:
  - mt_api
description:
  - add, remove, or modify a system scheduler task
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
      - sub endpoint for mikrotik system
    required: True
    options:
      - scheduler
  settings:
    description:
      - All Mikrotik compatible parameters for this particular endpoint.
        Any yes/no values must be enclosed in double quotes
    required: True
  state:
    description:
      - absent or present
    required: True
'''

EXAMPLES = '''
- mt_system_scheduler:
    hostname:      "{{ inventory_hostname }}"
    username:      "{{ mt_user }}"
    password:      "{{ mt_pass }}"
    state:         present
    parameter:     scheduler
      name:          test_by_ansible
      comment:       ansible_test
      on_event:      put "hello"
'''

from ansible.module_utils.mt_common import clean_params, MikrotikIdempotent
from ansible.module_utils.basic import AnsibleModule


def main():
  module = AnsibleModule(
    argument_spec=dict(
      hostname=dict(required=True),
      username=dict(required=True),
      password=dict(required=True, no_log=True),
      settings=dict(required=True, type='dict'),
      parameter = dict(
          required  = True,
          choices   = ['scheduler'],
          type      = 'str'
      ),
      state   = dict(
          required  = True,
          choices   = ['present', 'absent'],
          type      = 'str'
      )
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
    api_path         = '/system/' + str(params['parameter']),
    check_mode       = module.check_mode
  )

  # exit if login failed
  if not mt_obj.login_success:
    module.fail_json(
      msg = mt_obj.failed_msg
    )

  # add, remove or edit things
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
