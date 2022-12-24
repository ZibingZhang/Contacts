"""Command line commands."""
import enum

from contacts.command import add, pull, push, sync_groups, tag, validate


class Command(enum.StrEnum):
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
