import json
from pathlib import Path

import pytest


@pytest.fixture
def spec_dict(config):
    file_path = config.test_dir / "openapi.json"
    with open(file_path) as spec_file:
        return json.load(spec_file)


class Config:
    def __init__(self):
        self.test_dir = Path(__file__).parent
        self.endpoint_base = "tests.endpoints"


@pytest.fixture
def config():
    return Config()
