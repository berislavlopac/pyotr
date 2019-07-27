from openapi_core.wrappers.base import BaseOpenAPIRequest
from starlette.requests import Request
from starlette.routing import Match


class StarletteOpenAPIRequest(BaseOpenAPIRequest):

    def __init__(self, request: Request):
        self.request = request
        self.body = b''

    @classmethod
    async def prepare(cls, request):
        req = cls(request)
        req.body = await req.request.body()
        return req

    @property
    def host_url(self):
        url = f"{self.request.url.scheme}://{self.request.url.hostname}"
        if self.request.url.port:
            url = f"{url}:{self.request.url.port}"
        return url

    @property
    def path(self):
        return self.request['path']

    @property
    def method(self):
        return self.request.method.lower()

    @property
    def path_pattern(self):
        for route in self.request.app.router.routes:
            match, _ = route.matches(self.request)
            if match == Match.FULL:
                return route.path
        return self.path

    @property
    def parameters(self):
        return {
            'path': self.request.path_params,
            'query': self.request.query_params,
            'header': self.request.headers,
            'cookie': self.request.cookies,
        }

    @property
    def mimetype(self):
        return self.request.headers['content-type']
