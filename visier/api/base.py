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
Abstract base class for Visier API clients that abstract the VisierSession.
"""

from abc import ABC
from typing import Callable
from requests import Response
from visier.connector import VisierSession, QueryExecutionError, SessionContext


class ApiClientBase(ABC):
    """Abstract base class for Visier API clients that abstract the VisierSession."""
    def __init__(self, visier_session: VisierSession, raise_on_error: bool = False) -> None:
        """Construct an API Client.
        
        Arguments:
        - visier_session: The VisierSession to use for API calls.
        - raise_on_error: If True, raise an exception on API call errors. If False, return None with last_error populated."""
        super().__init__()
        self._visier_session = visier_session
        self._raise_on_error = raise_on_error
        self._last_error = None

    def run(self, func: Callable[[SessionContext], Response]):
        """Runs the provided function with the internal VisierSession.
        
        Arguments:
        - func: The function to run. The function should take a SessionContext as an argument and return a Response."""
        if self._raise_on_error:
            return self._visier_session.execute(func)
        try:
            self._last_error = None
            response = self._visier_session.execute(func)
            return response
        except QueryExecutionError as ex:
            self._last_error = f"Error. Message: {ex.message}. Status Code: {ex.status_code}."
            return None

    def last_error(self) -> str:
        """Returns the error from the msot recent API call or None if the call was successful"""
        return self._last_error
