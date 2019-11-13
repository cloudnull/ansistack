#!/usr/bin/env bash

## Shell Opts ----------------------------------------------------------------

set -o pipefail
set -eu

## Vars ----------------------------------------------------------------------

export PROJECT_DIR="$(dirname $(readlink -f ${BASH_SOURCE[0]}))/../"

## Main ----------------------------------------------------------------------

pushd ${PROJECT_DIR}
    source ansible-env-vars.rc
    ansible-playbook -i inventory-vms.yaml \
                     -e @local_vars.yaml \
                     -e tripleo_version_dev_enabled=yes \]
                     -e vm_cleanup=yes \
                     playbooks/vm-create.yml \
                     ${@}
popd
