from __future__ import annotations

import dataclasses
import re
import typing

import dataclasses_json
from common import error

if typing.TYPE_CHECKING:
    import model


def new_field(*, required) -> dataclasses.Field:
    kwargs = {
        "metadata": dataclasses_json.config(
            decoder=date_decoder,
            encoder=date_encoder,
        )
    }

    if not required:
        kwargs["default"] = None

    return dataclasses.field(**kwargs)


def date_encoder(date: model.Date | None) -> str | None:
    """An encoder for a date field.

    Returns:
        A string representation of a model.Date.
    """
    if date is None:
        return
    return (
        f"{date.year if date.year is not None else 'XXXX':04}"
        f"-{date.month if date.month is not None else 'XX':02}"
        f"-{date.day if date.day is not None else 'XX':02}"
    )


def date_decoder(date: str | None) -> model.Date | None:
    """A decoder for a date field.

    Returns:
        A model.Date or None.
    """
    import model

    if date is None:
        return
    if not re.match(r"^[0-9X]{4}-[0-9X]{2}-[0-9X]{2}$", date):
        raise error.DecodingError(date)

    year = date[:4]
    month = date[5:7]
    day = date[8:]

    year = int(year) if year != "XXXX" else None
    month = int(month) if month != "XX" else None
    day = int(day) if day != "XX" else None

    return model.Date(year=year, month=month, day=day)
