from collections import namedtuple
from functools import wraps
from importlib import import_module
from inspect import iscoroutinefunction
from pathlib import Path
from types import ModuleType
from typing import Callable, Union, Optional
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

Operation = namedtuple("Operation", "path method")


class Application(Starlette):
    def __init__(
        self,
        spec: Union[Spec, dict],
        *,
        module: Optional[Union[str, ModuleType]] = None,
        validate_responses: bool = True,
        enforce_case: bool = True,
        **kwargs,
    ):
        super().__init__(**kwargs)
        if not isinstance(spec, Spec):
            spec = create_spec(spec)
        self.spec = spec
        self.validate_responses = validate_responses
        self.enforce_case = enforce_case
        self._server_paths = {urlsplit(server.url).path for server in self.spec.servers}

        self._operations = {
            oper.operation_id: Operation(path, method)
            for path, path_spec in spec.paths.items()
            for method, oper in path_spec.operations.items()
        }

        if module is not None:
            if isinstance(module, str):
                module = _load_module(module)

            for operation_id, operation in self._operations.items():
                name = operation_id
                if "." in name:
                    base, name = name.rsplit(".", 1)
                    base_module = _load_module(f"{module.__name__}.{base}")
                else:
                    base_module = module
                if self.enforce_case:
                    name = snakecase(name)
                try:
                    endpoint_fn = getattr(base_module, name)
                except AttributeError as e:
                    raise RuntimeError(f"The function `{base_module}.{name}` does not exist!") from e
                self.set_endpoint(endpoint_fn, operation_id=operation_id)

    def set_endpoint(self, endpoint_fn: Callable, *, operation_id: Optional[str] = None):
        if operation_id is None:
            operation_id = endpoint_fn.__name__
        if self.enforce_case and operation_id not in self._operations:
            operation_id = {snakecase(op_id): op_id for op_id in self._operations}.get(operation_id)
        try:
            operation = self._operations[operation_id]
        except KeyError as e:
            raise ValueError(f"Unknown operationId: {operation_id}.") from e

        @wraps(endpoint_fn)
        async def wrapper(request, **kwargs) -> Response:
            validation_request = await StarletteOpenAPIRequest.prepare(request)
            request_validation = RequestValidator(self.spec).validate(validation_request)
            request_validation.raise_for_errors()

            if iscoroutinefunction(endpoint_fn):
                response = await endpoint_fn(request, **kwargs)
            else:
                response = endpoint_fn(request, **kwargs)
            if isinstance(response, dict):
                response = JSONResponse(response)

            # TODO: pass a list of operation IDs to specify which responses not to validate
            if self.validate_responses:
                ResponseValidator(self.spec).validate(
                    validation_request, StarletteOpenAPIResponse(response)
                ).raise_for_errors()
            return response

        for server_path in self._server_paths:
            self.add_route(server_path + operation.path, wrapper, [operation.method])

    def endpoint(self, operation_id: Union[Callable, str]):
        """ Decorator for setting endpoints.
        """
        if callable(operation_id):
            self.set_endpoint(operation_id)
            return operation_id
        else:

            def decorator(fn):
                self.set_endpoint(fn, operation_id=operation_id)
                return fn

            return decorator

    @classmethod
    def from_file(cls, path: Union[Path, str], *args, **kwargs) -> "Application":
        spec = get_spec_from_file(path)
        return cls(spec, *args, **kwargs)


def _load_module(name: str) -> ModuleType:
    """ Helper function to load module based on its dotted-string name.
    """
    try:
        module = import_module(name)
    except ModuleNotFoundError as e:
        raise RuntimeError(f"The module `{name}` does not exist!") from e
    else:
        return module
