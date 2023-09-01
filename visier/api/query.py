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
API client for the Visier Query API.
"""

from visier.connector import ResultTable
from .base import ApiClientBase


class QueryApiClient(ApiClientBase):
    """API client for the Visier Query API."""
    HEADER = {"Accept": "application/jsonlines, application/json"}

    def aggregate(self, query_def: object):
        """Execute a Visier aggregate query and return a tabular result."""
        return self._execute_query_api("/v1/data/query/aggregate", query_def)

    def list(self, query_def: object):
        """Execute a Visier list query and return a tabular result."""
        return self._execute_query_api("/v1/data/query/list", query_def)

    def sqllike(self, sql_query: str, options = None):
        """Execute a Visier SQL-like query statement and return a tabular result."""
        body = {"query" : sql_query}
        if options:
            body["options"] = options
        return self._execute_query_api("/v1/data/query/sql", body)

    def _execute_query_api(self, path: str, body: object):
        """Helper method for executing a query API with flattened result."""
        result = self.run(lambda s: s.session().post(url=s.mk_url(path),
                                                         json=body,
                                                         headers=s.mk_headers(self.HEADER)))
        if result is not None:
            return ResultTable(result.iter_lines())
        return None
