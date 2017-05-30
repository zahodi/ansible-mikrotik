DOCUMENTATION = '''
module: mt_ip_firewall
author:
  - "Valentin Gurmeza"
  - "Shaun Smiley"
version_added: "2.3"
short_description: Manage mikrotik /ip/firewall/
requirements:
  - mt_api
description:
  - Generic mikrotik firewall module
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
  rule:
    description:
      - a list containing dictionary parameters.
        action, chain, comment, and place-before keys are required
  parameter:
    description:
      - sub endpoint for mikrotik firewall
    required: True
    options:
      - filter
      - nat
      - mangle
  settings:
    description:
      - All Mikrotik compatible parameters for this particular endpoint.
        Any yes/no values must be enclosed in double quotes
      - if a firewall list containing dictionary parameters,
        action, chain, comment, and place-before keys are required
  state:
    description:
      - absent or present
  force:
    description:
      - True/False value to force remove the rule regardless of the position in the rule list.
'''

EXAMPLES = '''
- mt_ip_firewall:
    hostname:  "{{ inventory_hostname }}"
    username:  "{{ mt_user }}"
    password:  "{{ mt_pass }}"
    state:     present
    parameter: filter
    settings:
      action: accept
      chain: forward
      comment: controlled by ansible
      place-before: "2"
'''

from ansible.module_utils.basic import AnsibleModule
import mt_api
import re
from copy import copy


def main():

  module = AnsibleModule(
      argument_spec=dict(
          hostname  = dict(required=True),
          username  = dict(required=True),
          password  = dict(required=True),
          rule      = dict(required=False, type='dict'),
          parameter = dict(required=True, type='str'),
          state = dict(
              required  = False,
              default   = "present",
              choices   = ['present', 'absent'],
              type      = 'str'
          ),
      )
  )

  hostname     = module.params['hostname']
  username     = module.params['username']
  password     = module.params['password']
  rule = module.params['rule']
  state        = module.params['state']
  api_path     = '/ip/firewall/' + module.params['parameter']
# ##############################################
# Check if "place-before" is an integer
# #############################################
  try:
    desired_order = int(rule['place-before'])
  except:
    module.exit_json(
        failed=True,
        changed=False,
        msg="place-before is not set or is not set to an integer",
      )
  changed = False
  msg = ""

  mk = mt_api.Mikrotik(hostname, username, password)
  try:
    mk.login()
  except:
    module.fail_json(
        msg="Could not log into Mikrotik device." +
        " Check the username and password.",
    )

  filter_response = mk.api_print(api_path)
  current_rule = None
  current_id = None
  existing_order = None
  last_item = len(filter_response) - 2
  changed_msg = []

  # Always set the comment to the order_number
  if 'comment' in rule:
    rule['comment'] = str(desired_order) + " " + str(rule['comment'])
  else:
    rule['comment'] = str(desired_order)

  if desired_order <= last_item:
    placed_at_the_end = False
  else:
    placed_at_the_end = True
    # remove the place-before if we are placing
    # the rule at the bottom of the chain
    rule.pop('place-before', None)

  # Check rule is not present
  # find existing rule
  # current_rule is what's on mikrotik right now
  for index, current_param in enumerate(filter_response):
    if 'comment' in current_param[1]:
      if re.search(r"^" + str(desired_order) + "\s+", current_param[1]['comment']):
        current_id = current_param[1]['.id']
        existing_order = index
        current_rule = current_param[1]
        # remove the place-before since we'll be editing not moving it
        rule.pop('place-before', None)

  # ensure the rule if state is present
  if state == "present":
    # if we don't have an existing rule to match
    # the desired we create a new one
    if not current_rule:
      mk.api_add(api_path, rule)
      changed = True,
    # if current_rule is true we need to ensure the changes
    else:
      out_params = {}
      old_params = {}
      for desired_param in rule:
        rule[desired_param] = str(rule[desired_param])
        if desired_param in current_rule:
          if current_rule[desired_param] != rule[desired_param]:
            out_params[desired_param] = rule[desired_param]
            old_params[desired_param] = current_rule[desired_param]
        else:
          out_params[desired_param] = rule[desired_param]
          if desired_param in current_rule:
            old_params[desired_param] = current_rule[desired_param]

      # When out_params has been set it means we found our diff
      # and will set it on the mikrotik
      if out_params:
        if current_id is not None:
          out_params['.id'] = current_id

          mk.api_edit(
              base_path = api_path,
              params    = out_params
          )

          # we don't need to show the .id in the changed message
          if '.id' in out_params:
            del out_params['.id']
          changed = True

          changed_msg.append({
              "new_params": out_params,
              "old_params": old_params,
          })

    # ensure the rule is in right position
    if current_id:
      if int(existing_order) != int(desired_order):
        api_path += '/move'
        params = False
        if placed_at_the_end:
          if existing_order > last_item:
            params = {
            '.id': current_id,
            }
        else:
          params = {
          '.id': current_id,
          'destination': desired_order
          }
        if params:
          mk.api_command(api_path, params)
          changed_msg.append({
              "moved": existing_order,
              "to": old_params,
          })
          changed = True

#####################################
# Remove the rule
#####################################
  elif state == "absent":
    if current_rule:
      mk.api_remove(api_path, current_id)
      changed = True
      changed_msg.append("removed rule: " + str(desired_order))
  else:
    failed = True

  if changed:
    module.exit_json(
        failed=False,
        changed=True,
        msg=changed_msg
      )
  elif not changed:
    module.exit_json(
        failed=False,
        changed=False,
      )
  else:
    module.fail_json()

  ##########################################
  # To DO:
  # Clean up duplicate items
  ###########################################

if __name__ == '__main__':
  main()
