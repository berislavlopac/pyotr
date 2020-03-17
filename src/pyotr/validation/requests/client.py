from string import Formatter
from urllib.parse import parse_qs, urlsplit, urljoin, urlencode, urlunsplit

from openapi_core.schema.operations.models import Operation
from openapi_core.validation.request.datatypes import RequestParameters, OpenAPIRequest


class ClientOpenAPIRequest(OpenAPIRequest):
    def __init__(self, host_url: str, op_spec: Operation):
        self.spec = op_spec
        self._url_parts = urlsplit(host_url)

        formatter = Formatter()
        self.url_vars = [var for _, var, _, _ in formatter.parse(op_spec.path_name) if var is not None]
        self._path_pattern = self._url_parts.path + op_spec.path_name

        self.full_url_pattern = urljoin(host_url, self._path_pattern)
        self.method = op_spec.http_method.lower()
        self.body = None
        self.parameters = RequestParameters(path={}, query=parse_qs(self._url_parts.query), header={}, cookie={},)
        self.mimetype = NotImplemented

    @property
    def url(self):
        url_parts = self._url_parts._asdict()
        url_parts["path"] = self._path_pattern.format(**self.parameters.path)
        url_parts["query"] = urlencode(self.parameters.query)
        return urlunsplit(url_parts.values())

    def prepare(self, *args, **kwargs):
        len_vars = len(self.url_vars)
        if len(args) != len_vars:
            error_message = f"Incorrect arguments: {self.spec.operation_id} accepts"
            if len_vars:
                error_message += (
                    f" {len_vars} positional argument{'s' if len_vars > 1 else ''}:" f" {', '.join(self.url_vars)}"
                )
            else:
                error_message += f" no positional arguments"
            raise RuntimeError(error_message)
        self.parameters.header = kwargs.pop("headers_", None) or {}
        self.parameters.path = dict(zip(self.url_vars, args))
        self.parameters.query = kwargs
        self.mimetype = self.parameters.header.get("content-type", None)
        return self

    @property
    def headers(self):
        return self.parameters.header
