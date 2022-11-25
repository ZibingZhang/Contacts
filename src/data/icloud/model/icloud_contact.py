import dataclasses
import enum
import uuid

import dataclasses_json

import model
from common.utils import dataclasses_utils

NO_YEAR = 1604


def date_field(required: bool = False) -> dataclasses.Field:
    kwargs = {
        "metadata": dataclasses_json.config(
            encoder=dataclasses_utils.date_encoder(NO_YEAR),
            decoder=dataclasses_utils.date_decoder(NO_YEAR),
        )
    }

    if not required:
        kwargs["default"] = None

    return dataclasses.field(**kwargs)


@dataclasses.dataclass
class Date(dataclasses_utils.DataClassJsonMixin):
    label: str
    field: model.Date = date_field(required=True)


@dataclasses.dataclass
class EmailAddress(dataclasses_utils.DataClassJsonMixin):
    field: str
    label: str


@dataclasses.dataclass
class IMField(dataclasses_utils.DataClassJsonMixin):
    IMService: str
    userName: str


class IMLabel(str, enum.Enum):
    CUSTOM = "custom"
    HOME = "HOME"
    OTHER = "OTHER"
    WORK = "WORK"


@dataclasses.dataclass
class IM(dataclasses_utils.DataClassJsonMixin):
    field: IMField
    label: IMLabel


@dataclasses.dataclass
class Phone(dataclasses_utils.DataClassJsonMixin):
    field: str
    label: str | None = None


@dataclasses.dataclass
class Profile(dataclasses_utils.DataClassJsonMixin):
    field: str
    label: str | None = None
    displayName: str | None = None
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
