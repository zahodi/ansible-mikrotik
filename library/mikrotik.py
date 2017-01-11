#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Valentin Gurmeza'
__version__ = "0.1.1"

DOCUMENTATION = '''
module = mikrotik
'''


class MikrotikModule():
    def __init__(self, module):
        self.module = module
        # Variables
        # Init attributes
        #   Get Key name 1st from params if not check env variable
        self.user_name = self.module.params["user_name"]
        self.ip_addr = self.module.params["ip_addr"]
        self.password = self.module.params["password"]
        # self.name = self.module.params["name"]
        # self.time_out = self.module.params["time_out"]
        self.fail_on_warning = self.module.params["fail_on_warning"]

def main():
    module = AnsibleModule(
        argument_spec=dict(
            password=dict(default=None),
            user_name=dict(default=None),
            ip_addr=dict(default=None),
            # tags=dict(default=None, type="dict"),
            # fail_on_warning=dict(default=True, choices=BOOLEANS, type="bool"),
            # fire_forget=dict(default=True, choices=BOOLEANS, type="bool"),
            # time_out=dict(default=500, typ="int"),
        ),
        supports_check_mode=True
    )
    if not rosapi_found:
            module.fail_json(msg="The ansible mikrotik module requires rosapi library. use 'pip install rosapi' ")

try:
    import rosapi
except ImportError:
    rosapi_found = False
else:
    rosapi_found = True
    MikrotikModule(module).main()

from ansible.module_utils.basic import AnsibleModule
main()
