import json
from typing import Type, TypeVar

from common.utils import dataclasses_utils

T = TypeVar("T", bound=dataclasses_utils.DataClassJsonMixin)


def read_json_array_as_dataclass_objects(path: str, cls: Type[T]) -> list[T]:
    with open(path, encoding="utf-8") as f:
        objects = json.loads(f.read().strip())
    return [cls.from_dict(obj) for obj in objects]


def write_dataclass_objects_as_json_array(
    path: str, objects: list[dataclasses_utils.DataClassJsonMixin]
) -> None:
    with open(path, mode="w", encoding="utf-8") as f:
        f.write("[\n")
        for obj in objects[:-1]:
            f.write(f"    {obj.to_json()},\n")
        f.write(f"    {objects[-1].to_json()}\n")
        f.write("]\n")
