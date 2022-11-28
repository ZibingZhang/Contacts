from __future__ import annotations

from typing import Any, Callable, Tuple, Union

import dataclasses_json
from common.utils import json_utils


# https://github.com/lidatong/dataclasses-json/issues/187#issuecomment-919992503
class DataClassJsonMixin(dataclasses_json.DataClassJsonMixin):
    dataclass_json_config = dataclasses_json.config(
        exclude=lambda f: f is None, undefined=dataclasses_json.Undefined.RAISE
    )["dataclasses_json"]

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


def diff(dataclass_1: DataClassJsonMixin, dataclass_2: DataClassJsonMixin) -> dict:
    return json_utils.diff(dataclass_1.to_dict(), dataclass_2.to_dict())
