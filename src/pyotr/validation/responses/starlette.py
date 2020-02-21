from openapi_core.validation.response.datatypes import OpenAPIResponse


class StarletteOpenAPIResponseFactory:

    @classmethod
    def create(cls, response):
        return OpenAPIResponse(
            data=response.body,
            status_code=response.status_code,
            mimetype=response.headers.get("content-type"),
        )
