# -*- coding: utf-8 -*-
DOCUMENTATION = '''
module: mt_interface_ovpn_client
author:
  - "Valentin Gurmeza"
  - "Shaun Smiley"
version_added: "2.3"
short_description: Manage mikrotik openvpn client
requirements:
  - mt_api
description:
  - add, remove, or modify an openvpn client. Mikrotik uses ovpn alias for openvpn.
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
      - ovpn client present or absent
    required: True
    choices:
      - present
      - absent
  comment:
    description:
      - ovpn client comment
    required: False
  name:
    description:
      - name of the ovpn client
  user:
    description:
      - vpn user name
    required: True # if state is present
  connect_to:
    description:
      - Remote address of the OVPN server
    required: True # if state is present
  vpn_password:
    description:
      - ovpn client password
    required: True # if state is present
  port:
    description:
      - ovpn client port
    required: False
  max_mtu:
    description:
      -  Maximum Transmission Unit. Max packet size that OVPN interface will be able to send without packet fragmentation.
    required: False
  profile:
    description:
      - Used PPP profile
    required: False
  certificate:
    description:
      - Name of the client certificate
    required: False
  mac_address:
    description:
      - Mac address of OVPN interface
    required: False
  add_default_route:
    description:
      - Whether to add OVPN remote address as a default route
    required: False
    choices:
      - yes
      - no
  cipher:
    description:
      - Allowed ciphers
    required: False
    choices:
      - blowfish128
      - aes128
      - aes192
      - aes256
  auth:
    description:
      - Allowed authentication methods
    required: False
    choices:
      - sha1
      - md5
      - null
      - aes256
  mode:
    description:
      - Layer3 or layer2 tunnel mode (alternatively tun, tap)
    required: False
    choices:
      - ip
      - ethernet
'''

EXAMPLES = '''
- mt_interface_ovpn_client:
    hostname:      "{{ inventory_hostname }}"
    username:      "{{ mt_user }}"
    password:      "{{ mt_pass }}"
    state:         present
    vpn_user:      ansible_admin
    connect_to:    192.168.230.1
    client_name:   ansible_test
    vpn_password: 'password'
'''

import mt_api
import re
from ansible.module_utils.basic import AnsibleModule


def main():

  module = AnsibleModule(
      argument_spec=dict(
          hostname     = dict(required=True),
          username     = dict(required=True),
          password     = dict(required=True),
          name         = dict(required=True, type='str'),
          user         = dict(required=False, type='str'),
          connect_to   = dict(required=False, type='str'),
          comment      = dict(required=False, type='str'),
          vpn_password = dict(required=False, type='str'),
          port         = dict(required=False, type='str'),
          max_mtu      = dict(required=False, type='str'),
          profile      = dict(required=False, type='str'),
          certificate  = dict(required=False, type='str'),
          mac_address  = dict(required=False, type='str'),
          add_default_route  = dict(
              required  = False,
              choices = ['yes', 'no'],
              type='str'
          ),
          cipher       = dict(
              required  = False,
              choices   = ['blowfish128', 'aes128', 'aes192', 'aes256'],
              type='str'
          ),
          auth          = dict(
              required  = False,
              choices   = ['sha1', 'md5', 'null'],
              type='str'
          ),
          mode         = dict(
              required  = False,
              choices   = ['ip', 'ethernet'],
              type='str'
          ),
          state         = dict(
              required  = False,
              choices   = ['present', 'absent'],
              type      = 'str'
          ),
      )
  )

  hostname     = module.params['hostname']
  username     = module.params['username']
  password     = module.params['password']
  state        = module.params['state']
  ansible_client_name  = module.params['name']
  ansible_mac_address = module.params['mac_address']
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

  ovpn_client_path = '/interface/ovpn-client'

  response = mk.api_print(base_path=ovpn_client_path)
  ovpn_client_params = module.params
  mikrotik_client_name = ""
  mikrotik_ovpn_client = {}
  for item in response:
    if 'name' in item[1].keys():
      if ansible_client_name == item[1]['name']:
        mikrotik_client_name = item[1]['name']
        mikrotik_ovpn_client = item[1]

  #######################################
  # remove keys with empty values
  # remove unneeded parameters
  # modify keys with '_' to match mikrotik parameters
  ######################################
  remove_params = ['hostname', 'username', 'password', 'state']
  for i in remove_params:
    del ovpn_client_params[i]
  for key in ovpn_client_params.keys():
    if ovpn_client_params[key] is None:
      del ovpn_client_params[key]

  for key in ovpn_client_params.keys():
    if 'vpn_password' == key:
      ovpn_client_params['password'] = ovpn_client_params[key]
      del ovpn_client_params[key]

  for key in ovpn_client_params.keys():
    new_key = re.sub('_','-', key)
    if new_key != key:
      ovpn_client_params[new_key] = ovpn_client_params[key]
      del ovpn_client_params[key]

  if state == "present":
    if mikrotik_ovpn_client == {}:
      mk.api_add(
          base_path=ovpn_client_path,
          params=ovpn_client_params
      )
      module.exit_json(
          changed=True,
          failed=False,
          msg=ansible_client_name + " client added"
      )
    else:
      mikrotik_ovpn_client['add-default-route'] = 'no'
      if 'comment' in ovpn_client_params and 'comment' not in mikrotik_ovpn_client:
        mikrotik_ovpn_client['comment'] = None
      client_id = mikrotik_ovpn_client['.id']
      for i in ['.id', 'running']:
        mikrotik_ovpn_client.pop(i)
      update_keys = {}
      for key, value in ovpn_client_params.items():
          if value != mikrotik_ovpn_client[key]:
              update_keys[key] = value
      if update_keys == {}:
        module.exit_json(
            changed=False,
            failed=False,
        )
      else:
        update_keys['numbers'] = client_id
        mk.api_edit(
            base_path=ovpn_client_path,
            params=update_keys
        )
        module.exit_json(
            changed=True,
            failed=False,
            msg=update_keys,
        )
  else:
    if mikrotik_ovpn_client == {}:
        module.exit_json(
            changed=False,
            failed=False,
        )
    else:
      remove_response = mk.api_remove(
          base_path=ovpn_client_path,
          remove_id=mikrotik_ovpn_client['.id']
      )
      module.exit_json(
          changed=True,
          failed=False,
          msg=remove_response[0]
      )

if __name__ == '__main__':
  main()
