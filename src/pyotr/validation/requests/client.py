"""Pyotr API client."""
from __future__ import annotations
from string import Formatter
from urllib.parse import parse_qs, urlencode, urljoin, urlsplit, urlunsplit
from typing import Optional, Mapping

from openapi_core.schema.operations.models import Operation
from openapi_core.validation.request.datatypes import OpenAPIRequest, RequestParameters


class ClientOpenAPIRequest(OpenAPIRequest):
    """Client request."""

    def __init__(self, host_url: str, op_spec: Operation):
        self.spec = op_spec
        self._url_parts = urlsplit(host_url)

        formatter = Formatter()
        self.url_vars = [
            var for _, var, _, _ in formatter.parse(op_spec.path_name) if var is not None
        ]
        self._path_pattern = self._url_parts.path + op_spec.path_name

        self.full_url_pattern = urljoin(host_url, self._path_pattern)
        self.method = op_spec.http_method.lower()
        self.body: Mapping = {}
        self.parameters = RequestParameters(
            path={},
            query=parse_qs(self._url_parts.query),
            header={},
            cookie={},
        )
        self.mimetype = list(op_spec.request_body.content)[0] if op_spec.request_body else None

    @property
    def url(self):
        """Request URL."""
        url_parts = self._url_parts._asdict()
        url_parts["path"] = self._path_pattern.format(**self.parameters.path)
        url_parts["query"] = urlencode(self.parameters.query)
        return urlunsplit(tuple(url_parts.values()))

    def prepare(
        self,
        *args,
        body_: Optional[Mapping] = None,
        headers_: Optional[Mapping] = None,
        **kwargs,
    ) -> ClientOpenAPIRequest:
        """
        Prepare request.

        Arguments:
            *args: Positional arguments are inserted into the URL.
            body_: Optional request body.
            headers_: Optional request headers.
            **kwargs: The keyword arguments are converted to query arguments.
        """
        self._set_path_params(*args)
        if headers_ is not None:
            self.parameters.header.update(headers_)
        self.parameters.query = kwargs
        if body_ is not None:
            self.body = body_
        content_type_header = self.parameters.header.pop("content-type", None)
        if content_type_header:
            self.mimetype = content_type_header
        return self

    def _set_path_params(self, *args):
        len_vars = len(self.url_vars)
        if len(args) != len_vars:
            error_message = f"Incorrect arguments: {self.spec.operation_id} accepts"
            if len_vars:
                error_message += (
                    f" {len_vars} positional argument{'s' if len_vars > 1 else ''}:"
                    f" {', '.join(self.url_vars)}"
                )
            else:
                error_message += " no positional arguments"
            raise RuntimeError(error_message)
        self.parameters.path = dict(zip(self.url_vars, args))

    @property
    def headers(self):
        """Request headers."""
        return self.parameters.header
