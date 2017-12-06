DOCUMENTATION = '''
module: mt_ip_address
author:
  - "Valentin Gurmeza"
  - "Shaun Smiley"
version_added: "2.3"
short_description: Manage mikrotik /ip/addresses
requirements:
  - rosapi
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
  interface:
    description:
      -
  address:
    description:
      -
  network:
    description:
      -
  state:
    description:
      -
  force:
    description:
      - True/False value to force removing the address on an interface
        even if the address does not match.
'''

EXAMPLES = '''
- mt_ip_address:
    hostname:   "{{ inventory_hostname }}"
    username:   "{{ mt_user }}"
    password:   "{{ mt_pass }}"
    interface:  "ether2"
    address:    "192.168.88.2/24"
    network:    "192.168.88.0/24"
    state:      "present"
    comment:    "link 3"
'''

from ansible.module_utils import mt_api
import socket

#import mt_action #TODO: get this working

from ansible.module_utils.basic import AnsibleModule


def main():

  module = AnsibleModule(
      argument_spec=dict(
          hostname  = dict(required=True),
          username  = dict(required=True),
          password  = dict(required=True),
          interface = dict(required=True,  type='str'),
          address   = dict(required=True,  type='str', aliases=['ip', 'addr', 'ip_address']),
          network   = dict(required=False, type='str', default=""),
          comment   = dict(required=False, type='str', default=""),
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
  ip_address  = module.params['address']
  interface   = module.params['interface']
  network     = module.params['network']
  ip_state    = module.params['state']
  comment     = module.params['comment']
  changed = False
  msg = ""

  interface_path = '/interface'
  address_path = '/ip/address'
  address_print_params = {
    ".proplist": "interface,address,.id,network,netmask,comment"
  }
  interface_print_params = {
    ".proplist": "name,.id,type"
  }
  mk = mt_api.Mikrotik(hostname,username,password)
  try:
    mk.login()
    interfaces = mk.api_print(interface_path, interface_print_params)
  except:
    module.fail_json(
        msg="Could not log into Mikrotik device." +
        " Check the username and password.",
    )

  ###################################
  # Check if interface is present
  # exit if interface is not present
  ###################################
  interfacelist = []
  exitmessage = []
  for i in range(0, len(interfaces) - 1):
    interfacelist.append(interfaces[i][1]["name"])
  intExists = False

  if (interface in interfacelist):
    intExists = True
    # module.exit_json(failed=False, changed=False, msg=interfacelist)
  if intExists:
    pass
    #exitmessage.append("Interface " + interface + " exists.") #this is never used
  else:
    exitmessage.append("Interface " + interface + " does not exist.")
    module.fail_json(failed=True, msg=exitmessage)

  ##############################################
  # Check if IP address is set on the interface
  # make no changes if address already set
  ##############################################
  ip_addresses = mk.api_print(address_path, address_print_params)

  iplist = []
  for i in range(0, len(ip_addresses) - 1):
    iplist.append(ip_addresses[i][1]["address"])
    if ip_addresses[i][1]["address"] == ip_address:
      ip_id = ip_addresses[i][1][".id"]

  if ip_state == "present":
    if ip_address in iplist:
      module.exit_json(
          failed=False,
          #msg="IP Address: " + ip_address +
          #" is already configured" +
          #" on interface " + interface,
      )

    else:
      add_dict = {
          'address': ip_address,
          'interface': interface,
          'comment': comment
      }
      response = mk.api_add(address_path, add_dict)
      module.exit_json(
          failed=False,
          changed=True,
          #msg="IP address: " + ip_address + " has been configured" +
          #" on interface " + interface
      )

  if ip_state == "absent":
    if ip_address in iplist:
      response = mk.api_remove(address_path, ip_id)
      module.exit_json(
          failed=False,
          changed=True,
          #msg="IP Address: " + ip_address +
          #" has been removed"
      )

    else:
      module.exit_json(
          failed=False,
          changed=False,
          #msg="IP Address: " + ip_address +
          #" is already absent"
      )

if __name__ == '__main__':
  main()
