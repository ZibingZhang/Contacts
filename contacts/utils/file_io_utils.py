"""Utilities for file I/O."""
from __future__ import annotations

import json
import textwrap
from typing import Type, TypeVar

from contacts import model
from contacts.utils import dataclasses_utils

T = TypeVar("T", bound=dataclasses_utils.DataClassJsonMixin)


def read_json_object_as_dataclass_object(path: str, cls: Type[T]) -> T:
    """Read a dataclass object from a file.

    Read a json object from a file and transform it to a dataclass object.

    Args:
        path: The path of the file containing the json object.
        cls: The dataclass to convert the json object to.

    Returns:
        A dataclass object.
    """
    with open(path, encoding="utf-8") as f:
        obj = json.loads(f.read().strip())
    return cls.from_dict(obj)


def read_json_array_as_dataclass_objects(path: str, cls: Type[T]) -> list[T]:
    """Read dataclass objects from a file.

    Read a json array of objects from a file and transform them to a list of dataclass
    objects.

    Args:
        path: The path of the file containing the json array of objects.
        cls: The dataclass to convert the json objects to.

    Returns:
        A list of dataclass objects.
    """
    with open(path, encoding="utf-8") as f:
        objects = json.loads(f.read().strip())
    return [cls.from_dict(obj) for obj in objects]


def write_dataclass_objects_as_json_array(
    path: str, objects: list[dataclasses_utils.DataClassJsonMixin]
) -> None:
    """Write dataclass objects to a file.

    Transform a list of dataclass objects to a json array of objects and write them to
    a file.

    Args:
        path: The path of the file to write to.
        objects: The dataclass objects to write to the file.
    """
    output = ""
    if len(objects) > 0 and issubclass(objects[0].__class__, model.Contact):
        objects = sorted(objects, key=_contact_key)
    with open(path, mode="w", encoding="utf-8") as f:
        output += "[\n"
        output += textwrap.indent(",\n".join(obj.to_json() for obj in objects), "    ")
        output += "\n]\n"
        f.write(output)


def _contact_key(contact: model.Contact) -> str:
    return f"{contact.name.last_name}{contact.name.first_name}{contact.tags}"
