# https://github.com/jazzband/django-push-notifications/issues/586#issuecomment-963930371
from json import JSONEncoder
from uuid import UUID

old_default = JSONEncoder.default


def new_default(self, obj):
    if isinstance(obj, UUID):
        return str(obj)
    return old_default(self, obj)


JSONEncoder.default = new_default
