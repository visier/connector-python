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
Utility functions for loading JSON and text files from the examples directory.
"""

import json
import os


def load_json(path: str) -> dict:
    """Load a JSON file and return the contents as a dictionary."""
    return _load_from_path(path, json.load)


def load_str(path: str) -> str:
    """Load a text file and return the contents as a string."""
    return _load_from_path(path, lambda f: f.read())


def _load_from_path(path: str, func: callable) -> object:
    """Load a file and return the contents as an object."""
    if not path.startswith("examples/"):
        path = os.path.join("examples", path)
    with open(path, encoding="UTF-8") as spec_file:
        return func(spec_file)
