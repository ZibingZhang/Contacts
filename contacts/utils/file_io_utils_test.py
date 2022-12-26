"""Tests for contacts.utils.file_io_utils."""
from __future__ import annotations

import os.path

from contacts import model
from contacts.utils import file_io_utils, uuid_utils


def test_reading_and_writing_dataclasses_are_inverses() -> None:
    object_1 = model.PhoneNumber(country_code=1, number="1234")
    object_2 = model.PhoneNumber(country_code=86, number="5678")
    written_objects = [object_1, object_2]
    file_path = uuid_utils.generate()

    file_io_utils.write_dataclass_objects_as_json_array(
        path=file_path, objects=written_objects
    )
    read_objects = file_io_utils.read_json_array_as_dataclass_objects(
        path=file_path, cls=model.PhoneNumber
    )
    os.remove(file_path)

    assert written_objects == read_objects
