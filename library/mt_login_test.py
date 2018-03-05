#! /usr/bin/python
import socket
from ansible.module_utils import mt_api

from ansible.module_utils.basic import AnsibleModule


def main():

  module = AnsibleModule(
    argument_spec=dict(
      hostname=dict(required=True),
      username=dict(required=True),
      password=dict(required=True, no_log=True),
      )
    )

  hostname = module.params['hostname']
  username = module.params['username']
  password = module.params['password']
  changed = False
  msg = ""

  mk = mt_api.Mikrotik(hostname,username,password)
  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  result = sock.connect_ex((hostname, 8728))
  if result == 0:
    try:
      mk.login()
    except:
      module.fail_json(
        msg="Could not log into Mikrotik device.  Check the username and password."
      )
  else:
      module.fail_json(
        msg="Could not access RouterOS api." + " Verify API service is enabled and not blocked by firewall."
      )


  # response = apiros.talk([b'/ip/address/add', b'=address=192.168.15.2/24', b'=interface=ether7'])
  module.exit_json(
    changed=False,
    failed=False,
  )

if __name__ == '__main__':
  main()
