"""A date field on an iCloud contact."""
from __future__ import annotations

import re

from contacts import model
from contacts.common import error

NO_YEAR = 1604


def encoder(date: model.Date | None) -> str | None:
    """An encoder for a date field.

    Returns:
        A string representation of a model.Date.
    """
    if date is None:
        return None
    if date.month is None or date.day is None:
        raise error.EncodingError(date)
    return (
        f"{date.year if date.year is not None else NO_YEAR:04}"
        f"-{date.month:02}"
        f"-{date.day:02}"
    )


def decoder(date: str | None) -> model.Date | None:
    """A decoder for a date field.

    Returns:
        A model.Date or None.
    """
    from contacts import model

    if date is None:
        return None
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
        raise error.DecodingError(date)
    year = None if (year := int(date[:4])) == NO_YEAR else year
    month = int(date[5:7])
    day = int(date[8:])
    return model.Date(year=year, month=month, day=day)
