#!/usr/bin/env python3
from ansible.module_utils import mt_api

class MikrotikConnection():
  '''This will be a connection class

  '''
  def __init__():
    self.hostname = "localhost"
    self.username = "admin"
    self.password = ""

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
