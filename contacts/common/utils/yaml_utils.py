from __future__ import annotations

import typing
from typing import Any

import yaml

if typing.TYPE_CHECKING:
    from common.utils import dataclasses_utils


def load(obj: str) -> Any:
    return yaml.load(obj, Loader=yaml.Loader)


def dump(yaml_obj: dataclasses_utils.DataClassJsonMixin) -> str:
    return yaml.dump(_remove_none(yaml_obj.to_dict()), allow_unicode=True, indent=4)


def _remove_none(dct: Any) -> dict:
    if issubclass(dct.__class__, dict):
        return {k: _remove_none(v) for k, v in dct.items() if v is not None}
    return dct


class Dumper(yaml.Dumper):
    last_indent = 0
    new_line = False

    def write_plain(self, text, split=True):
        if self.indent == self.last_indent:
            if self.new_line:
                self.stream.write("\n" + (self.indent - 1) * " ")
            self.new_line = not self.new_line
        else:
            self.last_indent = self.indent
            self.new_line = True
        super().write_plain(text, split)
