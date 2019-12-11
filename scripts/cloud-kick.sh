#!/usr/bin/env bash

## Shell Opts ----------------------------------------------------------------

set -o pipefail
set -eu

## Vars ----------------------------------------------------------------------

export PROJECT_DIR="$(dirname $(readlink -f ${BASH_SOURCE[0]}))/../"

export DEPLOY_NAME=${DEPLOY_NAME:-osp}
export DEPLOY_RELEASE=${DEPLOY_RELEASE:-rhosp15}

## Main ----------------------------------------------------------------------

echo -e "\nRunning with Deployment Name:  ${DEPLOY_NAME}"
echo -e "Running with Deployment Release: ${DEPLOY_RELEASE}\n"

rm -f ${HOME}/vm-${DEPLOY_NAME}-lab-inventory.yaml
rm -f ${HOME}/vm-${DEPLOY_NAME}-lab-instackenv.yaml

pushd ${PROJECT_DIR}
    source ansible-env-vars.rc
    ansible-playbook -i inventory-dsal.yaml \
                     -e @local_dsal_vars.yml \
                     -e vm_cleanup=yes \
                     -e instackenv_file=${HOME}/vm-${DEPLOY_NAME}-lab-instackenv.yaml \
                     --forks 150 \
                     --limit "${DEPLOY_NAME}*:localhost" \
                     ${PROJECT_DIR}/playbooks/vm-create.yml \
                     ${PROJECT_DIR}/playbooks/vm-vbmc-setup.yml
popd
