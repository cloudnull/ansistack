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

pushd ${PROJECT_DIR}
    source ansible-env-vars.rc
    ansible-playbook -i ~/vm-${DEPLOY_NAME}-lab-inventory.yaml \
                     -e @local_dsal_vars.yml \
                     -e redhat_osp_release=${DEPLOY_RELEASE} \
                     -e instackenv_file=${HOME}/vm-${DEPLOY_NAME}-lab-instackenv.yaml \
                     ${PROJECT_DIR}/playbooks/osp-vm-setup.yml \
                     ${PROJECT_DIR}/playbooks/osp-deploy.yml
popd
