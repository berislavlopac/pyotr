import yaml
import json
from .conftest import Config


def yaml2json():
    """ Helper method used in development to convert YAML files to JSON.
    """
    c = Config()
    with open(c.yaml_spec_file) as yaml_file:
        spec_dict = yaml.safe_load(yaml_file)
    with open(c.json_spec_file, 'w') as json_file:
        json.dump(spec_dict, json_file)
