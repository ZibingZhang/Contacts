import dataclasses
import os
import uuid

from utils import dataclasses_utils
from utils.file_io_utils import (
    read_json_array_as_dataclass_objects,
    write_dataclass_objects_as_json_array,
)


@dataclasses.dataclass
class Dataclass(dataclasses_utils.DataClassJsonMixin):
    field_1: int
    field_2: str


def test_reading_and_writing_dataclasses_are_inverses():
    object_1 = Dataclass(field_1=1, field_2="object 1")
    object_2 = Dataclass(field_1=2, field_2="object 2")
    written_objects = [object_1, object_2]
    file_path = str(uuid.uuid4())

    write_dataclass_objects_as_json_array(path=file_path, objects=written_objects)
    read_objects = read_json_array_as_dataclass_objects(path=file_path, cls=Dataclass)
    os.remove(file_path)

    assert written_objects == read_objects
