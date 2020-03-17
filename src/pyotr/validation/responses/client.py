from openapi_core.validation.response.datatypes import OpenAPIResponse


class ClientOpenAPIResponseFactory(object):
    @classmethod
    def create(cls, response):
        oapi_response = OpenAPIResponse(
            data=response.content, status_code=response.status_code, mimetype=response.headers.get("content-type"),
        )
        oapi_response.payload = response.json()
        return oapi_response
