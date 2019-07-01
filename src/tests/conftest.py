import json
from pathlib import Path

import pytest

TEST_DIR = Path(__file__).parent
JSON_SPEC_FILE = TEST_DIR / 'openapi.json'


@pytest.fixture
def spec_dict(config):
    with open(config.json_spec_file) as spec_file:
        return json.load(spec_file)


class Config:
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.json_spec_file = self.test_dir / 'openapi.json'
        self.yaml_spec_file = self.test_dir / 'openapi.yaml'
        self.unknown_spec_file = self.test_dir / 'openapi.unknown'
        self.endpoint_base = 'tests.endpoints'


@pytest.fixture
def config():
    return Config()
