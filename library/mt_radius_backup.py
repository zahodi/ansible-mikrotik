# -*- coding: utf-8 -*-
DOCUMENTATION = '''
module: mt_radius
author:
  - "Valentin Gurmeza"
  - "Shaun Smiley"
version_added: "2.3"
short_description: Manage mikrotik radius client
requirements:
  - mt_api
description:
  - Add or remove a radius client
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
      - client present or absent
    required: True
    choices:
      - present
      - absent
  comment:
    description:
      - This module only ensures entries that match the comment field.
        Thus, you should make unique comments for every entry.
    required: True # only if state is present
  address:
    description:
      - IPv4 or IPv6 address of RADIUS server
    required: False
  secret:
    description:
      - Shared secret used to access the RADIUS server
     required: False
     default: null
  timeout:
    description:
      - Timeout after which the request should be resend
    required: False
     default: null
  service:
    description:
      - Router services that will use this RADIUS server:
    choices:
      - 'hotspot' # HotSpot authentication service
      - 'login'   # router's local user authentication
      - 'ppp      # Point-to-Point clients authentication
      - 'wireless # wireless client authentication (client's MAC address is sent as User-Name)
      - 'dhcp     # DHCP protocol client authentication (client's MAC address is sent as User-Name)IPv4 or IPv6 address of RADIUS server
    required: False
    default: null
  incoming:
    accept:
      choices: ['true', 'false' ]
    port: "3799"
    description:
      - Whether to accept the unsolicited messages.
        Also include the port number to listen for the requests on.
        Accept and port values must be strings
    required: False
    default: null
'''

EXAMPLES = '''
# Add a new radius entry
- mt_radius:
    hostname:      "{{ inventory_hostname }}"
    username:      "{{ mt_user }}"
    password:      "{{ mt_pass }}"
    state:         present
    address:       192.168.230.1
    comment:       ansible_test
    secret:       'password'
    service:
      - login
      - hotspot
      - wireless
    timeout:        '2s500ms'
'''

from ansible.module_utils import mt_api
from ansible.module_utils.basic import AnsibleModule


def main():
  module = AnsibleModule(
    argument_spec=dict(
      hostname= dict(required=True),
      username= dict(required=True),
      password= dict(required=True),
      address = dict(required=False, type='str'),
      comment = dict(required=True, type='str'),
      secret  = dict(required=False, type='str'),
      service = dict(required=False, type='list'),
      timeout = dict(required=False, type='str'),
      incoming= dict(required=False, type='dict'),
      state   = dict(
        required  = True,
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
  check_mode   = module.check_mode
  changed      = False
  msg = ""

  radius_path = '/radius'
  mk = mt_api.Mikrotik(hostname, username, password)
  try:
    mk.login()
  except:
    module.fail_json(
        msg="Could not log into Mikrotik device." +
        " Check the username and password.",
    )

  response = mk.api_print(radius_path)
  radius_params = module.params

  ########################################################
  # Check if we need to edit the incoming radius settings
  ########################################################
  if radius_params['incoming'] is not None:
    incoming_path = '/radius/incoming'
    incoming_response = mk.api_print(incoming_path)
    incoming = radius_params['incoming']
    if incoming_response[0][1]['accept'] == incoming['accept']:
      if incoming_response[0][1]['port'] == incoming['port']:
        # nothing to do
        pass
      else:
        # edit port
        if not check_mode:
          mk.api_edit(base_path=incoming_path, params=incoming)
    else:
      # edit the accept and the port
      if not check_mode:
        mk.api_edit(base_path=incoming_path, params=incoming)
  #######################################
  # Since we are grabbing all the parameters passed by the module
  # We need to remove the one that won't be used
  # as mikrotik parameters
  remove_params = ['hostname', 'username', 'password', 'state', 'incoming']
  for i in remove_params:
    radius_params.pop(i)
  #######################################
  # remove keys with empty values
  # convert service list to stings
  ######################################
  for key in radius_params.keys():
    if radius_params[key] is None:
      radius_params.pop(key)


  #################################################
  # Convert service list to comma separated string
  #################################################
  list_to_string = ""
  if 'service' in radius_params:
    list_to_string = ','.join(map(str, radius_params['service']))
    radius_params['service'] = list_to_string

  ################################################
  # mikrotik_radius is the dictionary with the parameters
  # we get from mikrotik
  #################################
  # We grab the first radius item to
  # match the comment
  #################################
  mikrotik_radius = {}
  for i in response:
    if 'comment' in i[1]:
      if i[1]['comment'] == radius_params['comment']:
         mikrotik_radius = i[1]
         break

  ##########################################################
  # Define radius_id to be used by remove and edit function
  ##########################################################
  if '.id' in mikrotik_radius:
    radius_id = mikrotik_radius['.id']
  else:
    radius_id = False

  ######################################################
  # If the state is present and we can't find matching
  # radius comment we add a new item with all the parameters
  # from Ansible
  #######################################################
  if state == "present":
    if mikrotik_radius == {}:
      if not check_mode:
        mk.api_add(base_path=radius_path, params=radius_params)
      module.exit_json(
          failed=False,
          changed=True,
          msg="Added radius item",
      )
    ###################################################
    # If an item exists we check if all the parameters
    # match what we have in ansible
    ######################################
    else:
      radius_diff_keys = {}
      for key in radius_params:
        if radius_params[key] != mikrotik_radius[key]:
          radius_diff_keys[key] = radius_params[key]
      if radius_diff_keys != {}:
        radius_diff_keys['numbers'] = radius_id
        if not check_mode:
          mk.api_edit(base_path=radius_path, params=radius_diff_keys)
        module.exit_json(
            failed=False,
            changed=True,
            msg="Changed radius item: " + radius_params['comment']
        )
      else:
        ####################
        # Already up date
        module.exit_json(
            failed=False,
            changed=False,
        )
  elif state == "absent":
    if radius_id:
      if not check_mode:
        mk.api_remove(base_path=radius_path, remove_id=radius_id)
      module.exit_json(
          failed=False,
          changed=True,
          msg=radius_params['comment'] + " removed"
      )
    #####################################################
    # if radius_id is not set there is nothing to remove
    #####################################################
    else:
      module.exit_json(
          failed=False,
          changed=False,
      )
  else:
    module.exit_json(
        failed=True,
        changed=False,
    )
if __name__ == '__main__':
  main()
