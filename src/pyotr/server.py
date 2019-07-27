from functools import wraps
from importlib import import_module
from inspect import iscoroutinefunction
from pathlib import Path
from typing import Callable, Union

from openapi_core import create_spec
from openapi_core.schema.specs.models import Spec
from openapi_core.shortcuts import RequestValidator, ResponseValidator
from starlette.applications import Starlette
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from starlette.types import ASGIApp
from stringcase import snakecase

from pyotr.utils import get_spec_from_file
from pyotr.validation.requests import StarletteOpenAPIRequest
from pyotr.validation.responses import StarletteOpenAPIResponse


class Application(Starlette):

    def __init__(
        self, spec: Union[Spec, dict], base: str, *, validate_responses: bool = True, **kwargs
    ):
        super().__init__(**kwargs)
        if not isinstance(spec, Spec):
            spec = create_spec(spec)
        self.spec = spec
        self.validate_responses = validate_responses

        self.add_middleware(OpenAPIRequestValidationMiddleware, spec=spec)

        for path, path_spec in spec.paths.items():
            for method, operation in path_spec.operations.items():
                endpoint = self._get_endpoint(operation.operation_id, base)
                self.add_route(path, endpoint, [method])

    def _get_endpoint(self, name: str, base: str, enforce_case: bool = True) -> Callable:
        if '.' in name:
            base, name = f"{base}.{name}".rsplit('.', 1)
        if enforce_case:
            name = snakecase(name)
        try:
            module = import_module(base)
        except ModuleNotFoundError:
            raise RuntimeError(f'The module {base} does not exist!')
        endpoint = getattr(module, name, None)
        if endpoint is None:
            raise RuntimeError(f'The function {base}.{name} does not exist!')

        @wraps(endpoint)
        async def wrapper(request, **kwargs) -> Response:
            if iscoroutinefunction(endpoint):
                response = await endpoint(request, **kwargs)
            else:
                response = endpoint(request, **kwargs)
            if not isinstance(response, Response):
                response = JSONResponse(response)
            # TODO: a list of endpoint names to specify which responses to skip
            if self.validate_responses:
                ResponseValidator(self.spec).validate(
                    StarletteOpenAPIRequest(request),
                    StarletteOpenAPIResponse(response)
                ).raise_for_errors()
            return response

        return wrapper

    @classmethod
    def from_file(cls, path: Union[Path, str], *args, **kwargs) -> 'Application':
        spec = get_spec_from_file(path)
        return cls(spec, *args, **kwargs)


class OpenAPIRequestValidationMiddleware(BaseHTTPMiddleware):

    def __init__(self, app: ASGIApp, spec: Spec, **kwargs):
        super().__init__(app, **kwargs)
        self.spec = spec

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        request = await StarletteOpenAPIRequest.prepare(request)
        request_validation = RequestValidator(self.spec).validate(request)
        request_validation.raise_for_errors()
        response = await call_next(request.request)
        return response
