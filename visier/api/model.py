# This file is part of visier-connector-python.
#
# visier-connector-python is free software: you can redistribute it and/or modify
# it under the terms of the Apache License, Version 2.0 (the "License").
#
# visier-connector-python is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# Apache License, Version 2.0 for more details.
#
# You should have received a copy of the Apache License, Version 2.0
# along with visier-connector-python. If not, see <https://www.apache.org/licenses/LICENSE-2.0>.

"""
API client for the Visier Model API.
"""

from typing import List
import urllib.parse as urlparse
from requests import Response
from visier.connector import SessionContext
from .base import ApiClientBase


class ModelApiClient(ApiClientBase):
    """API client for the Visier Model API."""
    def get_analytic_objects(self, ids: List[str] = None) -> Response:
        """Get analytic objects by id"""
        def call_impl(context: SessionContext) -> Response:
            args = _ids_as_url_args(ids)
            url = context.mk_url(f"/v1/data/model/analytic-objects{args}")
            return _get_with_header(context, url)
        return self.run(call_impl)

    def get_dimensions(self, object_id: str, ids: List[str] = None) -> Response:
        """Get dimensions by id"""
        def call_impl(context: SessionContext) -> Response:
            args = _ids_as_url_args(ids)
            url = context.mk_url(f"/v1/data/model/analytic-objects/{object_id}/dimensions{args}")
            return _get_with_header(context, url)
        return self.run(call_impl)

    def get_selection_concepts(self, object_id: str, ids: List[str] = None) -> Response:
        """Get concepts by id"""
        def call_impl(context: SessionContext) -> Response:
            args = _ids_as_url_args(ids)
            url = context.mk_url(f"/v1/data/model/analytic-objects/{object_id}/selection-concepts{args}")
            return _get_with_header(context, url)
        return self.run(call_impl)

    def get_properties(self, object_id: str, ids: List[str] = None) -> Response:
        """Get properties by id"""
        def call_impl(context: SessionContext) -> Response:
            args = _ids_as_url_args(ids)
            url = context.mk_url(f"/v1/data/model/analytic-objects/{object_id}/properties{args}")
            return _get_with_header(context, url)
        return self.run(call_impl)

    def get_metrics(self, ids: List[str] = None) -> Response:
        """Get metrics by id"""
        def call_impl(context: SessionContext) -> Response:
            args = _ids_as_url_args(ids)
            url = context.mk_url(f"/v1/data/model/metrics{args}")
            return _get_with_header(context, url)
        return self.run(call_impl)

    def get_metric_dimensions(self, metric_id: str) -> Response:
        """Get dimensions by id"""
        def call_impl(context: SessionContext) -> Response:
            url = context.mk_url(f"/v1/data/model/metrics/{metric_id}/dimensions")
            return _get_with_header(context, url)
        return self.run(call_impl)

    def get_metric_selection_concepts(self, metric_id: str) -> Response:
        """Get concepts by id"""
        def call_impl(context: SessionContext) -> Response:
            url = context.mk_url(f"/v1/data/model/metrics/{metric_id}/selection-concepts")
            return _get_with_header(context, url)
        return self.run(call_impl)


def _get_with_header(context: SessionContext, url: str) -> Response:
    """Invokes the Model GET request on the provided url with the provided headers."""
    return context.session().get(url, headers=context.mk_headers())

def _ids_as_url_args(ids: List[str]) -> str:
    """Constructs a URL argument string from a list of ids."""
    if (ids and len(ids) > 0):
        args = "&id=".join([urlparse.quote_plus(id) for id in ids])
        return f"?id={args}"
    return ""
