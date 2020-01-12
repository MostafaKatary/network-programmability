#!/usr/bin/env python3
import netmiko

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
        device_result = ['{0} {1} {0}'.format('=' * 20, hostname)]

        try:
            connection = netmiko.ConnectHandler(**device)
            for command in commands:
                command_result = connection.send_command(command)
                device_result.append('{0} {1} {0}'.format('=' * 20, command))
                device_result.append(command_result)
            connection.disconnect()
        except netmiko.ssh_exception.NetMikoTimeoutException as e:
            device_result.append(str(e))

        device_result_string = '\n\n'.join(device_result)
        yield device_result_string


def main():
    parsed_yaml = read_pyaml()
    connection_params = form_connection_parameters_from_yaml(parsed_yaml, vendor=Vendor_Type)

    if Vendor_Type == 'Cisco':
        COMMANDS_LIST = COMMANDS_LIST_CISCO
    elif Vendor_Type == 'Juniper':
        COMMANDS_LIST = COMMANDS_LIST_JUNIPER

    for device_result in collect_outputs(connection_params, COMMANDS_LIST):
        print(device_result)


if __name__ == '__main__':
    main()
