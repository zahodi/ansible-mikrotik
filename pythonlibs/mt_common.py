#!/usr/bin/env python
import mt_api
import re

      if 'policy' in ansible_scheduler_params:
        dif_list = []
        if 'policy' in mikrotik_scheduler_task:
          policy = mikrotik_scheduler_task['policy'].split(',')
          dif_list = set(ansible_scheduler_params['policy']) & set(policy)

        if dif_list == []:
          list_to_string = ""
          list_to_string = ','.join(map(str, ansible_scheduler_params['policy']))
          scheduler_diff_keys['policy'] = list_to_string

      for key in ansible_scheduler_params:
        if key != 'policy':
          if key in mikrotik_scheduler_task:
            if ansible_scheduler_params[key] != mikrotik_scheduler_task[key]:
              scheduler_diff_keys[key] = ansible_scheduler_params[key]
          else:
            scheduler_diff_keys[key] = ansible_scheduler_params[key]
      if scheduler_diff_keys != {}:
        scheduler_diff_keys['numbers'] = client_id
        if not check_mode:
          mk.api_edit(base_path=api_path, params=scheduler_diff_keys)
        changed = True
        changed_message.append(
          "Changed scheduler task : " + ansible_scheduler_params['name']
        )


def list_string(ansible_list, mikrotik_string):
  list_to_string = ""
  list_to_string = ','.join(map(str, ansible_scheduler_params['policy']))
  scheduler_diff_keys['policy'] = list_to_string


def clean_params(params):
  '''
  remove keys with empty values
  modify keys with '_' to match mikrotik parameters
  convert yes/no to true/false
  '''
  if isinstance(params, dict):
    for key in list(params):
      if params[key] is None:
        del params[key]
        continue

      new_key = re.sub('_', '-', key)
      if new_key != key:
        params[new_key] = str(params[key])
        del params[key]
        continue

      if params[key] == "yes":
        params[key] = "true"
      if params[key] == "no":
        params[key] = "false"
  else:
    print("Must be a dictionary")


class MikrotikIdempotent():
  '''
  MikrotikIdempotent Class
    - A helper class for Ansible modules to abstract common functions.

  Example Usage:
    mt_obj = MikrotikIdempotent(
      hostname        = params['hostname'],
      username        = params['username'],
      password        = params['password'],
      state           = None,
      desired_params  = params['settings'],
      idempotent_param= 'name',
      api_path        = '/interface/ethernet',
    )

    mt_obj.sync_state()
  '''

  def __init__(
   self, hostname, username, password, desired_params, api_path,
   state, idempotent_param, check_mode=False):

    self.hostname         = hostname
    self.username         = username
    self.password         = password
    self.state            = state
    self.desired_params   = desired_params
    self.idempotent_param = idempotent_param
    self.current_params   = {}
    self.api_path         = api_path
    self.check_mode       = check_mode

    self.login_success    = False
    self.changed          = False
    self.changed_msg      = []
    self.failed           = False
    self.failed_msg       = []

    self.login()

  def login(self):
    self.mk = mt_api.Mikrotik(
      self.hostname,
      self.username,
      self.password,
    )

    try:
      self.mk.login()
      self.login_success = True
    except:
      self.failed_msg = "Could not log into Mikrotik device." + " Check the username and password.",

  def get_current_params(self):
    clean_params(self.desired_params)
    self.param_id = None
    self.current_param = None
    self.current_params = self.mk.api_print(base_path=self.api_path)

    # When state and idempotent_param is None we are working
    # on editable params only and we are grabbing the only item from response
    if self.state is None and self.idempotent_param is None:
      self.current_param = self.current_params[0][1]

    # Else we iterate over every item in the list until we find the matching
    # params
    # We also set the param_id here to reference later for editing or removal
    else:
      for current_param in self.current_params:
        if self.idempotent_param in current_param[1]:
          if self.desired_params[self.idempotent_param] == current_param[1][self.idempotent_param]:
            self.current_param = current_param[1]
            self.param_id = current_param[1]['.id']
            # current_param now is a dict, something like:
            # {
            #    ".id": "*1",
            #    "full-duplex": "true",
            #    "mac-address": "08:00:27:6F:4C:22",
            #    "mtu": "1500",
            #    "name": "ether1",
            #    ...
            # }

  def add(self):
    # When current_param is empty we need to call api_add method to add
    # all the parameters in the desired_params
    if self.current_param is None:
      self.new_params = self.desired_params
      self.old_params = ""
      if not self.check_mode:
          self.mk.api_add(
              base_path = self.api_path,
              params    = self.desired_params,
          )
      self.changed = True

    # Else we need to determing what the difference between the currently
    # and the desired
    else:
      self.edit()

  def rem(self):
    # if param_id is set this means there is currently a matching item
    # which we will remove
    if self.param_id:
      self.new_params = "item removed"
      self.old_params = self.desired_params
      if not self.check_mode:
        self.mk.api_remove(
            base_path=self.api_path,
            remove_id=self.param_id,
        )
      self.changed = True

  def edit(self):
    out_params = {}
    old_params = {} #used to store values of params we change

    # iterate over items in desired params and match against items in current_param
    # to figure out the difference
    for desired_param in self.desired_params:
      self.desired_params[desired_param] = str(self.desired_params[desired_param])
      if desired_param in self.current_param:
        if self.current_param[desired_param] != self.desired_params[desired_param]:
          out_params[desired_param] = self.desired_params[desired_param]
          old_params[desired_param] = self.current_param[desired_param]
      else:
        out_params[desired_param] = self.desired_params[desired_param]
        if desired_param in self.current_param:
          old_params[desired_param] = self.current_param[desired_param]

    # When out_params has been set it means we found our diff
    # and will set it on the mikrotik
    if out_params:
      if self.param_id is not None:
        out_params['.id'] = self.current_param['.id']

      if not self.check_mode:
        self.mk.api_edit(
            base_path = self.api_path,
            params    = out_params,
        )

      # we don't need to show the .id in the changed message
      if '.id' in out_params:
        del out_params['.id']

      self.changed_msg.append({
          "new_params":   out_params,
          "old_params":   old_params,
      })

      self.new_params = out_params
      self.old_params = old_params
      self.changed = True

  def sync_state(self):
    self.get_current_params()

    # When state and idempotent_param are not set we are working
    # on editable parameters only that we can't add or remove
    if self.state is None and self.idempotent_param is None:
      self.edit()
    elif self.state == "absent":
      self.rem()
    elif self.state == "present" or self.idempotent_param:
      self.add()
