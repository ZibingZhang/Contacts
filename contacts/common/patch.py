"""Monkey patches."""
from __future__ import annotations

import json
import uuid


# https://github.com/jazzband/django-push-notifications/issues/586#issuecomment-963930371
def json_encode_uuid() -> None:
    old_default = json.JSONEncoder.default

    def new_default(self, obj):
        if isinstance(obj, uuid.UUID):
            return str(obj).upper()
        return old_default(self, obj)

    json.JSONEncoder.default = new_default
