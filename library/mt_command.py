# -*- coding: utf-8 -*-
DOCUMENTATION = '''
module: mt_command
author:
  - "Valentin Gurmeza"
version_added: "2.3"
short_description: Issue mikrotik command
requirements:
  - mt_api
description:
  - Issue a mikrotik command
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
  command:
    description:
      -  command to be sent to the router. The command must be a command path using
      - '/' for word separation
    required: True
  command_arguments:
    description:
      - parameters to pass with the command. Must be a dictionary
'''

EXAMPLES = '''
- mt_command:
    hostname:      "{{ inventory_hostname }}"
    username:      "{{ mt_user }}"
    password:      "{{ mt_pass }}"
    command:       /system/backup/save
    command_arguments:
      name:     ansible_test
      password: 123
'''

from ansible.module_utils import mt_api
from ansible.module_utils.mt_common import clean_params
from ansible.module_utils.basic import AnsibleModule


def main():

  module = AnsibleModule(
      argument_spec=dict(
          hostname=dict(required=True),
          username=dict(required=True),
          password=dict(required=True, no_log=True),
          command=dict(required=True, type='str'),
          command_arguments=dict(required=False, type='dict'),
      )
  )

  hostname     = module.params['hostname']
  username     = module.params['username']
  password     = module.params['password']
  changed = False
  changed_message = []

  mk = mt_api.Mikrotik(hostname, username, password)
  try:
    mk.login()
  except:
    module.fail_json(
        msg="Could not log into Mikrotik device." +
        " Check the username and password.",
    )

  api_path = module.params['command']

  if module.params['command_arguments'] != None:
    response = mk.api_command(base_path=api_path, params=module.params['command_arguments'])
  else:
    response = mk.api_command(base_path=api_path)

  if response[-1][0] == '!done':
    changed = True
    changed_message.append(response)
    changed_message.append(api_path)
    if module.params['command_arguments'] != None:
      changed_message.append(module.params['command_arguments'])

  if changed:
    module.exit_json(
        failed=False,
        changed=True,
        msg=changed_message
    )
  else:
    module.exit_json(
        failed=False,
        changed=False,
        msg="Command failed"
    )
if __name__ == '__main__':
  main()
