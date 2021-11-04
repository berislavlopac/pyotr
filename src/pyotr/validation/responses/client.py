"""Client responses."""
from openapi_core.validation.response.datatypes import OpenAPIResponse


class ClientOpenAPIResponseFactory(object):
    """Client response factory."""

    @classmethod
    def create(cls, response):
        """Create client response."""
        return OpenAPIResponse(
            data=response.content,
            status_code=response.status_code,
            mimetype=response.headers.get("content-type"),
        )
