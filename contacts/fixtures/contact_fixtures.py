"""Test fixture for contacts."""
from __future__ import annotations

from contacts import model
from contacts.utils import uuid_utils


def build(**kwargs) -> model.Contact:
    """Builds a contact.

    Args:
        **kwargs: The contact fields.

    Returns:
        A contact.
    """
    if "name" not in kwargs:
        kwargs["name"] = model.Name()
    if "icloud" not in kwargs:
        kwargs["icloud"] = model.ICloudMetadata(uuid=uuid_utils.generate())
    return model.Contact(**kwargs)  # type: ignore
