#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Copyright (c) 2017 Sam Edwards
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

from __future__ import absolute_import, division, print_function
__metaclass__ = type

import sys
import copy

# pylint: disable=no-member
from ansible import constants as C
from ansible.plugins.action.normal import ActionModule as _ActionModule
from ansible.module_utils.basic import AnsibleFallbackNotFound
from ansible.module_utils.six import iteritems
from routeros_utils import routeros_argument_spec

try:
    from __main__ import display
except ImportError:
    from ansible.utils.display import Display
    display = Display()


class ActionModule(_ActionModule):

    def run(self, tmp=None, task_vars=None):
        provider = self.load_provider()
        transport = provider['transport'] or 'cli'

        if self._play_context.connection != 'local' and transport == 'cli':
            return dict(
                failed=True,
                msg='invalid connection specified, expected connection=local, '
                    'got %s' % self._play_context.connection
            )

        display.vvvv('connection transport is %s' % transport, self._play_context.remote_addr)

        if transport == 'cli':
            pc = copy.deepcopy(self._play_context)
            pc.connection = 'network_cli'
            pc.network_os = 'routeros'
            pc.remote_addr = provider['host'] or self._play_context.remote_addr
            pc.port = int(provider['port'] or self._play_context.port or 22)
            pc.remote_user = provider['username'] or self._play_context.connection_user
            pc.password = provider['password'] or self._play_context.password
            pc.private_key_file = provider['ssh_keyfile'] or self._play_context.private_key_file
            pc.timeout = int(provider['timeout'] or C.PERSISTENT_COMMAND_TIMEOUT)
            display.vvv('using connection plugin %s' % pc.connection, pc.remote_addr)

            # RouterOS allows colors, terminal detection ANSI sequences, etc.
            # to be turned off in a weird way: appending flags to the username
            pc.remote_user += '+cet'

            connection = self._shared_loader_obj.connection_loader.get('persistent', pc, sys.stdin)

            socket_path = connection.run()
            display.vvvv('socket_path: %s' % socket_path, pc.remote_addr)
            if not socket_path:
                # pylint: disable=line-too-long
                return {'failed': True,
                        'msg': 'unable to open shell. Please see: ' +
                               'https://docs.ansible.com/ansible/network_debug_troubleshooting.html#unable-to-open-shell'}

            # make sure we are in the right cli context which should be
            # enable mode and not config module
            rc, out, err = connection.exec_command('prompt()')
            while str(out).strip().endswith(')#'):
                display.vvvv('wrong context, sending exit to device',
                             self._play_context.remote_addr)
                connection.exec_command('exit')
                rc, out, err = connection.exec_command('prompt()')

            task_vars['ansible_socket'] = socket_path

        else:
            provider['transport'] = 'api'
            if provider.get('host') is None:
                provider['host'] = self._play_context.remote_addr

            if provider.get('port') is None:
                if provider.get('use_ssl'):
                    provider['port'] = 8729
                else:
                    provider['port'] = 8728

            if provider.get('timeout') is None:
                provider['timeout'] = C.PERSISTENT_COMMAND_TIMEOUT

            if provider.get('username') is None:
                provider['username'] = self._play_context.connection_user

            if provider.get('password') is None:
                provider['password'] = self._play_context.password

            if provider.get('use_ssl') is None:
                provider['use_ssl'] = False

            if provider.get('validate_certs') is None:
                provider['validate_certs'] = True

            self._task.args['provider'] = provider

        result = super(ActionModule, self).run(tmp, task_vars)
        return result

    def load_provider(self):
        provider = self._task.args.get('provider', {})
        for key, value in iteritems(routeros_argument_spec):
            if key != 'provider' and key not in provider:
                if key in self._task.args:
                    provider[key] = self._task.args[key]
                elif 'fallback' in value:
                    provider[key] = self._fallback(value['fallback'])
                elif key not in provider:
                    provider[key] = None
        return provider

    def _fallback(self, fallback):
        strategy = fallback[0]
        args = []
        kwargs = {}

        for item in fallback[1:]:
            if isinstance(item, dict):
                kwargs = item
            else:
                args = item
        try:
            return strategy(*args, **kwargs)
        except AnsibleFallbackNotFound:
            pass
