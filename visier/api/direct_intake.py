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
API client for the Visier Direct Intake API.
"""

import dataclasses
from typing import List
from requests import Response
from visier.connector import SessionContext
from .base import ApiClientBase

DRAFT_ID = "prod"
BASE_PATH = f"/v1/data/directloads/{DRAFT_ID}"

@dataclasses.dataclass
class Configuration:
    """Configuration for a Direct Intake environment."""
    config = {}
    def __init__(self, is_supplemental: bool = None,
                 extend_objects: List[str] = None) -> None:
        self.config = {
            "job": {
                "supplementalMode": self._to_supplemental(is_supplemental),
                "extendObjects": self._to_list(extend_objects)
            }
        }

    def _to_supplemental(self, is_supplemental: bool) -> str:
        if is_supplemental is None:
            return "UNCHANGED"
        if is_supplemental:
            return "IS_SUPPLEMENTAL"
        return "IS_PRIMARY"

    def _to_list(self, extend_objects: List[str]) -> List[str]:
        if extend_objects is None:
            return []
        return extend_objects


class DirectIntakeApiClient(ApiClientBase):
    """API client for the Visier Direct Intake API."""

    def get_configuration(self) -> Response:
        """Get the configuration for the the direct intake environment."""
        def call_impl(context: SessionContext) -> Response:
            url = context.mk_url(f"{BASE_PATH}/configs")
            return context.session().get(url, headers=context.mk_headers())
        return self.run(call_impl)

    def set_configuration(self, configuration: Configuration) -> Response:
        """Set the configuration for the the direct intake environment.
        
        Arguments:
        - configuration: The direct intake environment configuration."""
        def call_impl(context: SessionContext) -> Response:
            url = context.mk_url(f"{BASE_PATH}/configs")
            return context.session().put(url, json=configuration.config, headers=context.mk_headers())
        return self.run(call_impl)

    def get_object_schema(self, object_id: str) -> Response:
        """Get the staging schema for the given object. This is the schema that the data file must conform to.
        
        Arguments:
        - object_id: The id of the object to get the schema for"""
        def call_impl(context: SessionContext) -> Response:
            url = context.mk_url(f"{BASE_PATH}/schemas/{object_id}")
            return context.session().get(url, headers=context.mk_headers())
        return self.run(call_impl)

    def start_transaction(self) -> Response:
        """Start an upload transaction"""
        def call_impl(context: SessionContext) -> Response:
            url = context.mk_url(f"{BASE_PATH}/transactions")
            return context.session().post(url, headers=context.mk_headers())
        return self.run(call_impl)

    def upload_file(self, transaction_id: str, object_name: str, payload_file_path: str) -> Response:
        """Upload a data file to the given object.
        
        Arguments:
        - transaction_id: The transaction id returned by start_transaction
        - obejct_name: The name of the object to upload to
        - payload_file: The path to the file to upload"""
        def call_impl(context: SessionContext) -> Response:
            url = context.mk_url(f"{BASE_PATH}/transactions/{transaction_id}/{object_name}")
            with open(payload_file_path, "rb") as payload_file:
                files = {"file": payload_file}
                return context.session().put(url, files=files, headers=context.mk_headers())
        return self.run(call_impl)

    def rollback_transaction(self, transaction_id: str) -> Response:
        """Roll-back a pending transaction and discard all uploaded data.
        
        Arguments:
        - transaction_id: The transaction id returned by start_transaction"""
        def call_impl(context: SessionContext) -> Response:
            url = context.mk_url(f"{BASE_PATH}/transactions/{transaction_id}")
            return context.session().delete(url, headers=context.mk_headers())
        return self.run(call_impl)

    def commit_transaction(self, transaction_id: str) -> Response:
        """Commit the transaction and make the uploaded data available for use.
        
        Arguments:
        - transaction_id: The transaction id returned by start_transaction"""
        def call_impl(context: SessionContext) -> Response:
            url = context.mk_url(f"{BASE_PATH}/transactions/{transaction_id}")
            return context.session().post(url, headers=context.mk_headers())
        return self.run(call_impl)

    def get_transaction_status(self, transaction_id: str) -> Response:
        """Get the status of the committed transaction.

        Arguments:
        - transaction_id: The transaction id returned by start_transaction"""
        def call_impl(context: SessionContext) -> Response:
            url = context.mk_url(f"{BASE_PATH}/transactions/{transaction_id}")
            return context.session().get(url, headers=context.mk_headers())
        return self.run(call_impl)
