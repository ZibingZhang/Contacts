import enum

from command import add, pull, push, tag, validate, sync_groups


class Command(str, enum.Enum):
    ADD = "add"
    PULL = "pull"
    PUSH = "push"
    SYNC_GROUPS = "sync-groups"
    TAG = "tag"
    VALIDATE = "validate"


add = add
pull = pull
push = push
sync_groups = sync_groups
tag = tag
validate = validate
