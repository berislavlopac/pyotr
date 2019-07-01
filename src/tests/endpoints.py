def dummy_test_endpoint(request):
    return {'foo': 'bar'}


async def dummy_test_endpoint_coro(request):
    return {'baz': 123}
