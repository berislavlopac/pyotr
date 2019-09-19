from pathlib import Path
from typing import Optional, Type, Union

import httpx
from openapi_core import create_spec
from openapi_core.schema.specs.models import Spec
from openapi_core.shortcuts import ResponseValidator
from stringcase import snakecase

from pyotr.typing import Requestable
from pyotr.utils import get_spec_from_file
from pyotr.validation.requests import ClientOpenAPIRequest
from pyotr.validation.responses import ClientOpenAPIResponse


class Client:

    def __init__(self, spec: Union[Spec, dict], *,
                 server_url: Optional[str] = None,
                 client: Requestable = httpx,
                 request_class: Type[ClientOpenAPIRequest] = ClientOpenAPIRequest,
                 response_class: Type[ClientOpenAPIResponse] = ClientOpenAPIResponse
                 ):
        if not isinstance(spec, Spec):
            spec = create_spec(spec)
        self.spec = spec
        self.client = client
        self.request_class = request_class
        self.response_class = response_class

        if server_url is None:
            server_url = self.spec.servers[0].url
        server_url = server_url.rstrip('/')
        if server_url not in self.spec.servers:
            self.spec.servers.append(server_url)
        self.server_url = server_url

        self.operations = {
            snakecase(op_spec.operation_id): self._get_operation(op_spec)
            for path_spec in spec.paths.values()
            for op_spec in path_spec.operations.values()
        }
        self.validator = ResponseValidator(self.spec)

    def __getattr__(self, item):
        try:
            return self.operations[item]
        except KeyError:
            raise AttributeError(f'Incorrect operation: {item}')

    def _get_operation(self, op_spec):
        def operation(*args,
                      body_: Optional[Union[dict, list]] = None,
                      headers_: Optional[dict] = None,
                      **kwargs
                      ):
            request = self.request_class(self.server_url, op_spec)
            request.prepare(*args, data_=body_, headers_=headers_, **kwargs)
            api_response = self.client.request(
                method=request.method, url=request.url, data=request.body
            )
            api_response.raise_for_status()
            response = self.response_class(api_response)
            self.validator.validate(request, response).raise_for_errors()
            return response
        return operation

    @classmethod
    def from_file(cls, path: Union[Path, str], **kwargs):
        spec = get_spec_from_file(path)
        return cls(spec, **kwargs)
