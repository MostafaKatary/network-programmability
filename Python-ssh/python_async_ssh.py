#!/usr/bin/env python3
import asyncio
from copy import deepcopy
# from pprint import pprint

import netdev
import yaml

Vendor_Type = 'Cisco'

COMMANDS_LIST_CISCO = {
    'show clock',
    'show version | in Version',
    'show users',
    'show ip interface brief | ex unassigned'
}

COMMANDS_LIST_JUNIPER = {
    'show system uptime',
    'show version | match Junos:',
    'show system users',
    'show interfaces terse | match inet'
}


def read_pyaml(path='inventory.yml'):
    """
    Reads inventory yaml file and return dictionary with parsed values
    Args:
        path (str): path to inventory YAML

    Returns:
        dict: parsed inventory YAML values

    """
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
    global_params = parsed_yaml['all']['vars']
    site_dict = parsed_yaml['all']['groups'].get(vendor)
    if site_dict is None:
        raise KeyError('Site {} is not specified in inventory.yml'.format(vendor))
    for host in site_dict['hosts']:
        host_dict = {}
        host_dict.update(global_params)
        host_dict.update(host)
        yield host_dict


async def collect_outputs(device_params, commands):
    """
    Execute commands on devices

    Args:
        device_params (dict): dictionary, where key is hostname, value is netmiko connection dictionary
        commands (list): list of commands to be executed on devices

    Returns:
        dict: key is hostname, value is string with all outputs
    """
    hostname = device_params.pop('hostname')
    device_result = ['{0} {1} {0}'.format('=' * 20, hostname)]

    try:
        async with netdev.create(**device_params) as connection:
            device_result = ['{0} {1} {0}'.format('=' * 20, hostname)]

            for command in commands:
                command_result = await connection.send_command(command)
                device_result.append('{0} {1} {0}'.format('=' * 20, command))
                device_result.append(command_result)

    except netdev.exceptions.TimeoutError as e:
        device_result.append(str(e))
        device_result_string = '\n\n'.join(device_result)

    device_result_string = '\n\n'.join(device_result)
    return device_result_string


def main():
    parsed_yaml = read_pyaml()
    if Vendor_Type == 'Cisco':
        COMMANDS_LIST = COMMANDS_LIST_CISCO
    elif Vendor_Type == 'Juniper':
        COMMANDS_LIST = COMMANDS_LIST_JUNIPER

    loop = asyncio.get_event_loop()
    tasks = [loop.create_task(collect_outputs(device, COMMANDS_LIST))
             for device in form_connection_parameters_from_yaml(parsed_yaml, vendor=Vendor_Type)]
    loop.run_until_complete(asyncio.wait(tasks))
    for task in tasks:
        print(task.result())


if __name__ == '__main__':
    main()
