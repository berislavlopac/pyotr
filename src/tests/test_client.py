import pytest
from pyotr.client import Client
from pyotr.server import Application
from pyotr.validation.responses.client import ClientOpenAPIResponse
from starlette.testclient import TestClient


def test_client_calls_endpoint(spec_dict, config):
    app = Application.from_file(config.yaml_spec_file, config.endpoint_base)
    client = Client(spec_dict, client=TestClient(app))
    response = client.dummy_test_endpoint()
    assert isinstance(response, ClientOpenAPIResponse)
    assert response.payload == {'foo': 'bar'}


def test_client_incorrect_args_raises_error(spec_dict, config):
    app = Application.from_file(config.yaml_spec_file, config.endpoint_base)
    client = Client(spec_dict, client=TestClient(app))
    with pytest.raises(RuntimeError):
        client.dummy_test_endpoint('foo')


def test_unknown_server_url_gets_added_to_spec(spec_dict):
    client = Client(spec_dict, server_url='foo.bar')
    assert 'foo.bar' in client.spec.servers


def test_incorrect_incorrect_endpoint_raises_error(spec_dict):
    client = Client(spec_dict)
    with pytest.raises(AttributeError):
        client.foo_bar()


def test_from_file_yaml(config):
    app = Client.from_file(config.yaml_spec_file)
    assert app.spec.info.title == "Test Spec"


def test_from_file_json(config):
    app = Client.from_file(config.json_spec_file)
    assert app.spec.info.title == "Test Spec"


def test_from_file_raises_exception_if_unknown_type(config):
    with pytest.raises(RuntimeError):
        Client.from_file(config.unknown_spec_file)


