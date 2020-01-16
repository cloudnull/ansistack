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
