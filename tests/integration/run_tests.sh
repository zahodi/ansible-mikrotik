#!/usr/bin/env bash

ABSOLUTE_PATH="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
pushd .

cd "$ABSOLUTE_PATH"
ansible-playbook tests.yml --diff -i 127.0.0.1, $@

popd  >/dev/null
