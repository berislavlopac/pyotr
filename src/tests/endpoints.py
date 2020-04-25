import json
from http import HTTPStatus

from starlette.responses import Response


def dummy_test_endpoint(request):
    return {"foo": "bar"}


def dummy_test_endpoint_with_argument(request):
    return {"foo": request.path_params["test_arg"]}


async def dummy_test_endpoint_coro(request):
    return {"baz": 123}


async def dummy_post_endpoint(request):
    body = await request.body()
    assert json.loads(body.decode()) == {"foo": "bar"}
    return Response(status_code=HTTPStatus.NO_CONTENT.value)


async def endpoint_returning_nothing(request):
    ...
