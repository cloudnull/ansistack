# Virt Lab Setup and VM Deployment

This repository contains playbooks which may be useful when setting cloud
deployments using Virtual Machines. While this is geared toward lab
deployments there's nothing stopping these tools from being used in
production.

## Virtual Server Setup

TBD

## TripleO Undercloud Deployment

TBD

## TripleO Overcloud Deployment

TBD

## Creating Virtual Machines

###### Assumptions

* VirtualBMC is already be installed and ready for use.
* The `virt-install` command is available on the `vm_virt_host` system.

###### Usage

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
