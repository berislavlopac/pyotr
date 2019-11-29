from inspect import iscoroutinefunction

import pytest
from starlette.requests import Request
from starlette.responses import JSONResponse

from pyotr.server import Application


@pytest.mark.parametrize("filename", ("openapi.json", "openapi.yaml"))
def test_server_from_file(config, filename):
    file_path = config.test_dir / filename
    app = Application.from_file(file_path, endpoints=config.endpoint_base)
    assert app.spec.info.title == "Test Spec"


def test_server_from_file_raises_exception_if_unknown_type(config):
    file_path = config.test_dir / "openapi.unknown"
    with pytest.raises(RuntimeError):
        Application.from_file(file_path)


def test_server_dotted_endpoint_name(spec_dict):
    spec_dict["paths"]["/test"]["get"]["operationId"] = "endpoints.dummyTestEndpoint"
    spec_dict["paths"]["/test/{test_arg}"]["get"]["operationId"] = "endpoints.dummyTestEndpointWithArgument"
    spec_dict["paths"]["/test-async"]["get"]["operationId"] = "endpoints.dummyTestEndpointCoro"
    app = Application(spec_dict, endpoints="tests")
    route = app.routes[0]
    assert callable(route.endpoint)
    assert route.endpoint.__name__ == "dummy_test_endpoint"
    assert route.path == "/test"


def test_server_endpoints_as_module(spec_dict):
    from tests import endpoints

    app = Application(spec_dict, endpoints=endpoints)
    route = app.routes[0]
    assert callable(route.endpoint)
    assert route.endpoint.__name__ == "dummy_test_endpoint"
    assert route.path == "/test"


def test_server_endpoints_as_module_dotted_endpoint_name(spec_dict):
    import tests

    spec_dict["paths"]["/test"]["get"]["operationId"] = "endpoints.dummyTestEndpoint"
    spec_dict["paths"]["/test/{test_arg}"]["get"]["operationId"] = "endpoints.dummyTestEndpointWithArgument"
    spec_dict["paths"]["/test-async"]["get"]["operationId"] = "endpoints.dummyTestEndpointCoro"
    app = Application(spec_dict, endpoints=tests)
    route = app.routes[0]
    assert callable(route.endpoint)
    assert route.endpoint.__name__ == "dummy_test_endpoint"
    assert route.path == "/test"


def test_server_with_path(spec_dict):
    from tests import endpoints

    spec_dict["servers"].insert(0, {"url": "http://localhost:8001/with/path"})
    app = Application(spec_dict, endpoints=endpoints)
    expected_routes = {
        "/test",
        "/test/{test_arg}",
        "/with/path/test",
        "/test-async",
        "/with/path/test/{test_arg}",
        "/with/path/test-async",
    }
    assert {route.path for route in app.routes} == expected_routes


def test_server_no_endpoint_module(spec_dict):
    with pytest.raises(RuntimeError):
        Application(spec_dict, endpoints="foo.bar")


def test_server_no_endpoint_function(spec_dict, config):
    spec_dict["paths"]["/test"]["get"]["operationId"] = "fooBar"
    with pytest.raises(RuntimeError):
        Application(spec_dict, endpoints=config.endpoint_base)


def test_server_wraps_endpoint_function(spec_dict, config):
    from .endpoints import dummy_test_endpoint

    app = Application(spec_dict, endpoints=config.endpoint_base)
    route = app.routes[0]
    assert route.endpoint is not dummy_test_endpoint
    assert route.endpoint.__wrapped__ is dummy_test_endpoint
    assert not iscoroutinefunction(dummy_test_endpoint)
    assert iscoroutinefunction(route.endpoint)


@pytest.mark.asyncio
async def test_server_wraps_endpoint_function_result_with_jsonresponse(spec_dict, config):
    async def dummy_receive():
        return {"type": "http.request"}

    app = Application(spec_dict, endpoints=config.endpoint_base)
    for route in app.routes:
        if route.path == "/test":
            break
    request = Request(
        {
            "type": "http",
            "path": app.spec.servers[0].url + route.path,
            "query_string": "",
            "headers": {},
            "app": app,
            "method": "get",
        },
        dummy_receive,
    )
    response = await route.endpoint(request)
    assert isinstance(response, JSONResponse)


@pytest.mark.asyncio
async def test_server_wraps_async_endpoint_function_result_with_jsonresponse(spec_dict, config):
    async def dummy_receive():
        return {"type": "http.request"}

    app = Application(spec_dict, endpoints=config.endpoint_base)
    for route in app.routes:
        if route.path == "/test-async":
            break
    request = Request(
        {
            "type": "http",
            "path": app.spec.servers[0].url + route.path,
            "query_string": "",
            "headers": {},
            "app": app,
            "method": "get",
        },
        dummy_receive,
    )
    response = await route.endpoint(request)
    assert isinstance(response, JSONResponse)


def test_init_base_argument_is_optional(spec_dict):
    app = Application(spec_dict)
    assert app.routes == []
