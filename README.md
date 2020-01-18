# AnsiStack

This repository contains tools for running cloud like infrastructure without
cloud like APIs. The tools themselves are Ansible playbooks which interact with
hosts to provision and manage virtualized infrastructure with minimal, to no,
overhead. This ansible driven approach provides for no niceties, no frills,
just straight virtualization. By aiming at pure virtualization and the smallest
possible footprint, AnsiStack builds, tests, runs, and develops machine based
workloads that are able to bind to any hardware, attach to any network, and
emulate most any architecture.

In a world where there are seemingly millions of over engineered cloud and
infrastructure solutions, AnsiStack aims to be, **NOT** that.

## Infrastructure vs Workflows

At this time AnsiStack has two different code paths, **Infrastructure** and
**Workflows**. The code within the infrastructure directory is designed to
setup hypervisors and build virtualized infrastructure. The workflows directory
contains playbooks that are used to deploy solutions within virtualized
infrastructure.

### Virtual Machine Deployment Particulars

The process to build virtual machines has been broken up into three primary types.

1. **Image based deployment using QCOW2 images**. These deployments will reside
   within a QCOW2 container that can be dynamically expanded as needed. Image
   based deployments are pre-configured using cloud-init allowing the deployer
   to provide additional packages, script based automation, and static IP
   addresses.

2. **ISO based deployment**. These deployments will setup the instance using a
   QCOW2 container that can be dynamically expanded as needed. The instance will
   bootup with the ISO attached to it and allow the operator to console to the VM
   to continue the installation or use-case.

3. **No OS based deployment**. These deployments will setup the instance using a
   QCOW2 container that can be dynamically expanded as needed. The install will
   power-on, then wait for a boot protocol over the network. These instances will
   be connected to a vBMC controller, which will allow the instances to be
   controlled via iPMI.

#### Virtual Machine Inventory Examples

To enable virtual machine deployments, inventory entries are required to define
each virtual machine name, type, and placement.

###### Image based deployment

``` yaml
provisioned_vms:
    hosts:
        centos7-vm:
            vm_virt_host: "compute1"
            vm_image_name: centos7
            vm_cores: 8  # Number of cores
            vm_ram: 16384  # Size in MiB
            vm_disk_size: 32  # Size in GiB
            vm_networks:
                uplink:
                    dhcp: true
                    interface: eth0
                    manager: nmcli
            vm_preprov_networks:
                eth1:
                - "192.168.4.104/22"
```

> The option **vm_preprov_networks** is used to define static IP address that
  bind to particular network interfaces; this option can be omitted.

> The option **vm_networks** is used to define the interfaces that will be
  attached to the virtual machine. This is a hash with the first key
  corresponding to the network name on the hypervisor which an interface will be
  spawned with. The sub-option **dhcp** is a boolean and will enable or disable
  DHCP on a given interface. The sub-option **manager** is a string and instructs
  cloud-init how to configure a given interface.

###### ISO based deployment

``` yaml
provisioned_vms:
    hosts:
        windows10-vm:
            vm_virt_host: "compute1"
            vm_bootable_iso: Win10_1909_English_x64.iso
            vm_variant: win10
            vm_cores: 8  # Number of cores
            vm_ram: 16384  # Size in MiB
            vm_disk_size: 32  # Size in GiB
            vm_networks:
                uplink:
                    interface: eth0
            vm_additional_isos:
            - virtio-win-0.1.171.iso
```

> The option **vm_bootable_iso** is a string and used to define the name of the ISO
  being attached to this VM.

> The **vm_additional_isos** option is a list and used to define any additional ISO
  files to attache to the VM.

> The option **vm_networks** is used to define the interfaces that will be
  attached to the virtual machine. This is a hash with the first key
  corresponding to the network name on the hypervisor which an interface will be
  spawned with.

###### No OS based deployment

``` yaml
bootable_vms:
    hosts:
        undefined-vm:
            vm_virt_host: "compute1"
            vm_cores: 8  # Number of cores
            vm_ram: 16384  # Size in MiB
            vm_disk_size: 32  # Size in GiB
            vm_networks:
                uplink:
                    interface: eth0
            vm_vbmc_port: 16026
```

> The **vm_vbmc_port** option is an integer and is used to define the port number
  that the hypervisor will allow iPMI commands on when controlling a given
  virtual machine.

> The option **vm_networks** is used to define the interfaces that will be
  attached to the virtual machine. This is a hash with the first key
  corresponding to the network name on the hypervisor which an interface will be
  spawned with.

### PCI Passthrough

Virtual machines can be given a specific PCI device which allows for specific
hardware availability within a virtualized machine. To enable PCI passthrough
define two options are available, **vm_passthrough_lookup_regex** and
**vm_pci_passthrough_devices**.

1. The **vm_passthrough_lookup_regex** option is a string which contains a regex
   pattern which will be used to search for devices that will be passed through
   to the virtual machine. *This search uses information obtained by `lspci`.*

2. The **vm_pci_passthrough_devices** option is a list which contains strings for
   device IDs used to define a particular piece of hardware. *The items within
   this list must match the items found in the output of the command
   `virsh nodedev-list`.*

#### Virtual machine Inventory examples with PCI passthrough

###### Regex PCI passthrough

``` yaml
provisioned_vms:
    hosts:
        windows10-gfx-vm:
            vm_virt_host: "compute1"
            vm_bootable_iso: Win10_1909_English_x64.iso
            vm_variant: win10
            vm_cores: 8  # Number of cores
            vm_ram: 16384  # Size in MiB
            vm_disk_size: 32  # Size in GiB
            vm_networks:
                uplink:
                    interface: eth0
            vm_additional_isos:
            - virtio-win-0.1.171.iso
            vm_passthrough_lookup_regex: '.*Ellesmere.*'
```

