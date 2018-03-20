DOCUMENTATION = '''
module: mt_ip_address
author:
  - "Valentin Gurmeza"
  - "Shaun Smiley"
  - "Antoni Matamalas"
version_added: "2.3"
short_description: Manage mikrotik /ip/addresses
requirements:
  - mt_api
description:
  - Manage addresses on interfaces
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
  idempotent:
    description:
      - parameter that will define the behavior for the ip address status.
      - If "interface" is used, only one IP will be allowed per interface.
        The "state" parameter will define if the IP is added, edited or
        removed. No settings options are required to removed the IP from an
        interface
      - If "address" is used, and interface will be able to have multiple IPs,
        but address will only be added or removed. In order to change an IP, it
        will have to be first removed and then added to the interface in two
        tasks.
    required: False
    default: address
  settings:
    description:
      - All Mikrotik compatible parameters for this particular endpoint.
        Any yes/no values must be enclosed in double quotes
    required: True
  state:
    description:
      - Depending on the idempotent option, it will define the status of the IP
        on an interface
    required: False
    default: present
'''

EXAMPLES = '''
# Add IP to an interface with a comment. If the interface has already an IP it
# will add as a sencond IP
- mt_ip_address:
    hostname:   "{{ inventory_hostname }}"
    username:   "{{ mt_user }}"
    password:   "{{ mt_pass }}"
    idempotent: "address"
    state:      "present"
    settings:
      interface:  "ether2"
      address:    "192.168.88.2/24"
      network:    "192.168.88.0/24"
      comment:    "link 3"

# Assign IP to the interface. If the interface has any previous IP, it will be
# replaced by this one.
- mt_ip_address:
    hostname:   "{{ inventory_hostname }}"
    username:   "{{ mt_user }}"
    password:   "{{ mt_pass }}"
    idempotent: "interface"
    state:      "present"
    settings:
      interface:  "ether2"
      address:    "192.168.88.2/24"
      network:    "192.168.88.0/24"
      comment:    "link 3"

# Remove any IP from an interface
- mt_ip_address:
    hostname:   "{{ inventory_hostname }}"
    username:   "{{ mt_user }}"
    password:   "{{ mt_pass }}"
    idempotent: "interface"
    state:      "absent"
    settings:
      interface:  "ether2"
'''

from ansible.module_utils.mt_common import clean_params, MikrotikIdempotent
from ansible.module_utils.basic import AnsibleModule


def main():

  module = AnsibleModule(
      argument_spec=dict(
          hostname  = dict(required=True),
          username  = dict(required=True),
          password  = dict(required=True, no_log=True),
          settings  = dict(required=True, type='dict'),
          idempotent = dict(
              required  = False,
              default   = 'address',
              choices   = ['address', 'interface'],
              type      = 'str'
          ),
          state = dict(
              required  = False,
              default   = "present",
              choices   = ['present', 'absent'],
              type      = 'str'
          ),
      ),
      supports_check_mode=True
  )

  params = module.params
  mt_obj = MikrotikIdempotent(
    hostname         = params['hostname'],
    username         = params['username'],
    password         = params['password'],
    state            = params['state'],
    desired_params   = params['settings'],
    idempotent_param = params['idempotent'],
    api_path         = '/ip/address',
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
      #msg='',
      msg=params['settings'],
    )

if __name__ == '__main__':
  main()

