# -*- coding: utf-8 -*-
DOCUMENTATION = '''
module: mt_service
author:
  - "Valentin Gurmeza"
  - "Shaun Smiley"
version_added: "2.3"
short_description: Manage mikrotik ip service
requirements:
  - mt_api
description:
  - enable, disable, or modify a ip service
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
  disabled:
    description:
      - service enabled or disabled
    required: True
    choices:
      - no
      - yes
  name:
    description:
      - name of the service
    required: True
    choices:
      - api
      - api-ssl
      - ftp
      - ssh
      - telnet
      - winbox
      - www
      - www-ssl
  address:
    description:
      - List of IP/IPv6 prefixes from which the service is accessible
  certificate:
    description:
      - The name of the certificate used by particular service. Applicable only for services that depends on certificates (www-ssl, api-ssl)
  port:
    description:
      - The port particular service listens on
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

import mt_api
import re
from ansible.module_utils.basic import AnsibleModule


def main():

  module = AnsibleModule(
      argument_spec=dict(
          hostname   = dict(required=True),
          username   = dict(required=True),
          password   = dict(required=True),
          interface  = dict(required=False, type='str'),
          address    = dict(required=False, type='str'),
          certificate= dict(required=False, type='str'),
          name       = dict(
            required=True,
            choices=[
              'api',
              'api-ssl',
              'ftp',
              'ssh',
              'telnet',
              'winbox',
              'www',
              'www-ssl'
            ],
            type='str'
          ),
          disabled=dict(
            required  = True,
            choices   = ['yes', 'no'],
            type      = 'str'
          ),
      )
  )

  hostname     = module.params['hostname']
  username     = module.params['username']
  password     = module.params['password']
  ansible_service_name  = module.params['name']
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

  service_path = '/ip/service'

  response = mk.api_print(base_path=service_path)
  service_params = module.params
  mikrotik_service = {}
  for item in response:
    if 'name' in item[1].keys():
      if ansible_service_name == item[1]['name']:
        mikrotik_service = item[1]

  #######################################
  # remove keys with empty values
  # remove unneeded parameters
  # modify keys with '_' to match mikrotik parameters
  # convert yes/no to true/false
  ######################################

  remove_params = ['hostname', 'username', 'password']
  for i in remove_params:
    del service_params[i]

  for key in service_params.keys():
    if service_params[key] is None:
      del service_params[key]

  for key in service_params:
    if service_params[key] == "yes":
      service_params[key] = "true"
    if service_params[key] == "no":
      service_params[key] = "false"

  if '.id' in mikrotik_service:
    client_id = mikrotik_service['.id']
  else:
    client_id = False

  service_diff_keys = {}

  for key in service_params:
    if key in mikrotik_service:
      if service_params[key] != mikrotik_service[key]:
        service_diff_keys[key] = service_params[key]
    else:
      service_diff_keys[key] = service_params[key]
  if service_diff_keys == {}:
    ####################
    # Already up date
    ###################
    module.exit_json(
      failed=False,
      changed=False,
    )
  elif service_diff_keys != {}:
    service_diff_keys['numbers'] = client_id
    mk.api_edit(base_path=service_path, params=service_diff_keys)
    module.exit_json(
      failed=False,
      changed=True,
      msg="Changed service item: " + service_params['name'],
    )
  else:
    ####################
    # Failure
    ###################
    module.exit_json(
      failed=True,
      changed=False
    )

if __name__ == '__main__':
  main()
