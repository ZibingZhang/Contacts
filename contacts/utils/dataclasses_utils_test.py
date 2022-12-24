"""Tests for contacts.utils.dataclasses_utils."""
from __future__ import annotations

from contacts import model
from contacts.utils import uuid_utils


def test_patch_dataclasses() -> None:
    icloud_metadata = model.ICloudMetadata(uuid=uuid_utils.generate())

    contact = model.Contact(
        name=model.Name(first_name="John", last_name="Smith"),
        icloud=icloud_metadata,
        notes="notes",
        tags=["tag1", "tag2"],
    )
    patch = model.Contact(
        name=model.Name(first_name="Jane"),
        icloud=icloud_metadata,
        tags=["tag3"],
    )

    contact.patch(patch)

    assert contact == model.Contact(
        name=model.Name(first_name="Jane", last_name="Smith"),
        icloud=icloud_metadata,
        notes="notes",
        tags=["tag3"],
    )
