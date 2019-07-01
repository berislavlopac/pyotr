import json
from enum import Enum
from itertools import chain
from pathlib import Path
from typing import Union

import yaml
from openapi_core.schema.specs.models import Spec


class SpecFileTypes(Enum):
    JSON = ('json',)
    YAML = ('yaml', 'yml')


def get_spec_from_file(path: Union[Path, str]) -> Spec:
    path = Path(path)
    suffix = path.suffix[1:].lower()
    with open(path) as spec_file:
        if suffix in SpecFileTypes.JSON.value:
            spec = json.load(spec_file)
        elif suffix in SpecFileTypes.YAML.value:
            spec = yaml.safe_load(spec_file)
        else:
            raise RuntimeError(
                f"Unknown specification file type."
                f" Accepted types: {', '.join(chain(*(i.value for i in SpecFileTypes)))}"
            )
    return spec
