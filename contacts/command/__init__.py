"""Command line commands."""
import enum

from contacts.command import (
    add,
    dump,
    load,
    pull,
    push,
    sync_groups,
    tag_ls,
    tag_mv,
    tag_repl,
    validate,
)


class Command(enum.StrEnum):
    ADD = "add"
    DUMP = "dump"
    LOAD = "load"
    PULL = "pull"
    PUSH = "push"
    SYNC_GROUPS = "sync-groups"
    TAG = "tag"
    VALIDATE = "validate"


class TagSubcommand(enum.StrEnum):
    LS = "ls"
    MV = "mv"
    REPL = "repl"


add = add
dump = dump
load = load
pull = pull
push = push
sync_groups = sync_groups
tag_ls = tag_ls
tag_mv = tag_mv
tag_repl = tag_repl
validate = validate
