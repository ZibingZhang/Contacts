from __future__ import annotations

import dataclasses
import enum

from common.utils import dataclasses_utils
from model import date_field

from data import icloud

NO_YEAR = 0


@dataclasses.dataclass
class Date(dataclasses_utils.DataClassJsonMixin):
    day: int | None = None
    month: int | None = None
    year: int | None = None


@dataclasses.dataclass
class DateRange(dataclasses_utils.DataClassJsonMixin):
    start: Date | None = date_field.new_field(required=False)
    end: Date | None = date_field.new_field(required=False)


@dataclasses.dataclass
class EmailAddress(dataclasses_utils.DataClassJsonMixin):
    label: str
    local_part: str
    domain: str


@dataclasses.dataclass
class ICloud(dataclasses_utils.DataClassJsonMixin):
    etag: str
    uuid: str
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


class CountryCode(enum.IntEnum):
    NANP = 1
    IRELAND = 353
    UNITED_KINGDOM = 44
    BRAZIL = 55
    CHILE = 56
    HONG_KONG = 852
    CHINA = 86
    TAIWAN = 886


@dataclasses.dataclass
class PhoneNumber(dataclasses_utils.DataClassJsonMixin):
    countryCode: CountryCode
    number: int
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
class Contact(dataclasses_utils.DataClassJsonMixin):
    birthday: Date | None = date_field.new_field(required=False)
    dated: DateRange | None = None
    email_addresses: list[EmailAddress] | None = None
    family: dict | None = None
    icloud: ICloud | None = None
    name: Name | None = None
    notes: str | None = None
    phone_numbers: list[PhoneNumber] | None = None
    social_profiles: SocialProfiles | None = None
    tags: list[str] | None = None
