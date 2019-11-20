from functools import wraps
from importlib import import_module
from inspect import iscoroutinefunction
from pathlib import Path
from types import ModuleType
from typing import Callable, Union
from urllib.parse import urlsplit

from openapi_core import create_spec
from openapi_core.schema.specs.models import Spec
from openapi_core.shortcuts import RequestValidator, ResponseValidator
from starlette.applications import Starlette
from starlette.responses import JSONResponse, Response
from stringcase import snakecase

from pyotr.utils import get_spec_from_file
from pyotr.validation.requests import StarletteOpenAPIRequest
from pyotr.validation.responses import StarletteOpenAPIResponse


class Application(Starlette):

    def __init__(
        self, spec: Union[Spec, dict], base: Union[str, ModuleType], *,
        validate_responses: bool = True, ignore_server_paths: bool = False, **kwargs
    ):
        super().__init__(**kwargs)
        if not isinstance(spec, Spec):
            spec = create_spec(spec)
        self.spec = spec
        self.validate_responses = validate_responses
        server_paths = {''}
        if not ignore_server_paths:
            server_paths = {
                urlsplit(server.url).path for server in self.spec.servers
            }

        if isinstance(base, str):
            base = _load_module(base)

        for path, path_spec in spec.paths.items():
            for method, operation in path_spec.operations.items():
                endpoint = self._get_endpoint(operation.operation_id, base)
                for server_path in server_paths:
                    self.add_route(server_path + path, endpoint, [method])

    def _get_endpoint(self, name: str, module: ModuleType, enforce_case: bool = True) -> Callable:
        if '.' in name:
            base, name = name.rsplit('.', 1)
            module = _load_module(f'{module.__name__}.{base}')
        if enforce_case:
            name = snakecase(name)
        try:
            endpoint = getattr(module, name)
        except AttributeError as e:
            raise RuntimeError(f'The function `{module}.{name}` does not exist!') from e

        @wraps(endpoint)
        async def wrapper(request, **kwargs) -> Response:
            validation_request = await StarletteOpenAPIRequest.prepare(request)
            request_validation = RequestValidator(self.spec).validate(validation_request)
            request_validation.raise_for_errors()

            if iscoroutinefunction(endpoint):
                response = await endpoint(request, **kwargs)
            else:
                response = endpoint(request, **kwargs)
            if isinstance(response, dict):
                response = JSONResponse(response)

            # TODO: pass a list of endpoint names to specify which responses to skip
            if self.validate_responses:
                ResponseValidator(self.spec).validate(
                    validation_request, StarletteOpenAPIResponse(response)
                ).raise_for_errors()
            return response

        return wrapper

    @classmethod
    def from_file(cls, path: Union[Path, str], *args, **kwargs) -> 'Application':
        spec = get_spec_from_file(path)
        return cls(spec, *args, **kwargs)


def _load_module(name: str) -> ModuleType:
    try:
        module = import_module(name)
    except ModuleNotFoundError as e:
        raise RuntimeError(f'The module `{name}` does not exist!') from e
    else:
        return module
