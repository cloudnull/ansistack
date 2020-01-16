# AnsiStack

This repository contains tools for running cloud like infrastructure without
cloud like APIs. The tools themselves are Ansible playbooks which interact with
hosts to provision and manage virtualized infrastructure with minimal, to no,
overhead. This ansible driven approach provides for no niceties, no frills,
just straight virtualization. By aiming at pure virtualization and the smallest
possible footprint, AnsiStack allow builds, tests, runs, and develops
Machine based workloads that are able to bind to any hardware, attach to any
network, and emulate most any architecture.

## Infrastructure vs Workflows

At this time AnsiStack has two different code paths, **Infrastructure** and
**Workflows**. The code within the infrastructure directory is designed to
setup hypervisors and build virtualized infrastructure. The workflows driectory
contains playbooks that are used to deploy solutions within virtualized
infrastructure.

## Deployment Particulars

The process to build virtual machines has been broken up into three primary types.

1. Image based deployment using QCOW2 images. These deployments will reside
   within a qcow2 container that can be dynamically expanded as needed. Image
   based deployments are pre-configured using cloud-init allowing the deployer
   to provide additional packages, script based automation, and static IP
   addresses.

2. ISO based deployment. These deployments will setup the instance using a
   QCOW2 container that can be dynamically expanded as needed. The instance will
   bootup with the ISO attached to it and allow the operator to console to the VM
   to continue the installation or use-case.

3. No OS based deployment. These deployments will setup the instance using a
   QCOW2 container that can be dynamically expanded as needed. The install will
   power-on, then wait for a boot protocol over the network. These instances will
   be connected to a vBMC controller, which will allow the instances to be
   controlled via iPMI.
