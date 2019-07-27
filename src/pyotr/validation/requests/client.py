from string import Formatter
from urllib.parse import parse_qs, urlencode, urlsplit, urlunsplit

from openapi_core.schema.operations.models import Operation
from openapi_core.wrappers.base import BaseOpenAPIRequest


class ClientOpenAPIRequest(BaseOpenAPIRequest):

    def __init__(self, host_url: str, op_spec: Operation):
        self.spec = op_spec
        self.method = op_spec.http_method.lower()

        self.host_url = host_url
        self._url_parts = urlsplit(self.host_url)

        self.path_pattern = op_spec.path_name

        self.parameters = {
            'path': {},
            'query': parse_qs(self._url_parts.query),
            'header': {},
            'cookie': {},
        }
        self.body = None

        self.mimetype = NotImplemented

        formatter = Formatter()
        self.url_vars = [
            var for _, var, _, _
            in formatter.parse(op_spec.path_name)
            if var is not None
        ]

    @property
    def url(self):
        url_parts = self._url_parts._asdict()
        url_parts['path'] += self.path
        url_parts['query'] = urlencode(self.parameters['query'])
        return urlunsplit(url_parts.values())

    @property
    def path(self):
        return self.spec.path_name.format(**self.parameters['path'])

    def prepare(self, *args, **kwargs):
        len_vars = len(self.url_vars)
        if len(args) != len_vars:
            error_message = f"Incorrect arguments: {self.spec.operation_id} accepts"
            if len_vars:
                error_message += (
                    f" {len_vars} positional argument{'s' if len_vars > 1 else ''}:"
                    f" {', '.join(self.url_vars)}"
                )
            else:
                error_message += f" no positional arguments"
            raise RuntimeError(error_message)

        self.body = kwargs.pop('data_', None)

        headers = kwargs.pop('headers_', None)
        self.parameters.update({
            'path': dict(zip(self.url_vars, args)),
            'query': kwargs,
            'header': headers
        })

        return self
