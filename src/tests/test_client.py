import pytest
from openapi_core.validation.response.datatypes import OpenAPIResponse
from starlette.testclient import TestClient

from pyotr.client import Client
from pyotr.server import Application


def test_client_calls_endpoint(spec_dict, config):
    app = Application(spec_dict, module=config.endpoint_base)
    client = Client(spec_dict, client=TestClient(app))
    response = client.dummy_test_endpoint()
    assert isinstance(response, OpenAPIResponse)
    assert response.payload == {"foo": "bar"}


def test_client_calls_endpoint_using_server_with_path(spec_dict, config):
    spec_dict["servers"].insert(0, {"url": "http://localhost:8001/with/path"})
    app = Application(spec_dict, module=config.endpoint_base)
    client = Client(spec_dict, client=TestClient(app))
    response = client.dummy_test_endpoint()
    assert isinstance(response, OpenAPIResponse)
    assert response.payload == {"foo": "bar"}


def test_client_calls_endpoint_with_custom_headers(spec_dict, config, monkeypatch):
    app = Application(spec_dict, module=config.endpoint_base)
    client = Client(spec_dict, client=TestClient(app))

    def patch_request(request):
        def wrapper(*args, **kwargs):
            client.request_info = {"args": args, "kwargs": kwargs}
            return request(*args, **kwargs)

        return wrapper

    monkeypatch.setattr(client.client, "request", patch_request(client.client.request))
    client.dummy_test_endpoint(headers_={"foo": "bar"})
    assert client.request_info["kwargs"]["headers"] == {"foo": "bar"}


def test_client_incorrect_args_raises_error(spec_dict, config):
    app = Application(spec_dict, module=config.endpoint_base)
    client = Client(spec_dict, client=TestClient(app))
    with pytest.raises(RuntimeError) as error:
        client.dummy_test_endpoint("foo")
    assert error.exconly() == "RuntimeError: Incorrect arguments: dummyTestEndpoint accepts no positional arguments"


def test_client_too_few_args_raises_error(spec_dict, config):
    app = Application(spec_dict, module=config.endpoint_base)
    client = Client(spec_dict, client=TestClient(app))
    with pytest.raises(RuntimeError) as error:
        client.dummy_test_endpoint_with_argument()
    assert error.exconly() == (
        "RuntimeError: Incorrect arguments: dummyTestEndpointWithArgument accepts 1 positional argument: test_arg"
    )


def test_unknown_server_url_gets_added_to_spec(spec_dict):
    test_server = spec_dict["servers"][1]["url"]
    client = Client(spec_dict, server_url=test_server)
    assert client.server_url == test_server


def test_known_server_url_gets_selected(spec_dict):
    client = Client(spec_dict, server_url="foo.bar")
    assert client.server_url == "foo.bar"
    assert client.spec.servers[-1].url == "foo.bar"


def test_use_first_server_url_as_default(spec_dict):
    client = Client(spec_dict)
    assert client.server_url == spec_dict["servers"][0]["url"]


def test_incorrect_endpoint_raises_error(spec_dict):
    client = Client(spec_dict)
    with pytest.raises(AttributeError):
        client.foo_bar()


@pytest.mark.parametrize("filename", ("openapi.json", "openapi.yaml"))
def test_from_file(config, filename):
    file_path = config.test_dir / filename
    client = Client.from_file(file_path)
    assert client.spec.info.title == "Test Spec"


def test_from_file_raises_exception_if_unknown_type(config):
    file_path = config.test_dir / "openapi.unknown"
    with pytest.raises(RuntimeError):
        Client.from_file(file_path)


def test_endpoint_docstring_constructed_from_spec(spec_dict):
    client = Client(spec_dict)
    assert client.dummy_test_endpoint.__doc__ == (
        "A dummy test endpoint.\n\nA test endpoint that doe nothing," " so is pretty dummy, but works fine for testing."
    )

def test_endpoint_docstring_constructed_with_default_values(spec_dict):
    client = Client(spec_dict)
    assert client.dummy_test_endpoint_with_argument.__doc__ == "dummyTestEndpointWithArgument"
