from __future__ import annotations

import dataclasses

import model
from common.utils import dataclasses_utils, yaml_utils


def from_string(notes: str) -> Notes:
    return Notes.from_dict(yaml_utils.load(notes))


def to_string(notes: Notes) -> str:
    return yaml_utils.dump(notes)


@dataclasses.dataclass
class School(dataclasses_utils.DataClassJsonMixin):
    name: str
    grad_year: int | None = None
    majors: str | None = None
    minors: str | None = None


@dataclasses.dataclass
class Education(dataclasses_utils.DataClassJsonMixin):
    bachelor: School | None = None
    high_school: School | None = None
    master: School | None = None


@dataclasses.dataclass
class Favorites(dataclasses_utils.DataClassJsonMixin):
    candy: str | None = None
    color: str | None = None


@dataclasses.dataclass
class FriendsFriend(dataclasses_utils.DataClassJsonMixin):
    name: str
    uuid: str


@dataclasses.dataclass
class Notes(dataclasses_utils.DataClassJsonMixin):
    chinese_name: str | None = None
    comment: str | None = None
    education: Education | None = None
    favorite: Favorites | None = None
    family: dict | None = None
    friends_friend: FriendsFriend | None = None
    partner: model.DateRange | None = None
