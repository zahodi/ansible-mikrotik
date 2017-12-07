# -*- coding: utf-8 -*-
DOCUMENTATION = '''
module: mt_interface_bridge
author:
  - "Valentin Gurmeza"
  - "Shaun Smiley"
version_added: "2.3"
short_description: Manage mikrotik bridge
requirements:
  - mt_api
description:
  - add, remove, or modify a bridge.
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
      - bridge present or absent
    required: True # if modifying bridge
    choices:
      - present
      - absent
  name:
    description:
      - name of the bridge
  comment:
    description:
      - brige comment
  admin_mac:
    description:
      - Static MAC address of the bridge (takes effect if auto-mac=no)
  ageing_time:
    description:
      - How long a host's information will be kept in the bridge database
  arp:
    description:
      - Address Resolution Protocol setting
    choices:
      - disabled
      - enabled
      - proxy-arp
      - reply-only
  auto_mac:
    description:
      - Automatically select one MAC address of bridge ports as a bridge MAC address
    choices:
      - yes
      - no
  forward_delay:
    description:
      - Time which is spent during the initialization phase of the bridge interface (i.e., after router startup or enabling the interface) in listening/learning state before the bridge will start functioning normally
  max_message_age:
    description:
      - How long to remember Hello messages received from other bridges
  mtu:
    description:
      - Maximum Transmission Unit
  priority:
    description:
      - Spanning tree protocol priority for bridge interface
  protocol_mode:
    description:
      - Select Spanning tree protocol (STP) or Rapid spanning tree protocol (RSTP) to ensure a loop-free topology for any bridged LAN
    choices:
      - none
      - rstp
      - stp
  transmit_hold_count:
    description:
      - The Transmit Hold Count used by the Port Transmit state machine to limit transmission rate
  settings:
    description:
      - Bridge settings. If defined this argument is a key/value dictionary
    choices:
      - allow-fast-path: yes/no
      - use-ip-firewall: yes/no
      - use-ip-firewall-for-ppoe: yes/no
      - use-ip-firewall-for-bridge: yes/no


'''

EXAMPLES = '''
- mt_interface_bridge:
    hostname:      "{{ inventory_hostname }}"
    username:      "{{ mt_user }}"
    password:      "{{ mt_pass }}"
    state:         present
    name:          bridge_native
    interface:     ether7
    comment:       ansible_test
'''

from ansible.module_utils import mt_api
from ansible.module_utils.mt_common import clean_params
from ansible.module_utils.basic import AnsibleModule


def main():
  module = AnsibleModule(
    argument_spec=dict(
      hostname       = dict(required=True),
      username       = dict(required=True),
      password       = dict(required=True),
      name           = dict(required=False, type='str'),
      comment        = dict(required=False, type='str'),
      admin_mac      = dict(required=False, type='str'),
      auto_mac       = dict(required=False, type='str'),
      ageing_time    = dict(required=False, type='str'),
      forward_delay  = dict(required=False, type='str'),
      max_message_age=dict(required=False, type='str'),
      transmit_hold_count=dict(required=False, type='str'),
      arp      = dict(
        required = False,
        choices   = ['disabled', 'enabled', 'proxy-arp', 'reply-only'],
        type='str'
      ),
      protocol_mode= dict(
        required  = False,
        choices   = ['none', 'rstp', 'stp'],
        type='str'
      ),
      settings= dict(
        required  = False,
        type='dict'
      ),
      state= dict(
        required  = False,
        choices   = ['present', 'absent'],
        type      = 'str'
      ),
    ),
    supports_check_mode=True
  )

  hostname     = module.params['hostname']
  username     = module.params['username']
  password     = module.params['password']
  state        = module.params['state']
  ansible_bridge_name  = module.params['name']
  check_mode = module.check_mode
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

  bridge_path = '/interface/bridge'

  response = mk.api_print(base_path=bridge_path)
  bridge_params = module.params
  mikrotik_bridge = {}
  for item in response:
    if 'name' in item[1]:
      if ansible_bridge_name == item[1]['name']:
        mikrotik_bridge = item[1]

  ########################################################
  # Check if we need to edit the bridge settings
  ########################################################
  if bridge_params['settings'] is not None:
    settings_path = '/interface/bridge/settings'
    settings_response = mk.api_print(settings_path)
    settings_response = settings_response[0][1]
    settings = bridge_params['settings']
    bridge_settings_diff_keys = {}

    for key in settings:
      if isinstance(settings[key], bool):
        settings[key] = str(settings[key])
        settings[key] = str.lower(settings[key])
      else:
        if settings[key] == "yes":
          settings[key] = "true"
        if settings[key] == "no":
          settings[key] = "false"

    for key in settings:
      if key in settings_response:
        if settings[key] != settings_response[key]:
          bridge_settings_diff_keys[key] = settings[key]
      else:
        bridge_settings_diff_keys[key] = settings[key]

    if bridge_settings_diff_keys != {}:
      if not check_mode:
        mk.api_edit(base_path=settings_path, params=bridge_settings_diff_keys)
      changed_message.append(bridge_settings_diff_keys)
      changed = True
    else:
      changed = False

  #######################################
  # remove unneeded parameters
  # clean up parameters
  ######################################

  remove_params = ['hostname', 'username', 'password', 'state', 'settings']
  for i in remove_params:
    del bridge_params[i]

  clean_params(bridge_params)

  if '.id' in mikrotik_bridge:
    client_id = mikrotik_bridge['.id']
  else:
    client_id = False

  ##################################################################
  # We need to make sure that bridge_bridge name is a string
  # if it's null then it has not been defined.
  ###################################################################
  if (state == "present" and isinstance(ansible_bridge_name, str)):
    if mikrotik_bridge == {}:
      if not check_mode:
        mk.api_add(
            base_path=bridge_path,
            params=bridge_params
        )
      changed_message.append(ansible_bridge_name + " added")
      changed = True,
    else:
      bridge_diff_keys = {}

      for key in bridge_params:
        if key in mikrotik_bridge:
          if bridge_params[key] != mikrotik_bridge[key]:
            bridge_diff_keys[key] = bridge_params[key]
        else:
          bridge_diff_keys[key] = bridge_params[key]
      if bridge_diff_keys != {}:
        bridge_diff_keys['numbers'] = client_id
        if not check_mode:
          mk.api_edit(base_path=bridge_path, params=bridge_diff_keys)
        changed = True
        changed_message.append("Changed bridge: " + bridge_params['name'])
      else:
        ####################
        # Already up date
        ###################
        if not changed:
          changed = False

  elif state == "absent":
    if client_id:
      if not check_mode:
        mk.api_remove(base_path=bridge_path, remove_id=client_id)
      changed_message.append(bridge_params['name'] + " removed")
      changed = True
    #####################################################
    # if client_id is not set there is nothing to remove
    #####################################################
    else:
      if not changed:
        changed = False
  elif settings:
    ########################################################
    # if settings were set we were modifying bridge settings
    # only
    pass
  else:
    module.exit_json(
        failed=True,
        changed=False,
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
