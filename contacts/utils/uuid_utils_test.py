"""Tests for contacts.utils.uuid_utils."""
from __future__ import annotations

import re
import unittest.mock as mock

from contacts.utils import uuid_utils


def test_delegate_to_uuid_uuid4() -> None:
    with mock.patch("uuid.uuid4") as mock_uuid4:
        uuid_utils.generate()

    mock_uuid4.assert_called_once()


def test_format() -> None:
    assert re.match(r"^\w{8}-\w{4}-\w{4}-\w{4}-\w{12}$", uuid_utils.generate())
