import dataclasses
import uuid as uuid_

import dataclasses_json

from common.utils import dataclasses_utils

NO_YEAR = 0


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
    day: int
    month: int
    year: int | None = None


@dataclasses.dataclass
class ICloud(dataclasses_utils.DataClassJsonMixin):
    uuid: uuid_.UUID | None = None


@dataclasses.dataclass
class Name(dataclasses_utils.DataClassJsonMixin):
    first_name: str | None = None
    nickname: str | None = None
    middle_name: str | None = None
    last_name: str | None = None
    chinese_name: str | None = None


@dataclasses.dataclass
class Contact(dataclasses_utils.DataClassJsonMixin):
    birthday: Date | None = date_field()
    icloud: ICloud | None = None
    name: Name | None = None
