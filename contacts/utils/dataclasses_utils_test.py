"""Tests for contacts.utils.dataclasses_utils."""
from __future__ import annotations

import pytest

from contacts import model


def test_patch_dataclasses() -> None:
    contact = model.Contact(
        name=model.Name(first_name="John", last_name="Smith"),
        notes="notes",
        tags=["tag1", "tag2"],
    )
    patch = model.Contact(name=model.Name(first_name="Jane"), tags=["tag3"])

    contact.patch(patch)

    assert contact == model.Contact(
        name=model.Name(first_name="Jane", last_name="Smith"),
        notes="notes",
        tags=["tag3"],
    )


def test_patch_dataclass_error_if_patch_not_subclass() -> None:
    with pytest.raises(ValueError):
        name = model.Name()
        patch = model.PhoneNumber(
            country_code=model.CountryCode.NANP.value, number="911"
        )
        name.patch(patch)
