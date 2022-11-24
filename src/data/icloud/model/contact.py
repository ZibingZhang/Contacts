import dataclasses
import enum
import uuid

import model

import dataclasses_json

from common import dataclasses_utils

NO_YEAR = 1604


def date_field():
    return dataclasses.field(
        metadata=dataclasses_json.config(
            encoder=dataclasses_utils.date_encoder(NO_YEAR),
            decoder=dataclasses_utils.date_decoder(NO_YEAR),
        )
    )


@dataclasses_json.dataclass_json
@dataclasses.dataclass(frozen=True)
class Date:
    label: str
    field: model.Date = date_field()


@dataclasses_json.dataclass_json
@dataclasses.dataclass(frozen=True)
class EmailAddress:
    field: str
    label: str


@dataclasses_json.dataclass_json
@dataclasses.dataclass(frozen=True)
class IMField:
    IMService: str
    userName: str


class IMLabel(str, enum.Enum):
    CUSTOM = "custom"
    HOME = "HOME"
    OTHER = "OTHER"
    WORK = "WORK"


@dataclasses_json.dataclass_json
@dataclasses.dataclass(frozen=True)
class IM:
    field: IMField
    label: IMLabel


@dataclasses_json.dataclass_json
@dataclasses.dataclass(frozen=True)
class Phone:
    field: str
    label: str | None = None


@dataclasses_json.dataclass_json
@dataclasses.dataclass(frozen=True)
class Profile:
    field: str
    label: str | None = None
    displayName: str | None = None
    user: str | None = None
    userId: str | None = None


@dataclasses_json.dataclass_json
@dataclasses.dataclass(frozen=True)
class RelatedName:
    field: str
    label: str


@dataclasses_json.dataclass_json
@dataclasses.dataclass(frozen=True)
class StreetAddressField:
    country: str | None = None
    countryCode: str | None = None
    city: str | None = None
    postalCode: str | None = None
    state: str | None = None
    street: str | None = None
    subLocality: str | None = None


@dataclasses_json.dataclass_json
@dataclasses.dataclass(frozen=True)
class StreetAddress:
    field: StreetAddressField
    label: str


@dataclasses_json.dataclass_json
@dataclasses.dataclass(frozen=True)
class Url:
    field: str
    label: str


@dataclasses_json.dataclass_json
@dataclasses.dataclass(frozen=True)
class ICloudContact:
    contactId: uuid.UUID
    etag: str
    isCompany: bool
    isGuardianApproved: bool
    normalized: str
    whitelisted: bool
    birthday: model.Date | None = date_field()
    IMs: list[IM] | None = None
    companyName: str | None = None
    dates: list[Date] | None = None
    department: str | None = None
    emailAddresses: list[EmailAddress] | None = None
    firstName: str | None = None
    lastName: str | None = None
    middleName: str | None = None
    nickName: str | None = None
    notes: str | None = None
    phones: list[Phone] | None = None
    phoneticCompanyName: str | None = None
    phoneticFirstName: str | None = None
    phoneticLastName: str | None = None
    prefix: str | None = None
    profiles: list[Profile] | None = None
    relatedNames: list[RelatedName] | None = None
    streetAddresses: list[StreetAddress] | None = None
    suffix: str | None = None
    urls: list[Url] | None = None
