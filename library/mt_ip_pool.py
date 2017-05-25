# -*- coding: utf-8 -*-
DOCUMENTATION = '''
module: mt_dhcp_server
author:
  - "Valentin Gurmeza"
  - "Shaun Smiley"
version_added: "2.3"
short_description: Manage mikrotik ip pools
requirements:
  - mt_api
description:
  - Add or remove ip pool
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
      - ip pool present or absent
    required: True
  name:
    description:
      - name of the ip pool
    required: True
  ranges:
    description:
      - IP address list of non-overlapping IP address ranges
     required: False
  next_pool:
    description:
      - When address is acquired from pool that has no free addresses, and next_pool property is set to another pool, then next IP address will be acquired from next_pool
    required: False
'''

EXAMPLES = '''
# Add a new dhcp server
- mt_dhcp_server:
    hostname:      "{{ inventory_hostname }}"
    username:      "{{ mt_user }}"
    password:      "{{ mt_pass }}"
    state:         present
    name:          ansible_test
    address_pool:  'pool1'
    interface:     vlan15
'''

import mt_api
from ansible.module_utils.basic import AnsibleModule
import re


def main():

  module = AnsibleModule(
      argument_spec=dict(
          hostname=dict(required=True),
          username=dict(required=True),
          password=dict(required=True),
          name=dict(required=True, type='str'),
          ranges=dict(required=False, type='str'),
          next_pool=dict(required=False, type='str'),
          state=dict(
              required  = True,
              choices   = ['present', 'absent'],
              type      = 'str'
          )
      )
  )

  hostname     = module.params['hostname']
  username     = module.params['username']
  password     = module.params['password']
  ip_pool_name     = module.params['name']
  state        = module.params['state']
  changed      = False
  msg = ""

  mk = mt_api.Mikrotik(hostname, username, password)
  try:
    mk.login()
  except:
    module.fail_json(
        msg="Could not log into Mikrotik device." +
        " Check the username and password.",
    )

  ip_pool_path = '/ip/pool'
  response = mk.api_print(base_path=ip_pool_path)
  ip_pool_params = module.params
  mikrotik_ip_pool= {}
  for item in response:
    if 'name' in item[1]:
      if ip_pool_name == item[1]['name']:
        ip_pool_name = item[1]['name']
        mikrotik_ip_pool = item[1]

  #################################################################
  # Since we are grabbing all the parameters passed by the module
  # We need to remove the one that won't be used
  # as mikrotik parameters
  #################################################
  remove_params = ['hostname', 'username', 'password', 'state']
  for i in remove_params:
    ip_pool_params.pop(i)
  #######################################
  # remove keys with empty values
  # convert vars with '_' to '-'
  # convert yes/no to true/false
  ######################################
  for key in ip_pool_params.keys():
    if ip_pool_params[key] is None:
      ip_pool_params.pop(key)

  for key in ip_pool_params.keys():
    new_key = re.sub('_','-', key)
    if new_key != key:
      ip_pool_params[new_key] = ip_pool_params[key]
      del ip_pool_params[key]

  for key in ip_pool_params:
    if ip_pool_params[key] == "yes":
      ip_pool_params[key] = "true"
    if ip_pool_params[key] == "no":
      ip_pool_params[key] = "false"

  ##########################################################
  # Define client_id to be used by remove and edit function
  ##########################################################
  if '.id' in mikrotik_ip_pool:
    client_id = mikrotik_ip_pool['.id']
  else:
    client_id = False

  if state == "present":
    if mikrotik_ip_pool == {}:
      mk.api_add(base_path=ip_pool_path, params=ip_pool_params)
      module.exit_json(
          failed=False,
          changed=True,
          msg="Added dhcp server " + ip_pool_name
      )
    ###################################################
    # If an item exists we check if all the parameters
    # match what we have in ansible
    ######################################
    else:
      ip_pool_diff_keys = {}

      for key in ip_pool_params:
        if key in mikrotik_ip_pool:
          if ip_pool_params[key] != mikrotik_ip_pool[key]:
            ip_pool_diff_keys[key] = ip_pool_params[key]
        else:
          ip_pool_diff_keys[key] = ip_pool_params[key]
      if ip_pool_diff_keys != {}:
        ip_pool_diff_keys['numbers'] = client_id
        mk.api_edit(base_path=ip_pool_path, params=ip_pool_diff_keys)
        module.exit_json(
            failed=False,
            changed=True,
            msg="Changed dhcp sever item: " + ip_pool_params['name'],
        )
      else:
        ####################
        # Already up date
        module.exit_json(
            failed=False,
            changed=False,
        )
  elif state == "absent":
    if client_id:
      mk.api_remove(base_path=ip_pool_path, remove_id=client_id)
      module.exit_json(
          failed=False,
          changed=True,
          msg=ip_pool_params['name'] + " removed"
      )
    #####################################################
    # if client_id is not set there is nothing to remove
    #####################################################
    else:
      module.exit_json(
          failed=False,
          changed=False,
          ms=mikrotik_ip_pool
      )
  else:
    module.exit_json(
        failed=True,
        changed=False,
    )
if __name__ == '__main__':
  main()
