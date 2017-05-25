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
  rule:
    description:
      - a list containing dictionary parameters.
        action, chain, comment, and place-before keys are required
  force:
    description:
      - True/False value to force remove the rule regardless of the position in the rule list.
'''

EXAMPLES = '''
- mt_ip_firewall_filter:
    hostname:   "{{ inventory_hostname }}"
    username:   "{{ mt_user }}"
    password:   "{{ mt_pass }}"
    rule:
      action: accept
      chain: forward
      comment: controlled by ansible
      place-before: "2"
'''

import mt_api

from ansible.module_utils.basic import AnsibleModule


def main():

  module = AnsibleModule(
      argument_spec=dict(
          hostname  = dict(required=True),
          username  = dict(required=True),
          password  = dict(required=True),
          rule      = dict(required=False, type='dict'),
          state = dict(
              required  = False,
              default   = "present",
              choices   = ['present', 'absent'],
              type      = 'str'
          ),
      )
  )

  hostname    = module.params['hostname']
  username    = module.params['username']
  password    = module.params['password']
  rule        = module.params['rule']
  rule_state  = module.params['state']
  changed = False
  msg = ""

  filter_path = '/ip/firewall/filter'
  mk = mt_api.Mikrotik(hostname, username, password)
  try:
    mk.login()
  except:
    module.fail_json(
        msg="Could not log into Mikrotik device." +
        " Check the username and password.",
    )

# ##############################################
# Check if "place-before" is an integer
# #############################################
  try:
    placement = int(rule['place-before'])
    if isinstance(placement, int):
      pass
  except:
      module.exit_json(
          failed=True,
          changed=False,
          msg="place-before is not set or is not set to an integer",
      )
#######################################################
# Construct the fluff to ignore the extras from mikrotik response
########################################################
  if "log" not in rule:
   rule['log'] = "false"
  if "log-prefix" not in rule:
    rule['log-prefix'] = ""
  fluff = (
      "bytes",
      "disabled",
      "invalid",
      "packets",
      "dynamic",
      "invalid",
      ".id",
  )

###################################
# Check if rule is present
# exit if rule is not present
###################################

  filter_response = mk.api_print(filter_path)
  last_item = len(filter_response) - 2
  order_number = int(rule['place-before'])
  if order_number <= last_item:
    clean_response = filter_response[order_number][1]
    clean_response['place-before'] = rule['place-before']
    placed_at_the_end = False
    remove_id = clean_response['.id']
    for f in fluff:
      clean_response.pop(f, None)
  else:
    placed_at_the_end = True
  if rule_state == "present":
    if placed_at_the_end is False:
      if rule == clean_response:
        module.exit_json(
            failed=False,
            changed=False,
        )
################################
# add the rule
##################################
      else:
        mk.api_remove(filter_path, remove_id)
        mk.api_add(filter_path, rule)
        module.exit_json(
            failed=False,
            changed=True,
        )
    else:
      rule.pop('place-before', None)
      mk.api_add(filter_path, rule)
      module.exit_json(
          failed=False,
          changed=True,
      )
#####################################
# Remove the rule
#####################################
  elif rule_state == "absent":
    if placed_at_the_end:
      module.exit_json(
          failed=False,
          changed=False
      )
    else:
      if rule == clean_response:
        mk.api_remove(filter_path, remove_id)
        module.exit_json(
            failed=False,
            changed=True
        )
      else:
        module.exit_json(
            failed=False,
            changed=False
        )


if __name__ == '__main__':
  main()
