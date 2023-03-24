import requests
import json
from requests import Session
from visier.connector.authentication import Authentication


class QueryExecutionError(Exception):
    """Description of error from executing a query"""
    def __init__(self, status_code, message) -> None:
        self.args = ("""The query execution failed with the following HTTP status code: {}
        The server returned the following description of the error:
        {}""".format(status_code, message), )


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


class VisierSession(object):
    """Visier Session object through which SQL-like queries are executed.
    
    Keyword arguments:
    auth -- Authentication configuration
    """
    def __init__(self, auth: Authentication) -> None:
        self._auth = auth
        self._session = None


    def executeAggregate(self, query_def: object):
        """Execute a Visier aggregate query and return a tabular result."""
        url = self._auth.host + "/v1/data/query/aggregate"
        return self._executeWithRetry(url, query_def)


    def executeList(self, query_def: object):
        """Execute a Visier list query and return a tabular result."""
        url = self._auth.host + "/v1/data/query/list"
        return self._executeWithRetry(url, query_def)


    def executeSqlLike(self, sql_query: str, options = None):
        """Execute a Visier SQL-like query statement and return a tabular result."""
        url = self._auth.host + "/v1/data/query/sql"
        body = {"query" : sql_query}
        if options:
            body["options"] = options
        return self._executeWithRetry(url, body)


    def __enter__(self):
        self._connect()
        return self


    def __exit__(self, ex_type, ex_value, trace_back):
        self._close()


    def _executeWithRetry(self, url: str, body: object):
        """Generic method for executing a query and retrying if necessary."""
        num_attempts_left = 2
        is_ok = False
        while not is_ok and num_attempts_left > 0:
            r = self._session.post(url=url, json=body, headers={"Accept": "application/jsonlines, application/json"})
            num_attempts_left -= 1
            is_ok = r.ok
            if not is_ok:
                if r.status_code == 401 and num_attempts_left > 0:
                    self._connect()
                else:
                    raise QueryExecutionError(r.status_code, r.text)
        return ResultTable(r.iter_lines())


    def _connect(self):
        url = self._auth.host + "/v1/admin/visierSecureToken"
        body = {'username': self._auth.username, 'password': self._auth.password}
        if self._auth.vanity:
            body["vanityName"] = self._auth.vanity
        r = requests.post(url=url, data=body)
        r.raise_for_status()

        # Only create a requests.Session once we have a Visier ASID Token
        asid_token = r.text
        self._session = Session()
        self._session.cookies["VisierASIDToken"] = asid_token
        self._session.headers.update({"apikey": self._auth.api_key})


    def _close(self):
        self._session.close()