"""A dataclass representation of the json object response for an iCloud contact."""
from __future__ import annotations

import dataclasses

import model
from data.icloud.model import date_field
from utils import dataclasses_utils


@dataclasses.dataclass
class Date(dataclasses_utils.DataClassJsonMixin):
    label: str
    field: model.Date = date_field.new_field(required=True)


@dataclasses.dataclass
class EmailAddress(dataclasses_utils.DataClassJsonMixin):
    field: str
    label: str


@dataclasses.dataclass
class IMField(dataclasses_utils.DataClassJsonMixin):
    IMService: str
    userName: str


@dataclasses.dataclass
class IM(dataclasses_utils.DataClassJsonMixin):
    field: IMField
    label: str


@dataclasses.dataclass
class Phone(dataclasses_utils.DataClassJsonMixin):
    field: str
    label: str | None = None


@dataclasses.dataclass
class PhotoCrop(dataclasses_utils.DataClassJsonMixin):
    height: int
    width: int
    x: int
    y: int


@dataclasses.dataclass
class Photo(dataclasses_utils.DataClassJsonMixin):
    crop: PhotoCrop
    signature: str
    url: str
    whitelisted: bool | None = None


@dataclasses.dataclass
class Profile(dataclasses_utils.DataClassJsonMixin):
    field: str
    label: str | None = None
    displayname: str | None = None
    user: str | None = None
    userId: str | None = None


@dataclasses.dataclass
class RelatedName(dataclasses_utils.DataClassJsonMixin):
    field: str
    label: str


@dataclasses.dataclass
class StreetAddressField(dataclasses_utils.DataClassJsonMixin):
    country: str | None = None
    countryCode: str | None = None
    city: str | None = None
    postalCode: str | None = None
    state: str | None = None
    street: str | None = None
    subLocality: str | None = None


@dataclasses.dataclass
class StreetAddress(dataclasses_utils.DataClassJsonMixin):
    field: StreetAddressField
    label: str


@dataclasses.dataclass
class Url(dataclasses_utils.DataClassJsonMixin):
    field: str
    label: str


@dataclasses.dataclass
class ICloudContact(dataclasses_utils.DataClassJsonMixin):
    contactId: str
    isCompany: bool
    birthday: model.Date | None = date_field.new_field(required=False)
    companyName: str | None = None
    dates: list[Date] | None = None
    department: str | None = None
    emailAddresses: list[EmailAddress] | None = None
    etag: str | None = None
    firstName: str | None = None
    IMs: list[IM] | None = None
    isGuardianApproved: bool | None = None
    jobTitle: str | None = None
    lastName: str | None = None
    middleName: str | None = None
    nickName: str | None = None
    notes: str | None = None
    normalized: str | None = None
    phones: list[Phone] | None = None
    phoneticCompanyName: str | None = None
    phoneticFirstName: str | None = None
    phoneticLastName: str | None = None
    photo: Photo | None = None
    prefix: str | None = None
    profiles: list[Profile] | None = None
    relatedNames: list[RelatedName] | None = None
    streetAddresses: list[StreetAddress] | None = None
    suffix: str | None = None
    urls: list[Url] | None = None
    whitelisted: bool | None = None
