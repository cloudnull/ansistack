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


class FilterModule(object):
    def filters(self):
        return {
            'preprov_hosts': self.preprov_hosts
            }

    def preprov_hosts(self, inv, cidr):
        tht = "/usr/share/openstack-tripleo-heat-templates"
        orig = {
            'resource_registry': {
                'OS::TripleO::DeployedServer::ControlPlanePort': os.path.join(
                    tht, 'deployed-server/deployed-neutron-port.yaml'),
                'OS::TripleO::Controller::Net::SoftwareConfig': os.path.join(
                    tht, 'templates/net-config-static-bridge.yaml'),
                'OS::TripleO::Compute::Net::SoftwareConfig': os.path.join(
                    tht, 'templates/net-config-static-bridge.yaml')
            },
            'parameter_defaults': {
                'DeployedServerPortMap': {},
                'HostnameMap': {}
            }
        }

        vms = inv['vms']
        index = collections.defaultdict(int)
        for k, v in vms['hosts'].items():
            if 'ooo_type' in v:
                if v['ooo_type'] != 'undefined':
                    ooo_type_name = 'overcloud-%s' % v['ooo_type']
                    port_map = orig['parameter_defaults']['DeployedServerPortMap']
                    port_map[k + '-ctlplane'] = {
                        'fixed_ips': [
                            {
                                'ip_address': v['ansible_host']
                            }
                        ],
                        'subnets': [
                            {
                                'cidr': cidr
                            }
                        ]
                    }
                    host_map = orig['parameter_defaults']['HostnameMap']
                    host_map['%s-%s' % (ooo_type_name, index[ooo_type_name])] = k
                    index[ooo_type_name] += 1

        return orig
