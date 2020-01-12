#!/usr/bin/env python3
import asyncio
import netdev

from helper import read_pyaml, form_connection_parameters_from_yaml

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
