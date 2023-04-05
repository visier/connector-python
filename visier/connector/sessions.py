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
Visier Session object through which JSON as well as SQL-like queries are executed.
"""

import json
import dataclasses
import requests
from requests import Session
from visier.connector.authentication import Authentication


@dataclasses.dataclass
class QueryExecutionError(Exception):
    """Description of error from executing a query"""
    def __init__(self, status_code, message) -> None:
        self.args = (f"""The query execution failed with the following
        HTTP status code: {status_code}
        The server returned the following description of the error:
        {message}""", )


@dataclasses.dataclass
class ResultTable:
    """Tabular result set

    Keyword args:
    jsonlines -- JSON Lines representation of the entire result set.
                 This is an array of strings, where each line will be
                 parsed independently.

    Class members:
    header -- Array of column header strings.
    rows() -- Row tuple generator
    """
    header = []

    def __init__(self, gen_f) -> None:
        self.header = json.loads(next(gen_f))
        self._generator = gen_f


    def rows(self):
        """Returns a row tuple generator"""
        for line in self._generator:
            yield json.loads(line)


class VisierSession:
    """Visier Session object through which SQL-like queries are executed.
    
    Keyword arguments:
    auth -- Authentication configuration
    """
    HEADER = {"Accept": "application/jsonlines, application/json"}

    def __init__(self, auth: Authentication) -> None:
        self._auth = auth
        self._session = None


    def execute_aggregate(self, query_def: object):
        """Execute a Visier aggregate query and return a tabular result."""
        url = self._auth.host + "/v1/data/query/aggregate"
        return self._execute_with_retry(url, query_def)


    def execute_list(self, query_def: object):
        """Execute a Visier list query and return a tabular result."""
        url = self._auth.host + "/v1/data/query/list"
        return self._execute_with_retry(url, query_def)


    def execute_sqllike(self, sql_query: str, options = None):
        """Execute a Visier SQL-like query statement and return a tabular result."""
        url = self._auth.host + "/v1/data/query/sql"
        body = {"query" : sql_query}
        if options:
            body["options"] = options
        return self._execute_with_retry(url, body)


    def __enter__(self):
        self._connect()
        return self


    def __exit__(self, ex_type, ex_value, trace_back):
        self._close()


    def _execute_with_retry(self, url: str, body: object):
        """Generic method for executing a query and retrying if necessary."""
        num_attempts_left = 2
        is_ok = False
        while not is_ok and num_attempts_left > 0:
            result = self._session.post(url=url, json=body, headers=self.HEADER)
            num_attempts_left -= 1
            is_ok = result.ok
            if not is_ok:
                if result.status_code == 401 and num_attempts_left > 0:
                    self._connect()
                else:
                    raise QueryExecutionError(result.status_code, result.text)
        return ResultTable(result.iter_lines())


    def _connect(self):
        url = self._auth.host + "/v1/admin/visierSecureToken"
        body = {'username': self._auth.username, 'password': self._auth.password}
        if self._auth.vanity:
            body["vanityName"] = self._auth.vanity
        result = requests.post(url=url, data=body, timeout=30)
        result.raise_for_status()

        # Only create a requests.Session once we have a Visier ASID Token
        asid_token = result.text
        self._session = Session()
        self._session.cookies["VisierASIDToken"] = asid_token
        self._session.headers.update({"apikey": self._auth.api_key})


    def _close(self):
        self._session.close()
