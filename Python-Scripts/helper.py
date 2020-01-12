from copy import deepcopy

import yaml


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
