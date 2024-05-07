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
API client for the Visier Data Version Export API.
"""
import json
from requests import Response
from visier.api.base import ApiClientBase
from visier.connector import SessionContext

BASE_PATH = "/v1alpha/data/data-version-exports"

class DVExportApiClient(ApiClientBase):
    """API client for the Visier Data Version Export API."""

    def schedule_initial_data_version_export_job(self, data_version_number: int) -> Response:
        """
        Schedule an initial data version export job. You might want to run an initial data version export job if you are
        creating an initial data store for the data version export. The information returned through
        `get_data_version_export_metadata` contains all the required details to create new tables.
        :param data_version_number: The DV number you want to export.
        """
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
        """
        Schedule a delta data version export job. Run a delta data version export job if you already
        exported an initial data version and want to export the changes between ``data_version_number``
        and ``base_data_version_number``.
        :param data_version_number: The data version number to export.
        :param base_data_version_number: The data version number to compare against.
        """
        def call_impl(context: SessionContext) -> Response:
            url = context.mk_url(f"{BASE_PATH}/jobs")
            payload = {
                'dataVersionNumber': str(data_version_number),
                'baseDataVersionNumber': str(base_data_version_number)
            }
            headers = context.mk_headers()
            headers['Content-Type'] = "application/json"
            return context.session().post(url, headers=headers, data=json.dumps(payload))
        return self.run(call_impl)

    def get_data_version_export_job_status(self, job_id: str) -> Response:
        """
        Check the status of a data version export job. Retrieve ``job_id`` from the response returned by
        ``schedule_initial_data_version_export_job`` or  ``schedule_delta_data_version_export_job``.
        :param job_id: The job ID of a scheduled DV export job.
        """
        def call_impl(context: SessionContext) -> Response:
            url = context.mk_url(f"{BASE_PATH}/jobs/{job_id}")
            return context.session().get(url, headers=context.mk_headers())
        return self.run(call_impl)

    def get_data_version_export_metadata(self, export_id: str):
        """
        After the DV export job completes, get the DV export details. Retrieve ``export_id``
        from the response returned by ``get_data_version_export_job_status``.
        :param export_id: The export ID of the completed DV export job.
        """
        def call_impl(context: SessionContext) -> Response:
            url = context.mk_url(f"{BASE_PATH}/exports/{export_id}")
            return context.session().get(url, headers=context.mk_headers())
        return self.run(call_impl)

    def get_data_versions_available_for_export(self) -> Response:
        """
        Returns details for all data versions on which you can run a DV export job.
        """
        def call_impl(context: SessionContext) -> Response:
            url = context.mk_url(f"{BASE_PATH}/data-versions")
            return context.session().get(url, headers=context.mk_headers())
        return self.run(call_impl)

    def get_available_data_version_exports(self) -> Response:
        """
        Returns a list of all available data version exports. Data version exports are available for 14 days after export job completes.
        """
        def call_impl(context: SessionContext) -> Response:
            url = context.mk_url(f"{BASE_PATH}/exports")
            return context.session().get(url, headers=context.mk_headers())
        return self.run(call_impl)

    def get_export_file(self, export_id: str, file_id: str, stream=False) -> Response:
        """
        Download a file with ID ``file_id`` for specific data version export with ID ``export_id``. The file is
        gz compressed on the server. The default ``stream=False`` lets you automatically decode the file during
        download. Set ``stream=True`` to download the compressed file as raw bytes to decode later.
        :param export_id: The ID of the export job that contains the file.
        :param file_id: The ID of the file within the ``export_id`` to download.
        :param stream: Boolean to pass to underlying ``Requests`` call. If ``True``, gives access to raw bytes.
            The default is ``False``.
        """
        def call_impl(context: SessionContext) -> Response:
            url = context.mk_url(f"{BASE_PATH}/exports/{export_id}/files/{file_id}")
            return context.session().get(url, headers=context.mk_headers(), stream=stream)
        return self.run(call_impl)
