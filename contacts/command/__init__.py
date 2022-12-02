import enum

from command import add, pull, push, tag, validate


class Command(str, enum.Enum):
    ADD = "add"
    PULL = "pull"
    PUSH = "push"
    TAG = "tag"
    VALIDATE = "validate"


add = add
pull = pull
push = push
tag = tag
validate = validate
