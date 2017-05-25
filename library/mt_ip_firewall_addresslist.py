# -*- coding: utf-8 -*-
DOCUMENTATION = '''
module: mt_ip_firewall_filter
author:
  - "Valentin Gurmeza"
  - "Shaun Smiley"
version_added: "2.3"
short_description: Manage mikrotik /ip/firewall/filter
requirements:
  - mt_api
description:
  - FILL ME OUT
options:
  hostname:
    description:
      -
  username:
    description:
      -
  password:
    description:
      -
  list-name:
    description:
      - name of the address-list
  state:
    description:
      - present or absent
  address_list:
    description:
      - A list of single IP addresses or range of IPs to add to address-list.
        Can also be a set to a hostname which will create a dynamic entry
        in the list with the proper IP address for the record (as of 6.38.1)
'''

EXAMPLES = '''
- mt_ip_firewall_addresslist:
    hostname:      "{{ inventory_hostname }}"
    username:      "{{ mt_user }}"
    password:      "{{ mt_pass }}"
    state:         "present"
    name:          "block_all"
    dynamic: false
    address_list:
      - 192.168.10.1
      - yahoo.com
      - 19.134.52.23/23
'''

import mt_api
from ansible.module_utils.basic import AnsibleModule


def main():

  module = AnsibleModule(
      argument_spec=dict(
          hostname  = dict(required=True),
          username  = dict(required=True),
          password  = dict(required=True),
          list_name  = dict(required=True, type='str'),
          address_list = dict(required=False, type='list'),
          state = dict(
              required  = False,
              default   = "present",
              choices   = ['present', 'absent', 'force'],
              type      = 'str'
          ),
      )
  )

  hostname     = module.params['hostname']
  username     = module.params['username']
  password     = module.params['password']
  ansible_list_name = module.params['list_name']
  ansible_address_list = module.params['address_list']
  state        = module.params['state']
  changed      = False
  msg = ""

  address_list_path = '/ip/firewall/address-list'
  mk = mt_api.Mikrotik(hostname, username, password)
  try:
    mk.login()
  except:
    module.fail_json(
        msg="Could not log into Mikrotik device." +
        " Check the username and password.",
    )

  response = mk.api_print(address_list_path)
  mikrotik_address_list = []
  mikrotik_address_id = {}
  list_name = ansible_list_name
  for item in response:
    if 'list' in item[1].keys():
      address = item[1]['address']
      if item[1]['list'] == list_name:
        temp_dict = {}
        temp_dict['address'] = item[1]['address']
        if 'comment' in item[1].keys():
          temp_dict['comment'] = item[1]['comment']
        mikrotik_address_list.append(dict(temp_dict))
        mikrotik_address_id[address] = item[1]['.id']

  if state == "present":
    if ansible_address_list == mikrotik_address_list:
      module.exit_json(
          changed = False,
          failed  = False,
          msg     = "list up to date",
      )
    common_list = []
    for item in ansible_address_list:
      for item2 in mikrotik_address_list:
        if item['address'] in item2['address']:
          common_list.append(item['address'])
          if item['comment'] in item2['comment']:
            ##################
            # update comment
            #################
            pass

    #################################
    # build add_list
    # add item missing from mikrotik
    #################################
    add_list = []
    for item in ansible_address_list:
      if item['address'] not in common_list:
        temp_dict = {}
        temp_dict['address'] = item['address']
        temp_dict['comment'] = item['comment']
        add_list.append(dict(temp_dict))

    for i in add_list:
      #address = i['address']
      #comment = i['comment']
      add_dictionary = {
        "address": i['address'],
        "list": list_name,
        "comment": i['comment']
      }
      mk.api_add(address_list_path, add_dictionary)
      changed = True

    #####################
    # build remove list
    ######################
    remove_list = []
    for item in mikrotik_address_list:
      if item['address'] not in common_list:
        remove_list.append(item['address'])
    #######################################
    # Remove every item in the address_list
    #######################################
    for i in remove_list:
      remove_id = mikrotik_address_id[i]
      mk.api_remove(address_list_path, remove_id)
      if not changed:
        changed = True
  else:
    #######################################
    # Remove every item
    #######################################
    for remove_id in mikrotik_address_id.values():
      mk.api_remove(address_list_path, remove_id)
      if not changed:
        changed = True

  if changed:
     module.exit_json(
         changed = True,
         failed = False,
         msg    = ansible_list_name + "has been modified",
     )
  else:
    module.exit_json(
        changed = False,
        failed = False,
        msg    = ansible_list_name + " is up to date",
    )


if __name__ == '__main__':
  main()
