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
  settings:
    description:
      - All Mikrotik compatible parameters for this particular endpoint.
        Any yes/no values must be enclosed in double quotes
    required: True
  state:
    description:
      - absent or present
'''

EXAMPLES = '''
- mt_ip_address:
    hostname:   "{{ inventory_hostname }}"
    username:   "{{ mt_user }}"
    password:   "{{ mt_pass }}"
    settings:
      interface:  "ether2"
      address:    "192.168.88.2/24"
      network:    "192.168.88.0/24"
      state:      "present"
      comment:    "link 3"
'''

from ansible.module_utils.mt_common import clean_params, MikrotikIdempotent
from ansible.module_utils.basic import AnsibleModule


def main():

  module = AnsibleModule(
      argument_spec=dict(
          hostname  = dict(required=True),
          username  = dict(required=True),
          password  = dict(required=True, no_log=True),
          settings  = dict(required=False, type='dict'),
          state = dict(
              required  = False,
              default   = "present",
              choices   = ['present', 'absent'],
              type      = 'str'
          ),
      ),
      supports_check_mode=True
  )

  idempotent_parameter = None
  params = module.params
  idempotent_parameter = 'interface'
  mt_obj = MikrotikIdempotent(
    hostname         = params['hostname'],
    username         = params['username'],
    password         = params['password'],
    state            = params['state'],
    desired_params   = params['settings'],
    idempotent_param = idempotent_parameter,
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

