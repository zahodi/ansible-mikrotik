# -*- coding: utf-8 -*-
DOCUMENTATION = '''
module: mt_interface_bridge_port
author:
  - "Valentin Gurmeza"
  - "Shaun Smiley"
version_added: "2.3"
short_description: Manage mikrotik bridge_port
requirements:
  - mt_api
description:
  - add, remove, or modify a bridge_port.
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
      - inteface present or absent in the bridge
    required: True
    choices:
      - present
      - absent
  comment:
    description:
      - brige comment
  auto_isolate:
    description:
      - Prevents STP blocking port from erroneously moving into a forwarding state if no BPDU's are received on the bridge
    choices:
      - yes
      - no
  bridge:
    description:
      -  The bridge interface the respective interface is grouped in
  edge:
    description:
      - Set port as edge port or non-edge port, or enable automatic detection. Edge ports are connected to a LAN that has no other bridge attached. If the port is configured to discover edge port then as soon as the bridge_ detects a BPDU coming to an edge port, the port becomes a non-edge port
    choices:
      - auto
      - no
      - no-discover
      - yes
      - yes-discover
  external_fdb:
    description:
      - Whether to use wireless registration table to speed up bridge host learning
    choices:
      - yes
      - no
      - auto
  horizon:
    description:
      - Use split horizon bridging to prevent bridging loops
  interface:
    description:
      - Name of the interface
  path_cost:
    description:
      - Path cost to the interface, used by STP to determine the "best" path
  point_to_point:
    description:
      - point to point
    choices:
      - yes
      - no
      - auto
  priority:
    description:
      - The priority of the interface in comparison with other going to the same subnet
'''

EXAMPLES = '''
- mt_interface_bridge_port:
    hostname:      "{{ inventory_hostname }}"
    username:      "{{ mt_user }}"
    password:      "{{ mt_pass }}"
    state:         present
    name:          bridge_port_native
    interface:     ether7
    comment:       ansible_test
'''

from ansible.module_utils import mt_api
from ansible.module_utils.mt_common import clean_params
from ansible.module_utils.basic import AnsibleModule


def main():
  module = AnsibleModule(
    argument_spec=dict(
      hostname    =dict(required=True),
      username    =dict(required=True),
      password    =dict(required=True),
      interface   =dict(required=True, type='str'),
      bridge =dict(required=False, type='str'),
      comment     =dict(required=False, type='str'),
      path_cost   =dict(required=False, type='str'),
      priority    =dict(required=False, type='str'),
      horizon     =dict(required=False, type='str'),
      external_fdb=dict(
        required=False,
        choices=['yes', 'no', 'auto'],
        type='str'
      ),
      auto_isolate=dict(
        required=False,
        choices=['yes', 'no'],
        type='str'
      ),
      edge=dict(
        required=False,
        choices=['auto', 'yes', 'no', 'no-discover', 'yes-discover'],
        type='str'
      ),
      point_to_point=dict(
        required=False,
        choices=['yes', 'no', 'auto'],
        type='str'
      ),
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
  ansible_bridge_port_interface  = module.params['interface']
  changed = False
  changed_message = []
  check_mode = module.check_mode
  msg = ""

  mk = mt_api.Mikrotik(hostname, username, password)
  try:
    mk.login()
  except:
    module.fail_json(
        msg="Could not log into Mikrotik device." +
        " Check the username and password.",
    )

  bridge_port_path = '/interface/bridge/port'

  response = mk.api_print(base_path=bridge_port_path)
  bridge_port_params = module.params
  mikrotik_bridge_port = {}
  for item in response:
    if 'interface' in item[1].keys():
      if ansible_bridge_port_interface == item[1]['interface']:
        mikrotik_bridge_port = item[1]

  #######################################
  # remove unneeded parameters
  ######################################

  remove_params = ['hostname', 'username', 'password', 'state']
  for i in remove_params:
    del bridge_port_params[i]

  ##########################################
  # modify clean_params in place
  ############################################
  clean_params(bridge_port_params)

  if '.id' in mikrotik_bridge_port:
    client_id = mikrotik_bridge_port['.id']
  else:
    client_id = False

  if state == "present":
    if mikrotik_bridge_port == {}:
      if not check_mode:
        mk.api_add(
            base_path=bridge_port_path,
            params=bridge_port_params
        )
      changed_message.append(ansible_bridge_port_interface + " added to bridge")
      changed = True,
    else:
      bridge_port_diff_keys = {}

      for key in bridge_port_params:
        if key in mikrotik_bridge_port:
          if bridge_port_params[key] != mikrotik_bridge_port[key]:
            bridge_port_diff_keys[key] = bridge_port_params[key]
        else:
          bridge_port_diff_keys[key] = bridge_port_params[key]
      if bridge_port_diff_keys != {}:
        bridge_port_diff_keys['numbers'] = client_id
        if not check_mode:
          mk.api_edit(base_path=bridge_port_path, params=bridge_port_diff_keys)
        changed = True
        changed_message.append("Changed bridge port: " + bridge_port_params['bridge'])
      else:
        ####################
        # Already up date
        ###################
        if not changed:
          changed = False

  elif state == "absent":
    if client_id:
      if not check_mode:
        mk.api_remove(base_path=bridge_port_path, remove_id=client_id)
      changed_message.append(bridge_port_params['interface'] + " removed")
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
