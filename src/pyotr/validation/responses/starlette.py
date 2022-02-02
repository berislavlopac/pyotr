"""Starlette responses."""
from openapi_core.validation.response.datatypes import OpenAPIResponse


class StarletteOpenAPIResponseFactory:
    """Starlette response factory."""

    @classmethod
    def create(cls, response):
        """Create Starlette response."""
        mimetype, *_ = response.headers.get("content-type", "").split(";")
        return OpenAPIResponse(
            data=response.body,
            status_code=response.status_code,
            mimetype=mimetype,
        )
