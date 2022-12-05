from __future__ import annotations

import dataclasses
from typing import Any

from model import date, enumeration
from utils import dataclasses_utils


@dataclasses.dataclass
class HighSchool(dataclasses_utils.DataClassJsonMixin):
    name: enumeration.HighSchoolName
    graduation_year: int | None = None


@dataclasses.dataclass
class University(dataclasses_utils.DataClassJsonMixin):
    name: enumeration.UniversityName
    graduation_year: int | None = None
    majors: list[str] | None = None
    minors: list[str] | None = None


@dataclasses.dataclass
class Education(dataclasses_utils.DataClassJsonMixin):
    bachelor: University | None = None
    high_school: HighSchool | None = None
    master: University | None = None


@dataclasses.dataclass
class EmailAddress(dataclasses_utils.DataClassJsonMixin):
    label: str
    local_part: str
    domain: str


@dataclasses.dataclass
class ICloudPhotoCrop(dataclasses_utils.DataClassJsonMixin):
    height: int
    width: int
    x: int
    y: int


@dataclasses.dataclass
class ICloudPhoto(dataclasses_utils.DataClassJsonMixin):
    crop: ICloudPhotoCrop
    signature: str
    url: str
    whitelisted: bool | None = None


@dataclasses.dataclass
class ICloudMetadata(dataclasses_utils.DataClassJsonMixin):
    uuid: str
    etag: str | None = None
    photo: ICloudPhoto | None = None


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
    country_code: enumeration.CountryCode
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
class InstagramProfile(dataclasses_utils.DataClassJsonMixin):
    username: str


@dataclasses.dataclass
class SocialProfiles(dataclasses_utils.DataClassJsonMixin):
    facebook: FacebookProfile | None = None
    game_center: GameCenterProfile | None = None
    instagram: InstagramProfile | None = None


@dataclasses.dataclass
class StreetAddress(dataclasses_utils.DataClassJsonMixin):
    country: enumeration.Country | None = None
    city: str | None = None
    label: str | None = None
    postal_code: int | None = None
    state: str | None = None
    street: list[str] | None = None


@dataclasses.dataclass
class Contact(dataclasses_utils.DataClassJsonMixin):
    name: Name
    birthday: date.Date | None = date.new_field(required=False)
    dated: date.DateRange | None = None
    education: Education | None = None
    email_addresses: list[EmailAddress] | None = None
    favorite: dict | None = None
    friends_friend: str | None = None
    icloud: ICloudMetadata | None = None
    notes: str | None = None
    phone_numbers: list[PhoneNumber] | None = None
    social_profiles: SocialProfiles | None = None
    street_addresses: list[StreetAddress] | None = None
    tags: list[str] | None = None

    def __setattr__(self, key: str, value: Any) -> None:
        if key == "email_addresses" and value is not None:
            super().__setattr__(
                key,
                sorted(
                    value,
                    key=lambda email_address: email_address.domain
                    + email_address.local_part,
                ),
            )
        elif key == "tags" and value is not None:
            super().__setattr__(key, list(sorted(set(value))))
        else:
            super().__setattr__(key, value)
