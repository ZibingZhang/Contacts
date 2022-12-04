import os
import uuid

import model
from utils import uuid_utils
from utils.file_io_utils import (
    read_json_array_as_dataclass_objects,
    write_dataclass_objects_as_json_array,
)


def test_reading_and_writing_dataclasses_are_inverses():
    object_1 = model.PhoneNumber(
        country_code=model.CountryCode.NANP.value, number="1234"
    )
    object_2 = model.PhoneNumber(
        country_code=model.CountryCode.CHINA.value, number="5678"
    )
    written_objects = [object_1, object_2]
    file_path = uuid_utils.generate()

    write_dataclass_objects_as_json_array(path=file_path, objects=written_objects)
    read_objects = read_json_array_as_dataclass_objects(
        path=file_path, cls=model.PhoneNumber
    )
    os.remove(file_path)

    assert written_objects == read_objects
