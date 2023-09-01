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
