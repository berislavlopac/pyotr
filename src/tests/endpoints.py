def dummy_test_endpoint(request):
    return {"foo": "bar"}


def dummy_test_endpoint_with_argument(request):
    return {"foo": request.path_params["test_arg"]}


async def dummy_test_endpoint_coro(request):
    return {"baz": 123}
