"""Utility classes and functions."""
from __future__ import annotations

import json
from enum import Enum
from itertools import chain
from pathlib import Path
from typing import Callable, Dict, Union

import yaml
from openapi_core.spec.paths import SpecPath
from stringcase import camelcase


class OperationSpec:
    """Utility class for defining API operations."""

    def __init__(self, path: str, method: str, spec: dict):
        self.path = path
        self.method = method
        self.spec = spec

    def __getattr__(self, name):
        """
        Looks for values of the specification fields.

        If the exact match of a name fails, also checks for the camel case version.
        """
        if name in self.spec:
            return self.spec[name]
        if (camelcase_name := camelcase(name)) in self.spec:
            return self.spec[camelcase_name]
        return super().__getattribute__(name)

    @classmethod
    def get_all(cls, spec: dict) -> Dict[str, OperationSpec]:
        """Builds a dict of all operations in the spec."""
        return {
            op_spec["operationId"]: cls(path, method, op_spec)
            for path, path_spec in spec["paths"].items()
            for method, op_spec in path_spec.items()
        }


class SpecFileTypes(tuple, Enum):
    """Supported spec file extensions."""

    JSON = ("json",)
    YAML = ("yaml", "yml")


def get_spec_from_file(path: Union[Path, str]) -> SpecPath:
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
