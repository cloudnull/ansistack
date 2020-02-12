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

import collections


class FilterModule(object):
    def __init__(self):
        self.rendered_template_path = '/tmp/templates'

    def filters(self):
        return {
            'bootable_hosts': self.bootable_hosts,
        }

    def bootable_hosts(self, ansible_play_batch, hostvars, groups,
                       stackname='overcloud'):
        nodes_list = list()
        index = collections.defaultdict(int)
        for node in ansible_play_batch:
            node_facts = hostvars.get(node)
            if node_facts and node in groups.get('bootable_vms', list()):
                node_info = {}
                if isinstance(node_facts.get('vm_macs'), list):
                    node_info['mac'] = node_facts['vm_macs']

                if 'tripleo_capabilities' in node_facts:
                    node_info['capabilities'] = '{}'.format(
                        node_facts['tripleo_capabilities']
                    )
                else:
                    node_info['capabilities'] = ''

                type_name = node_facts.get('tripleo_deploy_type')
                if type_name:
                    node_name = '{}-{}-{}'.format(
                        stackname,
                        type_name,
                        index[type_name]
                    )
                    index[type_name] += 1
                else:
                    for capability in node_info['capabilities'].split(','):
                        if 'profile' in capability:
                            _, type_name = capability.split(':')
                            type_name = type_name.strip()
                            node_name = '{}-{}-{}'.format(
                                stackname,
                                type_name,
                                index[type_name]
                            )
                            index[type_name] += 1
                            break
                    else:
                        node_name = node_facts['inventory_hostname']

                node_info['capabilities'] = '{},node:{}'.format(
                    node_info['capabilities'],
                    node_name
                )
                node_info['name'] = node_facts['inventory_hostname']
                node_info['cpu'] = node_facts['vm_cores']
                node_info['memory'] = node_facts['vm_ram']
                node_info['disk'] = node_facts['vm_disk_size']
                node_info['arch'] = 'x86_64'
                node_info['pm_type'] = 'ipmi'
                node_info['pm_user'] = node_facts['vm_vbmc_username']
                node_info['pm_password'] = node_facts['vm_vbmc_password']
                virt_host = node_facts['vm_virt_host']
                node_info['pm_addr'] = hostvars[virt_host]['ansible_host']
                node_info['pm_port'] = node_facts['vm_vbmc_port']
                node_info['_comment'] = (
                    'original target hostname [{}]. This is'
                    ' a KVM VM controlled with VBMC.'.format(
                        node_facts['inventory_hostname']
                    )
                )
                nodes_list.append(node_info)
        else:
            return {'nodes': nodes_list}
