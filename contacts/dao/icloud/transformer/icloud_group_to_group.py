"""Convert an icloud.model.ICloudGroup into a model.Group."""
from __future__ import annotations

from contacts import model
from contacts.dao import icloud


def icloud_group_to_group(icloud_group: icloud.model.ICloudGroup) -> model.Group:
    """Convert an icloud.model.ICloudGroup into a model.Group.

    Args:
        icloud_group: The iCloud group to transform.

    Returns:
        The transformed model.Group.
    """
    return model.Group(
        icloud=model.group.ICloudGroupMetadata(
            contact_uuids=icloud_group.contactIds,
            etag=icloud_group.etag,
            uuid=icloud_group.groupId,
        ),
        name=icloud_group.name,
    )
