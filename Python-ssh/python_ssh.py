#!/usr/bin/env python3
from copy import deepcopy
# from pprint import pprint

import netmiko
import yaml

Vendor_Type = 'Cisco'

COMMANDS_LIST = {
    'show clock',
    'show version | in image',
    'show users',
    'show ip interface brief | ex unassigned'
}


def read_pyaml(path='inventory.yml'):
    with open(path) as file:
        yaml_content = yaml.load(file.read(), Loader=yaml.FullLoader)
    return yaml_content


def form_connection_parameters_from_yaml(parsed_yaml, vendor='all'):
    """
    Form dictionary of netmiko connections parameters for all devices on site
    
    Args:
        parsed_yaml (dict): dictionary with parsed yaml file
        vendor (str): name of site. Default is 'all'
    Returns:
        dict: key is hostname, value is dict containing netmiko connection parameters for the host
    """
    parsed_yaml = deepcopy(parsed_yaml)
    # result = {}
    global_params = parsed_yaml['all']['vars']
    site_dict = parsed_yaml['all']['groups'].get(vendor)
    if site_dict is None:
        raise KeyError('Site {} is not specified in inventory.yml'.format(vendor))
    for host in site_dict['hosts']:
        host_dict = {}
        # hostname = host.pop('hostname')
        host_dict.update(global_params)
        host_dict.update(host)
        yield host_dict
        # result[hostname] = host_dict
    # return result


def collect_outputs(devices, commands):
    """
    Execute commands on devices

    Args:
        devices (dict): dictionary, where key is hostname, value is netmiko connection dictionary
        commands (list): list of commands to be executed on devices

    Returns:
        dict: key is hostname, value is string with all outputs
    """
    for device in devices:
        hostname = device.pop('hostname')
        connection = netmiko.ConnectHandler(**device)
        device_result = ['=' * 20 + hostname + '=' * 20]
        for command in commands:
            command_result = connection.send_command(command)
            device_result.append('=' * 20 + command_result + '=' * 20)
        device_result_string = '\n\n'.join(device_result)
        yield device_result_string


def main():
    parsed_yaml = read_pyaml()
    connection_params = form_connection_parameters_from_yaml(parsed_yaml, vendor=Vendor_Type)
    for device_result in collect_outputs(connection_params, COMMANDS_LIST):
        print(device_result)


if __name__ == '__main__':
    main()
