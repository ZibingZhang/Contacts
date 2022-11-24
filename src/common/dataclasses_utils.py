from __future__ import annotations

import re
import typing
from typing import Callable

if typing.TYPE_CHECKING:
    import model

from common import error


def date_encoder(no_year: int) -> Callable[[model.Date], str]:
    """Encodes

    :param no_year:
    :return:
    """

    def encoder(date: model.Date) -> str:
        return (
            f"{date.year if date.year is not None else no_year}-{date.month}-{date.day}"
        )

    return encoder


def date_decoder(no_year: int) -> Callable[[str], model.Date | None]:
    def decoder(date: str) -> model.Date | None:
        import model

        if date is None:
            return None
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
            raise error.DecodingError

        year = int(date[:4])
        year = year if year != no_year else None
        month = int(date[5:7])
        day = int(date[8:])
        return model.Date(year=year, month=month, day=day)

    return decoder
