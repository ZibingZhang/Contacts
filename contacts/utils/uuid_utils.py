"""Utilities for generating random uuids."""
from __future__ import annotations

import uuid


def generate() -> str:
    return str(uuid.uuid4()).upper()
