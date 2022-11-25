from __future__ import annotations

import re
import typing
from typing import Any, Callable, Tuple, Union

import dataclasses_json

from common import error

if typing.TYPE_CHECKING:
    import model


# https://github.com/lidatong/dataclasses-json/issues/187#issuecomment-919992503
class DataClassJsonMixin(dataclasses_json.DataClassJsonMixin):
    dataclass_json_config = dataclasses_json.config(exclude=lambda f: f is None)[
        "dataclasses_json"
    ]

    def to_json(
        self,
        *,
        skipkeys: bool = False,
        ensure_ascii: bool = False,
        check_circular: bool = True,
        allow_nan: bool = True,
        indent: Union[int, str] | None = None,
        separators: Tuple[str, str] | None = None,
        default: Callable[[Any, ...], Any] | None = None,
        sort_keys: bool = False,
        **kw,
    ) -> str:
        return super().to_json(
            skipkeys=skipkeys,
            ensure_ascii=ensure_ascii,
            check_circular=check_circular,
            allow_nan=allow_nan,
            indent=indent,
            separators=separators,
            default=default,
            sort_keys=sort_keys,
            **kw,
        )


def date_encoder(no_year: int) -> Callable[[model.Date], str | None]:
    """Creates an encoder for a date field.

    Args:
        no_year: The year to use if none exists on the model.Date.

    Returns:
        A function which encodes a model.Date.
    """

    def encoder(date: model.Date | None) -> str | None:
        if date is None:
            return
        return (
            f"{date.year if date.year is not None else no_year:04}"
            f"-{date.month:02}"
            f"-{date.day:02}"
        )

    return encoder


def date_decoder(no_year: int) -> Callable[[str], model.Date | None]:
    """Creates a decoder for a date field.

    Args:
        no_year: The year to use if none exists on the model.Date.

    Returns:
        A function which decodes a model.Date.
    """

    def decoder(date: str | None) -> model.Date | None:
        import model

        if date is None:
            return
        if not re.match(r"^\d{4}-\d{2}-\d{2}$", date):
            print(date)
            raise error.DecodingError

        year = int(date[:4])
        year = year if year != no_year else None
        month = int(date[5:7])
        day = int(date[8:])
        return model.Date(year=year, month=month, day=day)

    return decoder
