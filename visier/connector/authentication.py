
class Authentication(object):
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
        # TODO check for None and throw as necessary
        self.vanity = vanity
        self.host = host
        self.api_key = api_key
        self.username = username
        self.password = password
