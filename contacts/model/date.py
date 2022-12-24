"""The model for a dates."""
from __future__ import annotations

import dataclasses
import re
import typing

import dataclasses_json

from contacts.common import error
from contacts.utils import dataclasses_utils

if typing.TYPE_CHECKING:
    from contacts import model


def encoder(date: model.Date | None) -> str | None:
    """An encoder for a date field.

    Returns:
        A string representation of a model.Date.
    """
    if date is None:
        return None
    return (
        f"{date.year if date.year is not None else 'XXXX':04}"
        f"-{date.month if date.month is not None else 'XX':02}"
        f"-{date.day if date.day is not None else 'XX':02}"
    )


def decoder(date: str | None) -> model.Date | None:
    """A decoder for a date field.

    Returns:
        A model.Date or None.
    """
    from contacts import model

    if date is None:
        return None
    if not re.match(r"^[0-9X]{4}-[0-9X]{2}-[0-9X]{2}$", date):
        raise error.DecodingError(date)

    year_str = date[:4]
    month_str = date[5:7]
    day_str = date[8:]

    year = int(year_str) if year_str != "XXXX" else None
    month = int(month_str) if month_str != "XX" else None
    day = int(day_str) if day_str != "XX" else None

    return model.Date(year=year, month=month, day=day)


@dataclasses.dataclass
class DateRange(dataclasses_utils.DataClassJsonMixin):
    start: Date | None = dataclasses.field(
        metadata=dataclasses_json.config(
            decoder=decoder,
            encoder=encoder,
        )
    )
    end: Date | None = dataclasses.field(
        metadata=dataclasses_json.config(
            decoder=decoder,
            encoder=encoder,
        )
    )


@dataclasses.dataclass
class Date(dataclasses_utils.DataClassJsonMixin):
    day: int | None = None
    month: int | None = None
    year: int | None = None

    def __repr__(self) -> str:
        return encoder(self) or "XXXX-XX-XX"
