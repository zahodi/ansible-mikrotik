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
  state:
    description:
      - scheduler task present or absent
    required: True
    choices:
      - present
      - absent
  comment:
    description:
      - task comment
  interval:
    description:
      - interval between two script executions, if time interval is set to zero, the script is only executed at its start time, otherwise it is executed repeatedly at the time interval is specified
  name:
    description:
      -  name of the task
    required: True
  on_event:
    description:
      - name of the script to execute.
  start_date:
    description:
      - date of the first script execution
  start_time:
    description:
      - time of the first script execution
  policy:
    description:
      - policy
'''

EXAMPLES = '''
- mt_system_scheduler:
    hostname:      "{{ inventory_hostname }}"
    username:      "{{ mt_user }}"
    password:      "{{ mt_pass }}"
    state:         present
    name:          test_by_ansible
    comment:       ansible_test
    on_event:      put "hello"
'''

from ansible.module_utils import mt_api
from ansible.module_utils.mt_common import clean_params
from ansible.module_utils.basic import AnsibleModule


def main():
  module = AnsibleModule(
    argument_spec=dict(
      hostname  =dict(required=True),
      username  =dict(required=True),
      password  =dict(required=True, no_log=True),
      name      =dict(required=True, type='str'),
      on_event  =dict(required=False, type='str'),
      comment   =dict(required=False, type='str'),
      interval  =dict(required=False, type='str'),
      policy    =dict(required=False, type='list'),
      start_date=dict(required=False, type='str'),
      start_time=dict(required=False, type='str'),
      state=dict(
        required=True,
        choices=['present', 'absent'],
        type='str'
      ),
    ),
    supports_check_mode=True
  )

  hostname     = module.params['hostname']
  username     = module.params['username']
  password     = module.params['password']
  state        = module.params['state']
  check_mode   = module.check_mode
  ansible_scheduler_name  = module.params['name']
  changed = False
  changed_message = []
  msg = ""

  mk = mt_api.Mikrotik(hostname, username, password)
  try:
    mk.login()
  except:
    module.fail_json(
        msg="Could not log into Mikrotik device." +
        " Check the username and password.",
    )

  api_path = '/system/scheduler'

  response = mk.api_print(base_path=api_path)
  ansible_scheduler_params = module.params
  mikrotik_scheduler_task = {}
  for item in response:
    if 'name' in item[1]:
      if ansible_scheduler_name == item[1]['name']:
        mikrotik_scheduler_task = item[1]

  #######################################
  # remove unneeded parameters
  ######################################

  remove_params = ['hostname', 'username', 'password', 'state']
  for i in remove_params:
    del ansible_scheduler_params[i]


  ##########################################
  # modify params in place
  ############################################
  clean_params(ansible_scheduler_params)


  if '.id' in mikrotik_scheduler_task:
    client_id = mikrotik_scheduler_task['.id']
  else:
    client_id = False

  if state == "present":
    #################################################
    # Convert policy list to comma separated string
    #################################################

    if mikrotik_scheduler_task == {}:
      if 'policy' in ansible_scheduler_params:
        list_to_string = ""
        list_to_string = ','.join(map(str, ansible_scheduler_params['policy']))
        ansible_scheduler_params['policy'] = list_to_string
      if not check_mode:
        mk.api_add(
            base_path=api_path,
            params=ansible_scheduler_params
        )
      changed_message.append(ansible_scheduler_name + " added to bridge")
      changed = True,
    else:
      scheduler_diff_keys = {}

      ########################################################################
      # policy parameter is a comma separated list of values in a string that
      # we receive from mikrotik
      # we need to convert it to a list and then do a comparison against
      # ansible policy list to get the difference
      # if there is a difference between the two we need to convert the
      # ansible_scheduler_params['policy'] to a string with comma separated values
      #########################################################################

      if 'policy' in ansible_scheduler_params:
        dif_list = []
        if 'policy' in mikrotik_scheduler_task:
          policy = mikrotik_scheduler_task['policy'].split(',')
          dif_list = set(ansible_scheduler_params['policy']) & set(policy)

        if dif_list == []:
          list_to_string = ""
          list_to_string = ','.join(map(str, ansible_scheduler_params['policy']))
          scheduler_diff_keys['policy'] = list_to_string

      for key in ansible_scheduler_params:
        if key != 'policy':
          if key in mikrotik_scheduler_task:
            if ansible_scheduler_params[key] != mikrotik_scheduler_task[key]:
              scheduler_diff_keys[key] = ansible_scheduler_params[key]
          else:
            scheduler_diff_keys[key] = ansible_scheduler_params[key]
      if scheduler_diff_keys != {}:
        scheduler_diff_keys['numbers'] = client_id
        if not check_mode:
          mk.api_edit(base_path=api_path, params=scheduler_diff_keys)
        changed = True
        changed_message.append(
          "Changed scheduler task : " + ansible_scheduler_params['name']
        )
      else:
        ####################
        # Already up date
        ###################
        if not changed:
          changed = False

  elif state == "absent":
    if client_id:
      if not check_mode:
        mk.api_remove(base_path=api_path, remove_id=client_id)
      changed_message.append(ansible_scheduler_params['name'] + " removed")
      changed = True
    #####################################################
    # if client_id is not set there is nothing to remove
    #####################################################
    else:
      if not changed:
        changed = False
  else:
    module.exit_json(
        failed=True,
        changed=False,
        msg="state is invalid"
    )

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
    )
if __name__ == '__main__':
  main()
