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
Basic Authentication class for Visier Connector
"""

import os
from argparse import ArgumentParser, Namespace
import dataclasses
from abc import ABC
from typing import Any, OrderedDict
from .constants import (ENV_VISIER_USERNAME, ENV_VISIER_PASSWORD, ENV_VISIER_HOST,
                        ENV_VISIER_APIKEY, ENV_VISIER_VANITY, ENV_VISIER_CLIENT_ID,
                        ENV_VISIER_REDIRECT_URI, ENV_VISIER_TARGET_TENANT_ID,
                        ENV_VISIER_CLIENT_SECRET)


@dataclasses.dataclass
class Authentication(ABC):
    """Abstract base class for authentication configuration definition"""
    def __init__(self,
                 host: str,
                 api_key: str,
                 target_tenant_id: str = None) -> None:
        super().__init__()
        if not api_key or not host:
            raise ValueError("""ERROR: Missing required credentials.
            Please provide host and api_key. target_tenant_id is optional.""")
        self.host = host
        self.api_key = api_key
        self.target_tenant_id = target_tenant_id


@dataclasses.dataclass
class Basic(Authentication):
    """
    Basic Authentication configuration definition
    
    Keyword arguments:
    username -- The name of the user to authenticate as
    password -- The password of the user
    api_key -- The tenant's API Key
    host -- The host and protocol portion of the url. E.g. https://customer-name.visierinc.io
    vanity -- Optional vanity name for the customer
    target_tenant_id -- Optional tenant id to target in a partner authentication setting
    """

    def __init__(
            self,
            username: str,
            password: str,
            api_key: str,
            host: str,
            vanity: str = None,
            target_tenant_id: str = None) -> None:
        super().__init__(host, api_key, target_tenant_id)
        if not username or not password:
            raise ValueError("""ERROR: Missing required credentials.
            Please provide username, password, api_key, and host.""")
        self.vanity = vanity
        self.username = username
        self.password = password


@dataclasses.dataclass
class OAuth2(Authentication):
    """Authentication configuration definition for OAuth2.
    This refers to the OAuth2 Client Credentials Grant Flow, which
    will attempt to open a browser window for the consent page.

    Keyword arguments:
    host -- The host and protocol portion of the url. E.g. https://customer-name.visierinc.io
    api_key -- The tenant's API Key
    client_id -- The OAuth2 client id
    client_secret -- The OAuth2 client secret
    username -- Optional username for password grant OAuth2 flow
    password -- Optional password for password grant OAuth2 flow
    redirect_uri -- Optional redirect uri for the OAuth2 callback
    target_tenant_id -- Optional tenant id to target in a partner authentication setting
    """

    def __init__(self,
                 host: str,
                 api_key: str,
                 client_id: str,
                 client_secret: str,
                 username: str,
                 password: str,
                 redirect_uri: str = None,
                 target_tenant_id: str = None) -> None:
        super().__init__(host, api_key, target_tenant_id)
        if not client_id:
            raise ValueError("""ERROR: Missing required OAuth2 credentials.
            Please provide host, api_key and client_id. redirect_uri is optional.""")
        self.client_secret = client_secret
        self.client_id = client_id
        self.username = username
        self.password = password
        self.redirect_uri = redirect_uri

def add_auth_arguments(parser: ArgumentParser) -> None:
    """Augments an ArgumentParser with arguments for authentication configuration."""
    parser.add_argument("-a", "--apikey", help="Visier API key", type=str)
    parser.add_argument("-c", "--client-id", help="Visier OAuth client ID", type=str)
    parser.add_argument("-S", "--client-secret", help="Visier OAuth client secret", type=str)
    parser.add_argument("-H", "--host", help="Visier host", type=str)
    parser.add_argument("-p", "--password", help="Visier password", type=str)
    parser.add_argument("-r", "--redirect-uri", help="Visier OAuth redirect URI", type=str)
    parser.add_argument("-t", "--target-tenant-id", help="Visier partner tenant name", type=str)
    parser.add_argument("-u", "--username", help="Visier username", type=str)
    parser.add_argument("-v", "--vanity", help="Visier vanity", type=str)

def make_auth(args: Namespace = None,
              env_values: OrderedDict = None) -> Authentication:
    """Returns an Authentication subclass object based on parsed arguments or environment variable values.
    Delegates more detailed credential completeness checks to the Authentication classes.
    
    Keyword arguments:
    args -- Parsed arguments from ArgumentParser
    env_values -- Ordered dictionary of variable values from dotenv_values"""
    args = args or NoArgs()
    env_values = env_values or OrderedDict()

    def dot_or_os(var_name: str) -> str:
        return env_values.get(var_name) or os.getenv(var_name)

    host = args.host or dot_or_os(ENV_VISIER_HOST)
    api_key = args.apikey or dot_or_os(ENV_VISIER_APIKEY)
    target_tenant_id = args.target_tenant_id or dot_or_os(ENV_VISIER_TARGET_TENANT_ID)

    username = args.username or dot_or_os(ENV_VISIER_USERNAME)
    password = args.password or dot_or_os(ENV_VISIER_PASSWORD)

    client_id = args.client_id or dot_or_os(ENV_VISIER_CLIENT_ID)
    if client_id:
        return OAuth2(
            host=host,
            api_key=api_key,
            client_id=client_id,
            client_secret=args.client_secret or dot_or_os(ENV_VISIER_CLIENT_SECRET),
            username=username,
            password=password,
            redirect_uri=args.redirect_uri or dot_or_os(ENV_VISIER_REDIRECT_URI),
            target_tenant_id=target_tenant_id)

    if (username and password):
        return Basic(
            username=username,
            password=password,
            host=host,
            api_key=api_key,
            vanity=args.vanity or dot_or_os(ENV_VISIER_VANITY),
            target_tenant_id=target_tenant_id)

    raise ValueError("""ERROR: Missing required credentials.
                     Please provide either Basic or OAuth2 credentials.
                     Both methods require host and api_key.
                     Basic also requires username and password.
                     OAuth2 also requires client_id.
                     Customer applications using OAuth also requires client_secret.""")

@dataclasses.dataclass
class NoArgs(Namespace):
    """Empty namespace object with all None values"""
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.host = None
        self.apikey = None
        self.client_id = None
        self.client_secret = None
        self.redirect_uri = None
        self.target_tenant_id = None
        self.username = None
        self.password = None
        self.vanity = None
