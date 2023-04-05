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
Basic Authentication class for Visier Connector
"""

import dataclasses


@dataclasses.dataclass
class Authentication:
    """
    Authentication configuration definition
    
    Keyword arguments:
    username -- The name of the user to authenticate as
    password -- The password of the user
    api_key -- The tenant's API Key
    host -- The host and protocol portion of the url. E.g. https://customer-name.visierinc.io
    vanity -- Optional vanity name for the customer
    """

    def __init__(
            self,
            username: str,
            password: str,
            api_key: str,
            host: str,
            vanity: str = None) -> None:
        if not username or not password or not api_key or not host:
            raise ValueError("""ERROR: Missing required credentials.
            Please provide username, password, api_key, and host.""")

        self.vanity = vanity
        self.host = host
        self.api_key = api_key
        self.username = username
        self.password = password
