#!/usr/bin/env bash

set -eov

export JOB_TARGET=${JOB_TARGET:-compute1-vm-5}


pushd ~/projects/ansible-virt-lab
  ~/bin/venvs/ansible/bin/ansible-playbook -i inventory-vms.yaml \
                                           -e @local_vars.yaml \
                                           -e tripleo_version_dev_enabled=yes \]
                                           -e vm_cleanup=yes \
                                           -e vm_job_target=${JOB_TARGET} \
                                           playbooks/vm-create.yml \
                                           playbooks/tripleo-standalone-deployment.yml \
                                           ${@:-"--limit '${JOB_TARGET}:compute1:localhost'"}
popd
