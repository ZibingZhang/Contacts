from __future__ import annotations

import dataclasses

from common.utils import dataclasses_utils
from model import common, date_field

from data import icloud


@dataclasses.dataclass
class School(dataclasses_utils.DataClassJsonMixin):
    name: str
    graduation_year: int | None = None
    majors: list[str] | None = None
    minors: list[str] | None = None


@dataclasses.dataclass
class Education(dataclasses_utils.DataClassJsonMixin):
    bachelor: School | None = None
    high_school: School | None = None
    master: School | None = None


@dataclasses.dataclass
class EmailAddress(dataclasses_utils.DataClassJsonMixin):
    label: str
    local_part: str
    domain: str


@dataclasses.dataclass
class ICloud(dataclasses_utils.DataClassJsonMixin):
    etag: str
    uuid: str
    meta: dict | None = None
    photo: icloud.model.Photo | None = None


@dataclasses.dataclass
class Name(dataclasses_utils.DataClassJsonMixin):
    prefix: str | None = None
    first_name: str | None = None
    nickname: str | None = None
    middle_name: str | None = None
    last_name: str | None = None
    suffix: str | None = None
    chinese_name: str | None = None


@dataclasses.dataclass
class PhoneNumber(dataclasses_utils.DataClassJsonMixin):
    country_code: common.CountryCode
    number: str
    label: str | None = None


# https://www.facebook.com/help/211813265517027
@dataclasses.dataclass
class FacebookProfile(dataclasses_utils.DataClassJsonMixin):
    user_id: int | None = None
    username: str | None = None


@dataclasses.dataclass
class GameCenterProfile(dataclasses_utils.DataClassJsonMixin):
    link: str
    username: str


@dataclasses.dataclass
class SocialProfiles(dataclasses_utils.DataClassJsonMixin):
    facebook: FacebookProfile | None = None
    game_center: GameCenterProfile | None = None


@dataclasses.dataclass
class StreetAddress(dataclasses_utils.DataClassJsonMixin):
    country: common.Country | None = None
    city: str | None = None
    label: str | None = None
    postal_code: int | None = None
    state: str | None = None
    street: list[str] | None = None


@dataclasses.dataclass
class Contact(dataclasses_utils.DataClassJsonMixin):
    birthday: common.Date | None = date_field.new_field(required=False)
    dated: common.DateRange | None = None
    education: Education | None = None
    email_addresses: list[EmailAddress] | None = None
    family: dict | None = None
    favorite: dict | None = None
    friends_friend: dict | None = None
    icloud: ICloud | None = None
    name: Name | None = None
    notes: str | None = None
    phone_numbers: list[PhoneNumber] | None = None
    social_profiles: SocialProfiles | None = None
    street_addresses: list[StreetAddress] | None = None
    tags: list[str] | None = None
