from __future__ import annotations

import dataclasses
import re
import typing

import dataclasses_json
from common import error

if typing.TYPE_CHECKING:
    import model

NO_YEAR = 1604


def new_field(*, required) -> dataclasses.Field:
    kwargs = {
        "metadata": dataclasses_json.config(
            decoder=_date_decoder,
            encoder=_date_encoder,
        )
    }

    if not required:
        kwargs["default"] = None

    return dataclasses.field(**kwargs)


def _date_encoder(date: model.Date | None) -> str | None:
    """An encoder for a date field.

    Returns:
        A string representation of a model.Date.
    """
    if date is None:
        return
    if date.month is None or date.day is None:
        raise error.EncodingError
    return (
        f"{date.year if date.year is not None else NO_YEAR:04}"
        f"-{date.month:02}"
        f"-{date.day:02}"
    )


def _date_decoder(date: str | None) -> model.Date | None:
    """A decoder for a date field.

    Returns:
        A model.Date or None.
    """
    import model

    if date is None:
        return
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
        raise error.DecodingError
    year = int(date[:4])
    year = year if year != NO_YEAR else None
    month = int(date[5:7])
    day = int(date[8:])
    return model.Date(year=year, month=month, day=day)
