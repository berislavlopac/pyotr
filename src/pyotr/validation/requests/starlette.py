from urllib.parse import urljoin

from openapi_core.validation.request.datatypes import RequestParameters, OpenAPIRequest
from starlette.routing import Match


class StarletteOpenAPIRequestFactory:

    @classmethod
    async def create(cls, request):
        path_pattern = request["path"]
        for route in request.app.router.routes:
            match, _ = route.matches(request)
            if match == Match.FULL:
                path_pattern = route.path
                break

        host_url = f"{request.url.scheme}://{request.url.hostname}"
        if request.url.port:
            host_url = f"{host_url}:{request.url.port}"

        parameters = RequestParameters(
            path=request.path_params,
            query=request.query_params,
            header=request.headers,
            cookie=request.cookies,
        )

        return OpenAPIRequest(
            full_url_pattern=urljoin(host_url, path_pattern),
            method=request.method.lower(),
            parameters=parameters,
            body=await request.body(),
            mimetype=request.headers.get("content-type"),
        )
