from openapi_core.wrappers.base import BaseOpenAPIResponse


class ClientOpenAPIResponse(BaseOpenAPIResponse):

    def __init__(self, response):
        self.response = response

    @property
    def body(self):
        return self.response.content

    @property
    def data(self):
        return self.body

    @property
    def status_code(self):
        return self.response.status_code

    @property
    def mimetype(self):
        return self.response.headers.get('content-type')

    @property
    def payload(self):
        return self.response.json()
