import dataclasses

import dataclasses_json

from common import dataclasses_utils

NO_YEAR = 0


def date_field():
    return dataclasses.field(
        metadata=dataclasses_json.config(
            encoder=dataclasses_utils.date_encoder(NO_YEAR),
            decoder=dataclasses_utils.date_decoder(NO_YEAR),
        )
    )


@dataclasses.dataclass
class Date:
    day: int
    month: int
    year: int | None = None


@dataclasses.dataclass
class Name:
    first_name: str | None = None
    nickname: str | None = None
    middle_name: str | None = None
    last_name: str | None = None
    chinese_name: str | None = None


@dataclasses.dataclass
class Contact:
    name: Name | None = None
