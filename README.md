# AnsiStack

This repository contains tools for running cloud like infrastructure without
cloud like APIs. The tools themselves are Ansible playbooks which interact with
hosts to provision and manage virtualized infrastructure with minimal, to no,
overhead. This ansible driven approach provides for no niceties, no frills,
just straight virtualization. By aiming at pure virtualization and the smallest
possible footprint, AnsiStack builds, tests, runs, and develops machine based
workloads that are able to bind to any hardware, attach to any network, and
emulate most any architecture.

> In a world where there are seemingly millions of over engineered cloud
  solutions, AnsiStack aims to be **NOT** that.

## Infrastructure vs Workflows

At this time AnsiStack has two different code paths, **Infrastructure** and
**Workflows**. The code within the infrastructure directory is designed to
setup hypervisors and build virtualized infrastructure. The workflows directory
contains playbooks that are used to deploy solutions within virtualized
infrastructure.

## Deployment Particulars

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

### Virtual machine Inventory examples

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

### PCI passthrough

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
