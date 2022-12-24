"""Utilities for generating random uuids."""
from __future__ import annotations

import uuid


def generate() -> str:
    """Generate a random uuid.

    Returns:
        A random uuid.
    """
    return str(uuid.uuid4()).upper()
