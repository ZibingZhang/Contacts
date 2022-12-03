"""Utilities for JSON."""
import json


def dumps(dct: dict) -> str:
    """Convert a dictionary into JSON formatted data.

    Args:
        dct: A dictionary.

    Returns:
        JSON formatted representation of the data.
    """
    return json.dumps(dct, ensure_ascii=False, indent=2)
