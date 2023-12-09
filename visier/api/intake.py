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
API client for the Visier Data Intake API.
"""
from os.path import basename
from typing import List
from urllib.parse import urlencode
from mimetypes import guess_type
from requests import Response
from visier.connector import SessionContext
from .base import ApiClientBase

BASE_PATH = "/v1/op"

class DataIntakeApiClient(ApiClientBase):
    """API client for the Visier Data Intake API."""

    def get_data_sources(self) -> Response:
        """Get the data sources available for Data Intake"""
        def call_impl(context: SessionContext) -> Response:
            url = context.mk_url(f"{BASE_PATH}/data-sources")
            return context.session().get(url, headers=context.mk_headers())
        return self.run(call_impl)

    def start_transfer(self) -> Response:
        """Start an upload transfer session. This is the first step in uploading data to Visier."""
        def call_impl(context: SessionContext) -> Response:
            url = context.mk_url(f"{BASE_PATH}/data-transfer-sessions")
            return context.session().post(url, headers=context.mk_headers())
        return self.run(call_impl)

    def upload_records_batch(self, transfer_session_id: str, source_id: str, source_data: List,
                             tenant_code: str = None, sequence: int = 1) -> Response:
        """Transfer data to Visier in batches of records. Each request includes a 
        batch of records formatted as a comma separated array with the first row containing the column
        headers in the request body. Each subsequent request should also include the first row as a header.
        
        Arguments:
        - transfer_session_id: The id of the transfer session returned by start_transfer
        - source_id: The id of the source to upload data to, returned by get_data_sources
        - source_data: The data to upload, formatted as a list of strings where each string is a comma separated 
        list of values and the first row is the column headers
        - tenant_code: The tenant code to upload data to, if not specified the default tenant will be used
        - sequence: The sequence number of the batch, starting at 1"""
        def call_impl(context: SessionContext) -> Response:
            arguments = {
                "source_id": source_id,
                "sequence": sequence
            }
            if tenant_code:
                arguments["tenantCode"] = tenant_code
            url = context.mk_url(f"{BASE_PATH}/data-transfer-sessions/{transfer_session_id}/add?{urlencode(arguments)}")
            return context.session().put(url, json=source_data, headers=context.mk_headers())
        return self.run(call_impl)

    def upload_file(self, transfer_session_id: str, source_id: str, payload_file_path: str,
                    tenant_code: str = None, sequence: int = 1) -> Response:
        """Upload a data file to the given object. The file must be a CSV file with the first row containing the column or a ZIP file 
        containing CSV files with the first row containing the column headers.
        
        Arguments:
        - transfer_session_id: The id of the transfer session returned by start_transfer
        - source_id: The id of the source to upload data to, returned by get_data_sources
        - payload_file_path: The path to the file to upload
        - tenant_code: The tenant code to upload data to, if not specified the default tenant will be used
        - sequence: The sequence number of the batch, starting at 1"""
        def call_impl(context: SessionContext) -> Response:
            arguments = {
                "source_id": source_id,
                "sequence": sequence
            }
            if tenant_code:
                arguments["tenantCode"] = tenant_code
            url = context.mk_url(f"{BASE_PATH}/data-transfer-sessions/{transfer_session_id}/upload?{urlencode(arguments)}")
            with open(payload_file_path, "rb") as payload_file:
                filename = basename(payload_file.name)
                mimetype, _ = guess_type(filename)
                mimetype = mimetype or "application/octet-stream"
                files = {"file": (filename, payload_file, mimetype)}
                return context.session().put(url, files=files, headers=context.mk_headers())
        return self.run(call_impl)

    def complete_transfer(self, transfer_session_id: str, process_data: bool = False) -> Response:
        """Complete a transfer session by triggering a receiving job. A
        receiving job validates the transferred data and adds the transferred data to Visier's data store.
        You can set an optional parameter to generate a data version through a processing job immediately
        after the receiving job completes.
        
        Arguments:
        - transfer_session_id: The id of the transfer session returned by start_transfer
        - process_data: Whether to trigger a processing job after the receiving job completes. Default value is False"""
        def call_impl(context: SessionContext) -> Response:
            body = {
                "transferSessionId": transfer_session_id,
                "processingData": process_data
            }
            url = context.mk_url(f"{BASE_PATH}/jobs/receiving-jobs")
            return context.session().post(url, json=body, headers=context.mk_headers())
        return self.run(call_impl)

    def cancel_transfer(self, transfer_session_id: str) -> Response:
        """Roll-back a pending transfer session and discard all uploaded data in that session.
        
        Arguments:
        - transfer_session_id: The id of the transfer session returned by start_transfer"""
        def call_impl(context: SessionContext) -> Response:
            url = context.mk_url(f"{BASE_PATH}/data-transfer-sessions/{transfer_session_id}/cancel")
            return context.session().put(url, headers=context.mk_headers())
        return self.run(call_impl)

    def get_receiving_status(self, receiving_job_id: str, jobs: bool = False, tenant_code: str = None,
                             start: int = 0, limit: int = 1000) -> Response:
        """After completing a transfer session, you may want to know the status of the receiving job and
        the associated tenant receiving jobs. A receiving job validates the transferred data and adds the
        transferred data to Visier's data store.
        Use this API to retrieve the receiving job status and summary of analytic tenant receiving jobs.

        Arguments:
        - receiving_job_id: The id of the receiving job returned by complete_transfer
        - jobs: Whether to include the status of associated analytic tenant receiving jobs
        - tenant_code: The tenant code to get job status from, if not specified status will be returned from all tenants
        - start: The index to start retreiving status from. Default value is 0
        - limit: The number of job statuses to return. Default value is 1000"""
        def call_impl(context: SessionContext) -> Response:
            arguments = {
                "jobs": jobs,
                "start": start,
                "limit": limit
            }
            if tenant_code:
                arguments["tenantCode"] = tenant_code
            url = context.mk_url(f"{BASE_PATH}/jobs/receiving-jobs/{receiving_job_id}?{urlencode(arguments)}")
            return context.session().get(url, headers=context.mk_headers())
        return self.run(call_impl)

    def get_processing_status(self, receiving_job_id: str, tenant_code: str = None, start: int = 0, limit: int = 1000) -> Response:
        """Use this API to retrieve a list of statuses for all processing jobs associated with the given
        receiving job ID. Processing jobs deal with an individual analytic tenant's data load. A
        processing job is either triggered through the UI or is one of many processing jobs spawned
        from a receiving job. When a processing job is triggered as part of a set from an receiving job, it
        is associated to the receiving job through a Parent ID.

        Arguments:
        - receiving_job_id: The id of the receiving job returned by complete_transfer
        - tenant_code: The tenant code to get job status from, if not specified status will be returned from all tenants
        - start: The index to start retreiving status from. Default value is 0
        - limit: The number of job statuses to return. Default value is 1000"""
        def call_impl(context: SessionContext) -> Response:
            arguments = {
                "start": start,
                "limit": limit
            }
            if tenant_code:
                arguments["tenantCode"] = tenant_code
            url = context.mk_url(f"{BASE_PATH}/jobs/processing-jobs/{receiving_job_id}?{urlencode(arguments)}")
            return context.session().get(url, headers=context.mk_headers())
        return self.run(call_impl)
