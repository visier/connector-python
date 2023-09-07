# Copyright 2023 Visier Solutions Inc.

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

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

    def get_members(self, object_id: str, dimension_id: str) -> Response:
        """Get members by object and dimensions id"""
        def call_impl(context: SessionContext) -> Response:
            url = context.mk_url(f"/v1/data/model/analytic-objects/{object_id}/dimensions/{dimension_id}/members")
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
