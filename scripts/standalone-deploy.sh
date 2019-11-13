#!/usr/bin/env bash

## Shell Opts ----------------------------------------------------------------

set -o pipefail
set -eu

## Vars ----------------------------------------------------------------------

export PROJECT_DIR="$(dirname $(readlink -f ${BASH_SOURCE[0]}))/../"

export JOB_TARGET=${JOB_TARGET:-compute1-vm-5}

## Main ----------------------------------------------------------------------

pushd ${PROJECT_DIR}
    source ansible-env-vars.rc
    ansible-playbook -i inventory-vms.yaml \
                     -e @local_vars.yaml \
                     -e tripleo_version_dev_enabled=yes \]
                     -e vm_cleanup=yes \
                     -e vm_job_target=${JOB_TARGET} \
                     playbooks/vm-create.yml \
                     playbooks/tripleo-standalone-deployment.yml \
                     ${@:-"--limit '${JOB_TARGET}:compute1:localhost'"}
popd