> In this example all devices that match the **'.*Ellesmere.*'** regex will be
  passed through to the virtual machine.

###### Specific device PCI passthrough

``` yaml
provisioned_vms:
    hosts:
        windows10-pci-vm:
            vm_virt_host: "compute1"
            vm_bootable_iso: Win10_1909_English_x64.iso
            vm_variant: win10
            vm_cores: 8  # Number of cores
            vm_ram: 16384  # Size in MiB
            vm_disk_size: 32  # Size in GiB
            vm_networks:
                uplink:
                    interface: eth0
            vm_additional_isos:
            - virtio-win-0.1.171.iso
            vm_pci_passthrough_devices:
            - pci_0000_05_04_0
            - pci_0000_05_02_0
```

> In this example the specific devices **pci_0000_05_04_0** and
  **pci_0000_05_02_0** will be passed through to the virtual machine.

### Server Setup

Server setup is simple, though can be as complex as you want it to be. The base
requirement is a modern GNU/Linux operating system capable of running **KVM**
via **libvirt**.

Server playbooks within AnsiStack support Fedora29+, CentOS7/8, RHEL7/8, and
Debian 9+. While these playbooks exist to stand up a server that will run
virtualized workloads, these playbooks are optional. Any GNU/Linux server that
is capable of running **KVM** via **libvirt** with the `virsh` and
`virt-install` commands should be able to run AnsiStack workloads.

#### Basic Requirements

1. GNU/Linux

2. KVM

3. `virsh`

4. Libvirt

5. `virt-install`

#### Server Inventory Examples

To enable virtual machine deployments on servers, inventory entries are
required to define each server.

###### Server configuration

``` yaml
libvirt_hosts:
    hosts:
        kvm-server1:
            ansible_host: 10.1.1.10
            server_networks:
                uplink:
                    interface: eth1
                    type: macvlan
                external:
                    interface: eth1-VLAN10
                    type: macvlan
```

> The option **server_networks** is used to define network devices within
  virsh. The key for each network will define the name for the network within
  virsh. The **interface** option is a string, and is required. This option
  defines the ethernet device virsh network will bind to. The key **type** is a
  string, and is required. This option sets the network type virsh will attach
  virtual machines to; available options are *macvlan*, and *bridge*.

#### Server Optional Configuration and Optimizations

Several infrastructure playbooks exist that can be used to customize and
optimize virtualized workloads.

###### Server governor configuration

The playbook **server-governor.yml** will scan for and set server performance
options. This playbook sets all discovered power states to *performance*.

###### Server storage setup

The playbook **server-storage-setup.yml** configures block devices into
suitable storage for running virtual machines. This is done in one of two ways.

1. A set of disks are built into a software RAID.

2. A given block device is partitioned and provisioned using logical volumes.

#### Server Storage Inventory Examples

To enable virtual machine deployments on servers, inventory entries are
required to define each server.

###### Storage array deployment

``` yaml
libvirt_hosts:
    hosts:
        kvm-server1:
            ansible_host: 10.1.1.10
            server_storage_arrays:
            - name: 'md0'
              level: 0
              opts: 'noatime'
              mountpoint: /var/lib/libvirt
              fs: 'xfs'
              devices:
              - /dev/sdh
              - /dev/sdi
              - /dev/sdj
              - /dev/sdb
              - /dev/sdc
              - /dev/sdd
              - /dev/sde
              - /dev/sdg
              - /dev/sdf
              - /dev/sda
```

> The **server_storage_arrays** option is an list of hashes and is used to
  define the RAID array the playbook will setup. The key **name** is a string and
  defines the name of the array that will be created. The key **level** is an
  integer and defines the RAID level to be created. The key **opts** is a string
  and defines mount options when the device is mount within the system. The key
  **mountpoint** is a string and defines where the device will be mounted. The
  key **fs** is a string and defines the filesystem the device will be formatted.
  The key **devices** is a list, which defines all of the block devices that will
  make up the raid array.


###### Storage array deployment

``` yaml
libvirt_hosts:
    hosts:
        kvm-server1:
            ansible_host: 10.1.1.10
            server_storage_drive: /dev/sdb1
```

> The option **server_storage_drive** is a string and defines a block device or
  partition that will be provisioned using logical volumes, formatted *XFS*,
  and mounted at `/var/lib/libvirt`.

#### Server updates

The playbook **server-update.yml** will run package updates across the board.

#### Server power

The playbook **server-power.yml** will run IPMI power commands from the
executing system against a given host. This playbooks requires the `ipmitool`
command to be installed locally. Common extra options used in conjunction with
this playbook is **server_ipmi_command** which augments the power command; the
default value is *status*. This playbook will only interact with hosts that the
required options **server_ipmi_address**, **server_ipmi_username**,
**server_ipmi_password**, and defined within inventory.

###### Server power inventory examples

``` yaml
libvirt_hosts:
    hosts:
        kvm-server1:
            ansible_host: 10.1.1.10
            server_ipmi_address: 192.168.1.100
            server_ipmi_username: ADMIN
            server_ipmi_password: secrete
```

----

## Complete Inventory Examples

Complete inventory examples can be seen within this repository.

1. The file **inventory-phys.yaml** contains a complete example which enables
   servers for AnsiStack workloads.

2. The file **inventory-vms.yaml** contains a complete example which provides
   for virtualized workloads.
