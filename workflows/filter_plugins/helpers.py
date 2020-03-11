# Ansible cloud tools for lab based deployments
# Copyright (C) 2019  Kevin Carter
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import json
import os
import yaml
import collections
from collections import OrderedDict
from operator import itemgetter

from ansible.module_utils.parsing.convert_bool import boolean
from ansible.plugins.filter import ipaddr


class FilterModule(object):
    def __init__(self):
        self.rendered_template_path = '/tmp/templates'

    def filters(self):
        return {
            'preprov_hosts': self.preprov_hosts,
            'preprov_host_entry': self.preprov_host_entry,
            'non_ha': self.non_ha,
            'if_any': self.if_any,
            'novaless_hosts': self.novaless_hosts
        }

    def preprov_host_entry(self, data, anchor='ctlplane'):
        """
         data = DeployedServerPortMap:
                    compute2-vm-compute-1-controller-ctlplane:
                        fixed_ips:
                        -   ip_address: 172.16.27.165
                        subnets:
                        -   cidr: 22
                    compute2-vm-compute-1-compute-ctlplane:
                        fixed_ips:
                        -   ip_address: 172.16.27.207
                        subnets:
                        -   cidr: 22
                HostnameMap:
                    overcloud-controller-0: compute2-vm-compute-1-controller
                    overcloud-compute-0: compute2-vm-compute-1-compute
        """
        return_data = list()
        for k, v in data['HostnameMap'].items():
            orig_server = '{}-{}'.format(v, anchor)
            server = data['DeployedServerPortMap'][orig_server]
            for ip in server['fixed_ips']:
                return_data.append('{} {} {} {}'.format(ip['ip_address'], k, v, orig_server))
        else:
            return return_data

    @property
    def _resource_registry(self):
        """
        Type data pulled from THT
            OS::TripleO::.*::Net::SoftwareConfig
        """
        resource_registry = {
            'OS::TripleO::DeployedServer::ControlPlanePort': os.path.join(
                self.rendered_template_path,
                'deployed-server/deployed-neutron-port.yaml'
            )
        }
        software_types = [
            'OS::TripleO::BlockStorage::Net::SoftwareConfig',
            'OS::TripleO::CephStorage::Net::SoftwareConfig',
            'OS::TripleO::ComputeDVR::Net::SoftwareConfig',
            'OS::TripleO::Compute::Net::SoftwareConfig',
            'OS::TripleO::ControllerApi::Net::SoftwareConfig',
            'OS::TripleO::ControllerDeployedServer::Net::SoftwareConfig',
            'OS::TripleO::Controller::Net::SoftwareConfig',
            'OS::TripleO::ObjectStorage::Net::SoftwareConfig',
            'OS::TripleO::Standalone::Net::SoftwareConfig',
            'OS::TripleO::UndercloudMinion::Net::SoftwareConfig',
            'OS::TripleO::Undercloud::Net::SoftwareConfig'
        ]
        for software_type in software_types:
            resource_registry[software_type] = os.path.join(
                    self.rendered_template_path,
                    'vm_interface_template.yaml'
            )
        else:
            return resource_registry

    def non_ha(self, data):
        resource_registry = {
            'OS::TripleO::Services::CinderVolume': os.path.join(
                self.rendered_template_path,
                'deployment/cinder/cinder-volume-container-puppet.yaml'
            ),
            'OS::TripleO::Services::RabbitMQ': os.path.join(
                self.rendered_template_path,
                'deployment/rabbitmq/rabbitmq-container-puppet.yaml'
            ),
            'OS::TripleO::Services::HAproxy': os.path.join(
                self.rendered_template_path,
                'deployment/haproxy/haproxy-container-puppet.yaml'
            ),
            'OS::TripleO::Services::Redis': os.path.join(
                self.rendered_template_path,
                'deployment/database/redis-container-puppet.yaml'
            ),
            'OS::TripleO::Services::MySQL': os.path.join(
                self.rendered_template_path,
                'deployment/database/mysql-container-puppet.yaml'
            ),
            'OS::TripleO::Services::Keepalived': os.path.join(
                self.rendered_template_path,
                'deployment/keepalived/keepalived-container-puppet.yaml'
            ),
            'OS::TripleO::Services::Pacemaker': 'OS::Heat::None',
            'OS::TripleO::Services::PacemakerRemote': 'OS::Heat::None'
        }
        data['resource_registry'].update(resource_registry)
        return data

    def preprov_hosts(self, inv, rendered_template_path=None,
                      anchor='ctlplane', stackname='overcloud'):
        # These resources are assumed to be generated and stored in the
        # /tmp/templates directory.
        if rendered_template_path:
            self.rendered_template_path = rendered_template_path

        orig = {
            'resource_registry': self._resource_registry,
            'parameter_defaults': {
                'DeployedServerPortMap': {},
                'HostnameMap': {}
            }
        }

        vms = inv['vms']
        index = collections.defaultdict(int)
        for k, v in vms['hosts'].items():
            if 'tripleo_deploy_type' in v:
                if v['tripleo_deploy_type'] != 'undefined':
                    tripleo_deploy_type_name = '{}-{}'.format(
                        stackname,
                        v['tripleo_deploy_type']
                    )
                    port_map = orig['parameter_defaults']['DeployedServerPortMap']
                    network_address = v.get('vm_management_net', v.get('ansible_host'))
                    port_map[k + '-' + anchor] = {
                        'fixed_ips': [
                            {
                                'ip_address': ipaddr.ipaddr(
                                    network_address,
                                    query='address',
                                    version=False,
                                    alias='ipaddr'
                                )
                            }
                        ],
                        'subnets': [
                            {
                                'cidr': ipaddr.ipaddr(
                                    network_address,
                                    query='prefix',
                                    version=False,
                                    alias='ipaddr'
                                )
                            }
                        ],
                        'network': {
                            'tags': [
                                ipaddr.ipaddr(
                                    network_address,
                                    query='network/prefix',
                                    version=False,
                                    alias='ipaddr'
                                )
                            ]
                        }
                    }
                    host_map = orig['parameter_defaults']['HostnameMap']
                    host_entry = '{}-{}'.format(
                        tripleo_deploy_type_name,
                        index[tripleo_deploy_type_name]
                    )
                    host_map[host_entry] = k
                    index[tripleo_deploy_type_name] += 1

        return orig

    def novaless_hosts(self, inv, anchor='ctlplane', stackname='overcloud'):
        types = dict()
        index = collections.defaultdict(int)
        for k, v in inv['vms']['hosts'].items():
            if 'tripleo_deploy_type' in v:
                if v['tripleo_deploy_type'] == 'minion':
                    continue
                elif v['tripleo_deploy_type'] == 'undercloud':
                    continue
                else:
                    tripleo_deploy_type_name = '{}-{}'.format(
                        stackname,
                        v['tripleo_deploy_type']
                    )

                    if v['tripleo_deploy_type'] == 'novacompute':
                        type_name = 'compute'
                    else:
                        type_name = v['tripleo_deploy_type']

                    if type_name == 'Undefined':
                        continue

                    type_name = type_name.capitalize()

                    if type_name in types:
                        type_data = types[type_name]
                    else:
                        type_data = types[type_name] = dict()
                        type_data['name'] = type_name
                        type_data['count'] = 0
                        type_data['instances'] = list()
                        type_data['defaults'] = {'image': {'href': 'overcloud-full'}}

                    instance_data = dict()
                    instance_data['name'] = k
                    instance_data['hostname'] = '{}-{}'.format(
                        tripleo_deploy_type_name,
                        index[tripleo_deploy_type_name]
                    )
                    index[tripleo_deploy_type_name] += 1
                    type_data['count'] += 1
                    disk_size = v.get('vm_disk_size', 12)
                    instance_data['root_size_gb'] = disk_size - 3
                    instance_data['swap_size_mb'] = 2 * 1024

                    nics = list()
                    nic_data = dict()
                    vm_preprov_networks = v.get('vm_preprov_networks')
                    if vm_preprov_networks:
                        for _, ips in vm_preprov_networks.items():
                            nic_data['network'] = 'ctlplane'  # This should be able to be defined.
                            for ip in ips:  # The last ip address defined will always win.
                                network_address = ipaddr.ipaddr(
                                    ip,
                                    query='address',
                                    version=False,
                                    alias='ipaddr'
                                )
                                if network_address:
                                    nic_data['fixed_ip'] = network_address
                    if nic_data:
                        nics.append(nic_data)

                    if nics:
                        instance_data['nics'] = nics

                    type_data['instances'].append(instance_data)

        return [i for i in types.values()]

    def if_any(self, items):
        return any([boolean(i) for i in items if i])
