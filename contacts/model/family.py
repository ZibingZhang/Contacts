"""The model for a family."""
from __future__ import annotations

import dataclasses

import dataclasses_json

from contacts.utils import dataclasses_utils


def _children_decoder(d: list[dict | int] | None) -> list[Family | int] | None:
    return (
        None
        if d is None
        else [e if isinstance(e, int) else Family.from_dict(e) for e in d]
    )


@dataclasses.dataclass(repr=False)
class Family(dataclasses_utils.DataClassJsonMixin):
    parents: list[int] | None = None
    children: list[Family | int] | None = dataclasses.field(
        default=None,
        metadata=dataclasses_json.config(decoder=_children_decoder),
    )
