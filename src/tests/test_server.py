from inspect import iscoroutinefunction

import pytest
from pyotr.server import Application
from starlette.requests import Request
from starlette.responses import JSONResponse


def test_server_from_file_yaml(config):
    app = Application.from_file(config.yaml_spec_file, config.endpoint_base)
    assert app.spec.info.title == "Test Spec"


def test_server_from_file_json(config):
    app = Application.from_file(config.json_spec_file, config.endpoint_base)
    assert app.spec.info.title == "Test Spec"


def test_server_from_file_raises_exception_if_unknown_type(config):
    with pytest.raises(RuntimeError):
        Application.from_file(config.unknown_spec_file, config.endpoint_base)


def test_server_dotted_endpoint(spec_dict):
    spec_dict['paths']['/test']['get']['operationId'] = 'endpoints.dummyTestEndpoint'
    spec_dict['paths']['/test-async']['get']['operationId'] = 'endpoints.dummyTestEndpointCoro'
    app = Application(spec_dict, 'tests')
    route = app.routes[0]
    assert callable(route.endpoint)
    assert route.endpoint.__name__ == 'dummy_test_endpoint'
    assert route.path == '/test'


def test_server_no_endpoint_module(spec_dict):
    with pytest.raises(RuntimeError):
        Application(spec_dict, 'foo.bar')


def test_server_no_endpoint_function(spec_dict, config):
    spec_dict['paths']['/test']['get']['operationId'] = 'fooBar'
    with pytest.raises(RuntimeError):
        Application(spec_dict, config.endpoint_base)


def test_server_wraps_endpoint_function(spec_dict, config):
    from .endpoints import dummy_test_endpoint
    app = Application(spec_dict, config.endpoint_base)
    route = app.routes[0]
    assert route.endpoint is not dummy_test_endpoint
    assert route.endpoint.__wrapped__ is dummy_test_endpoint
    assert not iscoroutinefunction(dummy_test_endpoint)
    assert iscoroutinefunction(route.endpoint)


@pytest.mark.asyncio
async def test_server_wraps_endpoint_function_result_with_jsonresponse(spec_dict, config):

    async def dummy_receive():
        return {'type': 'http.request'}

    app = Application(spec_dict, config.endpoint_base)
    for route in app.routes:
        request = Request({
            'type': 'http',
            'path': app.spec.servers[0].url + route.path,
            'query_string': '',
            'headers': {},
            'app': app,
            'method': 'get',
        }, dummy_receive)
        response = await route.endpoint(request)
        assert isinstance(response, JSONResponse)
