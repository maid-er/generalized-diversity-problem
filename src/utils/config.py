'''Function to handle configuration YAML files'''
import os
import yaml


def read_config(instance_name: str):
    '''
    Reads a YAML configuration file based on the provided instance name.

    Args:
      instance_name (str): reads the configuration from a YAML file specific to the
    `instance_name` instance.

    Returns:
      (dict): the configuration settings loaded from a YAML file specific to the `instance_name`
    provided as an argument.
    '''
    yaml_relative_path = os.path.join('..', '..', 'config', f'{instance_name}.yaml')
    file_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), yaml_relative_path)
    with open(file_path, 'r', encoding='utf-8') as yamlfile:
        config = yaml.safe_load(yamlfile)

    return config
