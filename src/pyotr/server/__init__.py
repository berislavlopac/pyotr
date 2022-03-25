"""Pyotr server."""
from functools import wraps
from http import HTTPStatus
from importlib import import_module
from inspect import iscoroutine
from pathlib import Path
from types import ModuleType
from typing import Callable, Optional, Union
from urllib.parse import urlsplit

from openapi_core import create_spec
from openapi_core.exceptions import OpenAPIError
from openapi_core.shortcuts import RequestValidator, ResponseValidator
from openapi_core.spec.paths import SpecPath
from openapi_core.validation.exceptions import InvalidSecurity
from starlette.applications import Starlette
from starlette.exceptions import HTTPException
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from stringcase import snakecase

from pyotr.utils import get_spec_from_file, OperationSpec
from pyotr.validation.requests import StarletteOpenAPIRequest
from pyotr.validation.responses import StarletteOpenAPIResponse


class Application(Starlette):
    """Pyotr server application."""

    def __init__(
        self,
        spec: Union[SpecPath, dict],
        *,
        module: Optional[Union[str, ModuleType]] = None,
        validate_responses: bool = True,
        enforce_case: bool = True,
        **kwargs,
    ):
        super().__init__(**kwargs)
        if not isinstance(spec, SpecPath):
            spec = create_spec(spec)
        self.spec = spec
        self.validate_responses = validate_responses
        self.enforce_case = enforce_case
        self.custom_formatters = None
        self.custom_media_type_deserializers = None

        self._operations = OperationSpec.get_all(self.spec)
        self._server_paths = {urlsplit(server["url"]).path for server in self.spec["servers"]}

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
                    raise RuntimeError(
                        f"The function `{base_module}.{name}` does not exist!"
                    ) from e
                self.set_endpoint(endpoint_fn, operation_id=operation_id)

    def set_endpoint(self, endpoint_fn: Callable, *, operation_id: Optional[str] = None):
        """Sets endpoint function for a given `operationId`.

        If the `operation_id` is not given, it will try to determine it
        based on the function name.
        """
        if operation_id is None:
            operation_id = endpoint_fn.__name__
        if self.enforce_case and operation_id not in self._operations:
            operation_id_key = {snakecase(op_id): op_id for op_id in self._operations}.get(
                operation_id
            )
        else:
            operation_id_key = operation_id
        try:
            operation = self._operations[operation_id_key]
        except KeyError as ex:
            raise ValueError(f"Unknown operationId: {operation_id}.") from ex

        @wraps(endpoint_fn)
        async def wrapper(request: Request, **kwargs) -> Response:
            openapi_request = await StarletteOpenAPIRequest(request)
            validated_request = RequestValidator(
                self.spec,
                custom_formatters=self.custom_formatters,
                custom_media_type_deserializers=self.custom_media_type_deserializers,
            ).validate(openapi_request)
            try:
                validated_request.raise_for_errors()
            except InvalidSecurity as ex:
                raise HTTPException(HTTPStatus.FORBIDDEN, "Invalid security.") from ex
            except OpenAPIError as ex:
                raise HTTPException(HTTPStatus.BAD_REQUEST, "Bad request") from ex

            response = endpoint_fn(request, **kwargs)
            if iscoroutine(response):
                response = await response
            if isinstance(response, dict):
                response = JSONResponse(response)
            elif not isinstance(response, Response):
                raise ValueError(
                    f"The endpoint function `{endpoint_fn.__name__}` must return"
                    " either a dict or a Starlette Response instance."
                )

            # TODO: pass a list of operation IDs to specify which responses not to validate
            if self.validate_responses:
                ResponseValidator(
                    self.spec,
                    custom_formatters=self.custom_formatters,
                    custom_media_type_deserializers=self.custom_media_type_deserializers,
                ).validate(
                    openapi_request, StarletteOpenAPIResponse(response)
                ).raise_for_errors()
            return response

        for server_path in self._server_paths:
            self.add_route(
                server_path + operation.path, wrapper, [operation.method], name=operation_id
            )

    def endpoint(self, operation_id: Union[Callable, str]):
        """Decorator for setting endpoints.

        If used without arguments, it will try to determine the `operationId` based on the
        decorated function name:

            @app.endpoint
            def foo_bar(request):
                # sets the endpoint for operationId fooBar

        Otherwise, the `operationId` can be set explicitly:

            @app.endpoint('fooBar'):
            def my_endpoint():
                ...
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
        """Creates an instance of the class by loading the spec from a local file."""
        spec = get_spec_from_file(path)
        return cls(spec, *args, **kwargs)


def _load_module(name: str) -> ModuleType:
    """Helper function to load module based on its dotted-string name."""
    try:
        module = import_module(name)
    except ModuleNotFoundError as e:
        raise RuntimeError(f"The module `{name}` does not exist!") from e
    else:
        return module
