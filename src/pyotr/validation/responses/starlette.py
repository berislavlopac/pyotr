from openapi_core.wrappers.base import BaseOpenAPIResponse
from starlette.responses import Response


class StarletteOpenAPIResponse(BaseOpenAPIResponse):

    def __init__(self, response: Response):
        self.body = response.body
        self.status_code = response.status_code
        self.mimetype = response.headers.get('content-type')
        self.data = self.body
