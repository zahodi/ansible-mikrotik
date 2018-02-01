#!/usr/bin/env python
from ansible.module_utils.basic import env_fallback
from ansible.module_utils.six import iteritems
from __future__ import absolute_import, division, print_function
from ansible.module_utils import mt_api

__metaclass__ = type


routeros_provider_spec = {
    'host': dict(),
    'port': dict(type='int'),

    'username': dict(fallback=(env_fallback, ['ANSIBLE_NET_USERNAME'])),
    'password': dict(fallback=(env_fallback, ['ANSIBLE_NET_PASSWORD']), no_log=True),
    'ssh_keyfile': dict(fallback=(env_fallback, ['ANSIBLE_NET_SSH_KEYFILE']), type='path'),

    'use_ssl': dict(type='bool'),
    'validate_certs': dict(type='bool'),

    'timeout': dict(type='int'),

    'transport': dict(default='api', choices=['cli', 'api'])
}


def load_params(module):
    provider = module.params.get('provider') or dict()
    for key, value in iteritems(provider):
        if key in routeros_provider_spec:
            if module.params.get(key) is None and value is not None:
                module.params[key] = value

_DEVICE_CONNECTION = None


def get_connection(module):
    # pylint: disable=global-statement
    global _DEVICE_CONNECTION
    if not _DEVICE_CONNECTION:
        load_params(module)
        conn = Api(module)
        _DEVICE_CONNECTION = conn
    return _DEVICE_CONNECTION


class Api:
    def __init__(self, module):
        self._module = module

        username = self._module.params['username']
        password = self._module.params['password']

        host = self._module.params['host']
        port = self._module.params['port']

        timeout = self._module.params['timeout']

        self._api = mt_api.Mikrotik(
            host,
            username,
            password
        )
