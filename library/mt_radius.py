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
  username:
    description:
      - username used to connect to mikrotik router
  password:
    description:
      - password used for authentication to mikrotik router
  state:
    description:
      - client present or absent
    required: False
    choices:
      - present
      - absent
'''

EXAMPLES = '''
# Add a new radius entry
- mt_radius:
    hostname:    "{{ inventory_hostname }}"
    username:    "{{ mt_user }}"
    password:    "{{ mt_pass }}"
    state:         present
    parameter: radius
    settings:
      address: 192.168.230.1
      comment: ansible_test
      timeout: '2s500ms'
      secret:  'password'
      service:
        - login
        - hotspot
        - wireless
'''

from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.mt_common import MikrotikIdempotent


def main():
    module = AnsibleModule(
        argument_spec = dict(
            hostname  = dict(required=True),
            username  = dict(required=True),
            password  = dict(required=True),
            settings  = dict(required=False, type='dict'),
            parameter = dict(
                required  = True,
                choices   = ['radius', 'incoming'],
                type      = 'str'
            ),
            state   = dict(
                required  = False,
                choices   = ['present', 'absent'],
                type      = 'str'
            ),
        ),
    supports_check_mode=True
    )

    idempotent_parameter = None
    params = module.params

    if params['parameter'] == 'radius':
      idempotent_parameter = 'comment'
      params['parameter'] = "/radius"

    if params['parameter'] == 'incoming':
      params['parameter'] = "/radius/incoming"


    mt_obj = MikrotikIdempotent(
        hostname         = params['hostname'],
        username         = params['username'],
        password         = params['password'],
        state            = params['state'],
        desired_params   = params['settings'],
        idempotent_param = idempotent_parameter,
        api_path         = str(params['parameter']),
        check_mode       = module.check_mode,

    )

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
