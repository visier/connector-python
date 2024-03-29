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
Visier Session object through which JSON as well as SQL-like queries are executed.
"""

from typing import Callable
import webbrowser
from queue import Empty
from urllib.parse import urlencode, quote
import secrets
import hashlib
import base64
import requests
from requests import Session, Response
from deprecated import deprecated
from .table import ResultTable
from .authentication import Authentication, OAuth2, Basic
from .constants import TARGET_TENANT_ID, USER_AGENT, USER_AGENT_VALUE
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
        # Set the User-Agent header for internal tracking purposes
        self._session.headers.update({USER_AGENT: USER_AGENT_VALUE})

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
        self._timeout = 30 # timeout in seconds for individual requests
        self._auth_code_flow_timeout = 120 # timeout in seconds for the OAuth2 authorization code flow

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
        self._close()

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
            self._connect_oauth(self._auth)
        else:
            self._connect_basic(self._auth)

    def _connect_oauth(self, auth: OAuth2):
        """Connect to Visier using OAuth2.
        Both password (two-legged) and authorization code (three-legged) flows are supported."""
        if auth.username and auth.password:
            self._connect_oauth_password(auth)
        else:
            self._connect_auth_code(auth)

    def _connect_basic(self, auth: Basic):
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
        if result.status_code == 500 and not auth.vanity:
            raise QueryExecutionError(result.status_code, "Vanity name is required for logging on to this tenant")
        result.raise_for_status()
        # Only create a requests.Session once we have a Visier ASID Token
        update_session(result.text)

    def _update_session(self, token: str, api_key: str) -> None:
        headers = {
            "Authorization": f"Bearer {token}",
            "apikey": api_key
        }
        self._session = Session()
        self._session.headers.update(headers)

    def _request_token(self, auth: OAuth2, body: dict) -> str:
        def get_client_auth():
            if auth.client_id and auth.client_secret:
                return (auth.client_id, quote(auth.client_secret, safe=''))
            return None

        url = auth.host + "/v1/auth/oauth2/token"
        # if we have a redirect_uri when getting the auth code, we also must include it in the token
        # request as part of the grant. https://datatracker.ietf.org/doc/html/rfc6749#section-4.1.3
        if auth.redirect_uri:
            body["redirect_uri"] = auth.redirect_uri
        response = requests.post(url=url,
                                 data=body,
                                 headers={"apikey": auth.api_key, USER_AGENT: USER_AGENT_VALUE},
                                 timeout=self._timeout,
                                 auth=get_client_auth())
        response.raise_for_status()
        response = response.json()
        return response['access_token']

    def _connect_auth_code(self, auth: OAuth2):
        """Connect to Visier using (three-legged) OAuth2.
        This method will attempt to open a browser for the authentication and consent screens.
        It will also spin up a local web server to receive the OAuth2 authorization code."""
        def mk_pkce_pair():
            """"Generate a PKCE code verifier and challenge pair"""
            code_verifier = secrets.token_urlsafe(64)
            code_challenge_digest = hashlib.sha256(code_verifier.encode()).digest()
            code_challenge = base64.urlsafe_b64encode(code_challenge_digest).decode().rstrip("=")
            return code_verifier, code_challenge

        def get_token(code: str, code_verifier: str) -> str:
            body = {
                "grant_type": "authorization_code",
                "client_id": auth.client_id,
                "scope": "read",
                "code": code,
                "code_verifier": code_verifier
            }
            return self._request_token(auth, body)

        code_verifier, code_challenge = mk_pkce_pair()
        url_prefix = auth.host + "/v1/auth/oauth2"
        binding = CallbackBinding(auth.redirect_uri)
        with CallbackServer(binding) as svr:
            query_args = {
                "apikey": auth.api_key,
                "response_type": "code",
                "client_id": auth.client_id,
                "code_challenge_method": "S256",
                "code_challenge": code_challenge
            }
            if auth.redirect_uri:
                query_args["redirect_uri"] = auth.redirect_uri

            browser_url = f'{url_prefix}/authorize?{urlencode(query_args)}'
            # Launch the browser for authentication and consent screens
            webbrowser.open(browser_url)
            try:
                # Wait up to 2 minutes for the user to complete the OAuth2 code flow
                code = svr.queue.get(block=True, timeout=self._auth_code_flow_timeout)
                self._update_session(get_token(code, code_verifier), auth.api_key)
            except Empty as empty:
                raise OAuthConnectError("Timed out waiting for OAuth2 auth code") from empty

    def _connect_oauth_password(self, auth: OAuth2):
        """Connect to Visier using (two-legged) OAuth2 password grant flow."""
        body = {
            "grant_type": "password",
            "client_id": auth.client_id,
            "scope": "read",
            "username": auth.username,
            "password": auth.password,
        }
        token = self._request_token(auth, body)
        self._update_session(token, auth.api_key)

    def _close(self):
        """Close the session."""
        if self._session:
            self._session.close()
            self._session = None
