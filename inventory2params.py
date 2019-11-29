import yaml
import collections

with open('vm-lab-inventory.yaml') as f:
    inv = yaml.safe_load(f.read())

orig = {
    'resource_registry': {
        'OS::TripleO::DeployedServer::ControlPlanePort': '/usr/share/openstack-tripleo-heat-templates/deployed-server/deployed-neutron-port.yaml'
    },
    'parameter_defaults': {
        'DeployedServerPortMap': {},
        'HostnameMap': {}
    }
}

vms = inv['vms']
index = collections.defaultdict(int)
for k, v in vms['hosts'].items():
    ooo_type = v.get('ooo_type', 'undefined')
    ooo_type_name = 'overcloud-%s' % ooo_type
    port_map = orig['parameter_defaults']['DeployedServerPortMap']
    port_map[k + '-ctlplane'] = {
        'fixed_ips': [
            {
                'ip_address': v['ansible_host']
            }
        ],
        'subnets': [
            {
                'cidr': 22
            }
        ]
    }
    host_map = orig['parameter_defaults']['HostnameMap']
    host_map['%s-%s' % (ooo_type_name, index[ooo_type_name])] = k
    index[ooo_type_name] += 1

with open('params-hosts.yml', 'w') as f:
    f.write(yaml.safe_dump(orig))
