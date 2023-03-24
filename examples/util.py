import json
import os


def load_json(path: str) -> dict:
    """Load a JSON file and return the contents as a dictionary."""
    return _load_from_path(path, lambda f: json.load(f))


def load_str(path: str) -> str:
    """Load a text file and return the contents as a string."""
    return _load_from_path(path, lambda f: f.read())


def _load_from_path(path: str, func: callable) -> object:
    """Load a file and return the contents as an object."""
    if not path.startswith("examples/"):
        path = os.path.join("examples", path)
    with open(path) as f:
        return func(f)