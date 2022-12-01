import enum

from command import add, pull, push, tag


class Command(str, enum.Enum):
    ADD = "add"
    PULL = "pull"
    PUSH = "push"
    TAG = "tag"


add = add.add
pull = pull.pull
push = push.push
tags = tag.tag
