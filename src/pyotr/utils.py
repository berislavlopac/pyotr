"""Utility classes and functions."""

import json
from enum import Enum
from itertools import chain
from pathlib import Path
from typing import Any, Union, Callable

import yaml
from openapi_core.schema.specs.models import Spec
from typing_extensions import Protocol


class SpecFileTypes(tuple, Enum):
    """Supported spec file extensions."""

    JSON = ("json",)
    YAML = ("yaml", "yml")


def get_spec_from_file(path: Union[Path, str]) -> Spec:
    """Loads a local file and creates an OpenAPI `Spec` object."""
    path = Path(path)
    suffix = path.suffix[1:].lower()

    if suffix in SpecFileTypes.JSON:
        spec_load: Callable = json.load
    elif suffix in SpecFileTypes.YAML:
        spec_load = yaml.safe_load
    else:
        raise RuntimeError(
            f"Unknown specification file type."
            f" Accepted types: {', '.join(chain(*SpecFileTypes))}"
        )

    with open(path) as spec_file:
        return spec_load(spec_file)


class Requestable(Protocol):  # pragma: no cover
    """Implements the `request` method compatible with the `requests` library."""

    def request(self, method: str, url: str, **kwargs) -> Any:
        """Construct and send a `Request`."""
        ...
