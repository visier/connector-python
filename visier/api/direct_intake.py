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
API client for the Visier Direct Intake API.
"""

import dataclasses
from requests import Response
from visier.connector import SessionContext
from .base import ApiClientBase

DRAFT_ID = "prod"
BASE_PATH = f"/v1/data/directloads/{DRAFT_ID}"

@dataclasses.dataclass
class Configuration:
    """Configuration for a Direct Intake environment."""
    config = {}
    def __init__(self, is_supplemental: bool = None) -> None:
        self.config = {"job":{"supplementalMode": _to_supplemental(is_supplemental)}}

def _to_supplemental(is_supplemental: bool) -> str:
    if is_supplemental is None:
        return "UNCHANGED"
    if is_supplemental:
        return "IS_SUPPLEMENTAL"
    return "IS_PRIMARY"


class DirectIntakeApiClient(ApiClientBase):
    """API client for the Visier Direct Intake API."""

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
