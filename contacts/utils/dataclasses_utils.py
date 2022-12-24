"""Utilities for dataclasses."""
from __future__ import annotations

import dataclasses
from typing import Any, Callable, Tuple, TypeVar, Union

import dataclasses_json
import jsondiff

TDataClassJsonMixin = TypeVar("TDataClassJsonMixin", bound="DataClassJsonMixin")


def diff(dataclass_1: DataClassJsonMixin, dataclass_2: DataClassJsonMixin) -> dict:
    return jsondiff.diff(
        dataclass_1.to_dict(),
        dataclass_2.to_dict(),
        marshal=True,
        syntax="explicit",
    )


def _is_none(obj) -> bool:
    return obj is None


class DataClassJsonMixin(dataclasses_json.DataClassJsonMixin):
    # https://github.com/lidatong/dataclasses-json/issues/187#issuecomment-919992503
    dataclass_json_config = dataclasses_json.config(  # type: ignore
        exclude=_is_none, undefined=dataclasses_json.Undefined.RAISE  # type: ignore
    )["dataclasses_json"]

    def to_json(
        self: TDataClassJsonMixin,
        *,
        skipkeys: bool = False,
        ensure_ascii: bool = False,
        check_circular: bool = True,
        allow_nan: bool = True,
        indent: Union[int, str, None] = None,
        separators: Tuple[str, str] | None = None,
        default: Callable[..., Any] | None = None,
        sort_keys: bool = False,
        **kw,
    ) -> str:
        return super().to_json(
            skipkeys=skipkeys,
            ensure_ascii=ensure_ascii,
            check_circular=check_circular,
            allow_nan=allow_nan,
            indent=indent,
            separators=separators,  # type: ignore
            default=default,  # type: ignore
            sort_keys=sort_keys,
            **kw,
        )

    def copy(self: TDataClassJsonMixin) -> TDataClassJsonMixin:
        return self.__class__.from_dict(self.to_dict())

    def patch(self: TDataClassJsonMixin, patch: TDataClassJsonMixin) -> None:
        if not issubclass(patch.__class__, self.__class__):
            raise ValueError

        for field in dataclasses.fields(self):
            self_value = getattr(self, field.name)
            patch_value = getattr(patch, field.name)

            if patch_value is None:
                continue
            elif self_value is None:
                setattr(self, field.name, patch_value)
            elif issubclass(self_value.__class__, DataClassJsonMixin):
                self_value.patch(patch_value)
            else:
                setattr(self, field.name, patch_value)
