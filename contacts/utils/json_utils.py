"""Utilities for JSON."""
import functools
import json

dumps = functools.partial(json.dumps, ensure_ascii=False, indent=2)
