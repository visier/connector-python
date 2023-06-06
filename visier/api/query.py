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
