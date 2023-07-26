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

import os
from typing import Callable
import webbrowser
from queue import Empty
import urllib.parse
import requests
from requests import Session, Response
from deprecated import deprecated
from .table import ResultTable
from .authentication import Authentication, OAuth2, Basic
from .constants import TARGET_TENANT_ID, ENV_VISIER_OAUTH_CALLBACK_URL
from .callback import CallbackServer, CallbackBinding


class QueryExecutionError(Exception):
    """Description of error from executing a query"""
    def __init__(self, status_code, message) -> None:
        self.args = (f"""The query execution failed with the following
        HTTP status code: {status_code}
        The server returned the following description of the error:
        {message}""", )
        self._status_code = status_code
        self._message = message

    def status_code(self) -> int:
        """Returns the HTTP status code"""
        return self._status_code

    def message(self) -> str:
        """Returns the error message"""
        return self._message


class OAuthConnectError(Exception):
    """Raised when there is an error connecting to Visier using OAuth2"""
    def __init__(self, message) -> None:
        self.args = (f"""The OAuth2 connection failed with the following error:
        {message}""", )
        self._message = message

    def message(self) -> str:
        """Returns the error message"""
        return self._message


class SessionContext:
    """
    Context object passed to the user-defined function in the execute() method.
    """
    def __init__(self, session: Session, host: str, target_tenant_id: str = None) -> None:
        self._session = session
        self._host = host
        self._target_tenant_id = target_tenant_id

    def session(self) -> Session:
        """Returns the current session object"""
        return self._session

    def mk_url(self, path: str) -> str:
        """Returns a URL for the given path"""
        return self._host + path

    def mk_headers(self, headers: dict = None) -> dict:
        """Returns the headers for the current request"""
        if headers is None:
            headers = {}
        if self._target_tenant_id is not None:
            headers[TARGET_TENANT_ID] = self._target_tenant_id
        return headers


class VisierSession:
    """Visier Session object through which SQL-like queries are executed.
    
    Keyword arguments:
    auth -- Authentication configuration
    """
    HEADER = {"Accept": "application/jsonlines, application/json"}

    def __init__(self, auth: Authentication) -> None:
        self._auth = auth
        self._session = None
        self._timeout = 30

    @deprecated(version="0.9.5", reason="Use visier.api.QueryApiClient instead")
    def execute_aggregate(self, query_def: object):
        """Execute a Visier aggregate query and return a tabular result."""
        return self._execute_query_api("/v1/data/query/aggregate", query_def)

    @deprecated(version="0.9.5", reason="Use visier.api.QueryApiClient instead")
    def execute_list(self, query_def: object):
        """Execute a Visier list query and return a tabular result."""
        return self._execute_query_api("/v1/data/query/list", query_def)

    @deprecated(version="0.9.5", reason="Use visier.api.QueryApiClient instead")
    def execute_sqllike(self, sql_query: str, options = None):
        """Execute a Visier SQL-like query statement and return a tabular result."""
        body = {"query" : sql_query}
        if options:
            body["options"] = options
        return self._execute_query_api("/v1/data/query/sql", body)

    def execute(self, call_function: Callable[[SessionContext], Response]) -> Response:
        """Execute a custom function with the current session.

        Keyword arguments:
        call_function -- Function that takes a SessionContext object as input and
                         returns a Response object.
        """
        num_attempts_left = 2
        is_ok = False
        while not is_ok and num_attempts_left > 0:
            context = SessionContext(self._session, self._auth.host, self._auth.target_tenant_id)
            result = call_function(context)
            num_attempts_left -= 1
            is_ok = result.ok
            if not is_ok:
                if result.status_code == 401 and num_attempts_left > 0:
                    self._connect()
                else:
                    raise QueryExecutionError(result.status_code, result.text)
        return result

    def __enter__(self):
        self._connect()
        return self

    def __exit__(self, ex_type, ex_value, trace_back):
        self.close()

    def _execute_query_api(self, path: str, body: object):
        """Helper method for executing a query API with flattened result.
        This is a legacy and deprecated method that doesn't support partner administrative
        principals to execute queries in the customer tenants."""
        result = self.execute(lambda s: s.session().post(url=s.mk_url(path),
                                                         json=body,
                                                         headers=self.HEADER))
        return ResultTable(result.iter_lines())

    def _connect(self):
        """Connect to Visier using either OAuth or basic authentication."""
        if isinstance(self._auth, OAuth2):
            self.connect_oauth(self._auth)
        else:
            self.connect_basic(self._auth)

    def connect_oauth(self, auth: OAuth2):
        """Connect to Visier using (three-legged) OAuth2.
        This method will attempt to open a browser for the authentication and consent screens.
        It will also spin up a local web server to receive the OAuth2 authorization code."""
        url_prefix = auth.host + "/v1/auth/oauth2"

        def get_token(code: str) -> str:
            url = url_prefix + "/token"
            body = {
                "grant_type": "authorization_code",
                "client_id": auth.client_id,
                "scope": "read",
                "code": code
            }
            # if we have a redirect_uri when getting the auth code, we also must include it in the token
            # request as part of the grant. https://datatracker.ietf.org/doc/html/rfc6749#section-4.1.3
            if auth.redirect_uri:
                body["redirect_uri"] = auth.redirect_uri
            response = requests.post(url=url, data=body, headers={"apikey": auth.api_key}, timeout=self._timeout)
            response.raise_for_status()
            response = response.json()
            # Currently not using refresh_token and id_token
            # refresh_token = response['refresh_token']
            # id_token = response['id_token']
            return response['access_token']

        def update_session(token: str) -> None:
            headers = {
                "Authorization": f"Bearer {token}",
                "apikey": auth.api_key
            }
            self._session = Session()
            self._session.headers.update(headers)

        callback_url = os.getenv(ENV_VISIER_OAUTH_CALLBACK_URL)
        binding = CallbackBinding(callback_url)
        with CallbackServer(binding) as svr:
            if auth.redirect_uri:
                redirect_uri_arg = f"&redirect_uri={urllib.parse.quote(auth.redirect_uri, safe='')}"
            else:
                redirect_uri_arg = "" # Empty means use the redirect_uri registered with Visier
            browser_url = f'{url_prefix}/authorize?apikey={auth.api_key}&response_type=code&client_id={auth.client_id}{redirect_uri_arg}'
            # Launch the browser for authentication and consent screens
            webbrowser.open(browser_url)
            try:
                # Wait up to 5 minutes for the user to complete the OAuth2 code flow
                code = svr.queue.get(block=True, timeout=300)
                update_session(get_token(code))
            except Empty as empty:
                raise OAuthConnectError("Timed out waiting for OAuth2 auth code") from empty

    def connect_basic(self, auth: Basic):
        """Connect to Visier using Basic Authentication."""
        def update_session(asid_token: str):
            self._session = Session()
            self._session.cookies["VisierASIDToken"] = asid_token
            self._session.headers.update({"apikey": auth.api_key})

        url = auth.host + "/v1/admin/visierSecureToken"
        body = {'username': auth.username, 'password': auth.password}
        if auth.vanity:
            body["vanityName"] = auth.vanity
        result = requests.post(url=url, data=body, timeout=self._timeout)
        result.raise_for_status()

        # Only create a requests.Session once we have a Visier ASID Token
        update_session(result.text)

    def close(self):
        """Close the session."""
        self._session.close()
        self._session = None
