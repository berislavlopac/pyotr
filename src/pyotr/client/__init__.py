"""Pyotr client."""
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Optional, Protocol, Type, Union

import httpx
from openapi_core import create_spec
from openapi_core.shortcuts import ResponseValidator
from openapi_core.spec.paths import SpecPath
from openapi_core.validation.response.datatypes import OpenAPIResponse
from stringcase import snakecase

from pyotr.utils import get_spec_from_file, OperationSpec
from pyotr.validation.requests import ClientOpenAPIRequest
from pyotr.validation.responses import ClientOpenAPIResponse


class Requestable(Protocol):  # pragma: no cover
    """Defines the `request` method compatible with the `requests` library."""

    def request(self, method: str, url: str, **kwargs) -> Any:
        """Construct and send a `Request`."""
        ...


class Client:
    """Pyotr client class."""

    def __init__(
        self,
        spec: Union[SpecPath, dict],
        *,
        server_url: Optional[str] = None,
        client: Union[ModuleType, Requestable] = httpx,
        request_class: Type[ClientOpenAPIRequest] = ClientOpenAPIRequest,
        response_factory: Callable[[Any], OpenAPIResponse] = ClientOpenAPIResponse,
        headers: Optional[dict] = None,
    ):
        if not isinstance(spec, SpecPath):
            spec = create_spec(spec)
        self.spec = spec
        self.client = client
        self.request_class = request_class
        self.response_factory = response_factory
        self.common_headers = headers or {}

        if server_url is None:
            server_url = self.spec["servers"][0]["url"]
        else:
            server_url = server_url.rstrip("/")
            for server in self.spec["servers"]:
                if server_url == server["url"]:
                    break
            else:
                self.spec["servers"].append({"url": server_url})
        self.server_url = server_url
        self.validator = ResponseValidator(self.spec)

        for operation_id, op_spec in OperationSpec.get_all(spec).items():
            setattr(
                self,
                snakecase(operation_id),
                self._get_operation(op_spec).__get__(self),
            )

    @staticmethod
    def _get_operation(op_spec: OperationSpec):
        # TODO: extract args and kwargs from operation parameters
        def operation(
            self,
            *args,
            body_: Optional[Union[dict, list]] = None,
            headers_: Optional[dict] = None,
            **kwargs,
        ):
            request_headers = self.common_headers.copy()
            request_headers.update(headers_ or {})
            request = self.request_class(self.server_url, op_spec)
            request.prepare(*args, body_=body_, headers_=request_headers, **kwargs)
            request_params = {
                "method": request.method,
                "url": request.url,
                "headers": request.headers,
            }
            if request.body:
                request_params["json" if "json" in request.mimetype else "data"] = request.body
            api_response = self.client.request(**request_params)
            api_response.raise_for_status()
            response = self.response_factory(api_response)
            self.validator.validate(request, response).raise_for_errors()
            return response

        operation.__doc__ = op_spec.spec.get("summary") or op_spec.operation_id
        if description := op_spec.spec.get("description"):
            operation.__doc__ = f"{ operation.__doc__ }\n\n{ description }"
        return operation

    @classmethod
    def from_file(cls, path: Union[Path, str], **kwargs):
        """Creates an instance of the class by loading the spec from a local file."""
        spec = get_spec_from_file(path)
        return cls(spec, **kwargs)
