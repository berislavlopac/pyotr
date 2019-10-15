import pytest
from starlette.testclient import TestClient

from pyotr.client import Client
from pyotr.server import Application
from pyotr.validation.responses.client import ClientOpenAPIResponse


def test_client_calls_endpoint(spec_dict, config):
    spec_path = config.test_dir / 'openapi.yaml'
    app = Application.from_file(spec_path, config.endpoint_base)
    client = Client(spec_dict, client=TestClient(app))
    response = client.dummy_test_endpoint()
    assert isinstance(response, ClientOpenAPIResponse)
    assert response.payload == {'foo': 'bar'}


def test_client_incorrect_args_raises_error(spec_dict, config):
    spec_path = config.test_dir / 'openapi.yaml'
    app = Application.from_file(spec_path, config.endpoint_base)
    client = Client(spec_dict, client=TestClient(app))
    with pytest.raises(RuntimeError):
        client.dummy_test_endpoint('foo')


def test_unknown_server_url_gets_added_to_spec(spec_dict):
    client = Client(spec_dict, server_url='foo.bar')
    assert client.server_url == 'foo.bar'
    assert client.spec.servers[-1].url == 'foo.bar'


def test_use_first_server_url_as_default(spec_dict):
    client = Client(spec_dict)
    assert client.server_url == 'https://localhost:8000'


def test_incorrect_endpoint_raises_error(spec_dict):
    client = Client(spec_dict)
    with pytest.raises(AttributeError):
        client.foo_bar()


@pytest.mark.parametrize('filename', ('openapi.json', 'openapi.yaml'))
def test_from_file(config, filename):
    file_path = config.test_dir / filename
    app = Client.from_file(file_path)
    assert app.spec.info.title == "Test Spec"


def test_from_file_raises_exception_if_unknown_type(config):
    file_path = config.test_dir / 'openapi.unknown'
    with pytest.raises(RuntimeError):
        Client.from_file(file_path)
