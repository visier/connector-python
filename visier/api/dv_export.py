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
API client for the Visier DV Export API.
"""
from requests import Response
from visier.api.base import ApiClientBase
from visier.connector import SessionContext
import json

BASE_PATH = "/v1alpha/data/data-version-exports"

class DVExportApiClient(ApiClientBase):
    """API client for the Visier DV Export API."""

    def schedule_initial_data_version_export_job(self, data_version_number: int) -> Response:
        def call_impl(context: SessionContext) -> Response:
            url = context.mk_url(f"{BASE_PATH}/jobs")
            payload = {'dataVersionNumber': str(data_version_number)}
            headers = context.mk_headers()
            headers['Content-Type'] = "application/json"
            return context.session().post(url, headers=headers, data=json.dumps(payload))
        return self.run(call_impl)

    def schedule_delta_data_version_export_job(self,
                                               data_version_number: int,
                                               base_data_version_number: int) -> Response:
        def call_impl(context: SessionContext) -> Response:
            url = context.mk_url(f"{BASE_PATH}/jobs")
            payload = {'dataVersionNumber': str(data_version_number), 'baseDataVersionNumber': str(base_data_version_number)}
            headers = context.mk_headers()
            headers['Content-Type'] = "application/json"
            return context.session().post(url, headers=headers, data=json.dumps(payload))
        return self.run(call_impl)

    def get_data_version_export_job_status(self, job_id: str) -> Response:
        def call_impl(context: SessionContext) -> Response:
            url = context.mk_url(f"{BASE_PATH}/jobs/{job_id}")
            return context.session().get(url, headers=context.mk_headers())

        return self.run(call_impl)

    def get_dava_version_export_metadata(self, export_id: str):
        def call_impl(context: SessionContext) -> Response:
            url = context.mk_url(f"{BASE_PATH}/exports/{export_id}")
            return context.session().get(url, headers=context.mk_headers())

        return self.run(call_impl)

    def get_data_versions_available_for_export(self) -> Response:
        def call_impl(context: SessionContext) -> Response:
            url = context.mk_url(f"{BASE_PATH}/availableDataVersions")
            return context.session().get(url, headers=context.mk_headers())

        return self.run(call_impl)

    def get_available_data_version_exports(self) -> Response:
        def call_impl(context: SessionContext) -> Response:
            url = context.mk_url(f"{BASE_PATH}/exports")
            return context.session().get(url, headers=context.mk_headers())
        return self.run(call_impl)

    def get_export_file(self, export_id: str, file_id: str) -> Response:
        def call_impl(context: SessionContext) -> Response:
            url = context.mk_url(f"{BASE_PATH}/exports/{export_id}/files/{file_id}")
            return context.session().get(url, headers=context.mk_headers())
        return self.run(call_impl)
