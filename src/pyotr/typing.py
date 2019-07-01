from typing import Any

from typing_extensions import Protocol


class Requestable(Protocol):  # pragma: no cover
    """ Any object (usually a module, class or instance) that implements the
        `request` method compatible with the `requests` library.
    """
    def request(method: str, url: str, **kwargs) -> Any:
        ...
