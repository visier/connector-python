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
