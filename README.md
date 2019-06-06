# Virt Lab Setup and VM Deployment

This repository contains playbooks which may be useful when setting cloud
deployments using Virtual Machines. While this is geared toward lab
deployments there's nothing stopping these tools from being used in
production.

## Virtual Server Setup

TBD

## TripleO Standalone Deployment

Standalone deployments are simple test driven deployments that rapidly
deploys an run the overcloud on a single node. This playbook assumes
raw VMs have already been created using the `vm-create.yml` playbook.

To run the standalone deployment capability two arguments are required;
`vm_job_target` and `vm_job_user`. These arguments denote the node
name where the deployment will be executed, and the username used to
login to the target node.

``` shell
ansible-playbook -i inventory-vms.yaml \
                 playbooks/tripleo-standalone-deployment.yml \
                 -e vm_job_target=raw-vm-3 \
                 -e vm_job_user=centos
```

Other options exist which can aide in deployment setup and
troubleshooting, common options to include in the playbook run are
`tripleo_version_dev_enabled` and `tripleo_ceph_enabled`.

* `tripleo_version_dev_enabled` is a Boolean option which enables or disable
  developer mode, which sets the tripleo repos to use the latest development
  packages. If this option is set to **false** the option `tripleo_version`
  can be used to set the desired deployment version.
* `tripleo_ceph_enabled` is a Boolean option which will setup standalone
  ceph within the deployment.

## TripleO Undercloud Deployment

TBD

## TripleO Overcloud Deployment

TBD

## Run package upgrades

The `server-update.yaml` playbook will run package upgrades across the
**all_hosts** group and uses the package module to ensure it equally
supports most modern GNU/Linux distros.

## Creating Virtual Machines

###### Assumptions

* VirtualBMC is already be installed and ready for use when using the
  `osp_vms` group.
* The `virt-install` command is available on the `vm_virt_host` system.

###### Usage

Two different VM types can be deployed using this `vm-create.yml` playbook,
raw and osp.

* raw vms are virtual machines that are deployed using a cloud image and
  DHCP. Think of this as a light weight nested virtualization solution
  suitable for most applications. The instance will be setup with cloud-init
  and networking defaults to DHCP.

* osp vms are virtual machines that are deployed for the sole purpose of
  being enrolled into an undercloud using VirtualBMC. No configuration or
  operating system will be deployed when using the osp vm type.

> an example inventory **(vm-inventory.yaml)** can be seen in the root of this
repository.

Once the inventory is setup run the `vm-create.yml` playbook to build virtual
machines which have no operating system installed and are connected to
VirtualBMC for ipmi control.

``` shell
ansible-playbook -i vm-inventory.yaml playbooks/vm-create.yml
```

###### This playbook requires two networks to be enabled within libvirt

* provisioning
* external

How these networks are created is totally open-ended, they simply musst exist
and allow for VMs to attach to them.

###### This playbook has three basic options

* vm_cleanup - if `true` clenaup old VMs and create create new ones
* vm_purge - if `true` purge all VMs
* vm_flags - Options to pass into libvirt (virt-install).

All of these options are made for convienance and are not required for a basic
playbook run.

###### Post playbook run

Upon completion of the playbooks all VMs will be offline and enrolled into
vBMC.

An **instackenv** file will have been fetched and stored in the home directory
of the executing user. The file will be named `vm-instackenv.yaml`. This file
should be compatible with the TripleO / OSP baremetal node import
process.

> Example TripleO command: `openstack overcloud node import --introspect --provide vm-instackenv.yaml`

These playbooks are idempotent and will return an **instackenv** file even if
no new vms are created.
