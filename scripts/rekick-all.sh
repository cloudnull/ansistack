#!/usr/bin/env bash

set -eov

pushd ~/projects/ansible-virt-lab
  ~/bin/venvs/ansible/bin/ansible-playbook -i inventory-vms.yaml \
                                           -e @local_vars.yaml \
                                           -e tripleo_version_dev_enabled=yes \]
                                           -e vm_cleanup=yes \
                                           playbooks/vm-create.yml \
                                           ${@}
popd
