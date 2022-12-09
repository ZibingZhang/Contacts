"""Convert a model.Group into an icloud.model.ICloudGroup."""
from __future__ import annotations

from contacts import model
from contacts.dao import icloud


def group_to_icloud_group(group: model.Group) -> icloud.model.ICloudGroup:
    """Convert a model.Contact into an icloud.model.ICloudContact.

    Args:
        group: The contact to transform.

    Returns:
        The transformed icloud.model.ICloudGroup.
    """
    return icloud.model.ICloudGroup(
        contactIds=group.icloud.contact_uuids,
        etag=group.icloud.etag,
        groupId=group.icloud.uuid,
        name=group.name,
        isGuardianApproved=False,
        whitelisted=False,
    )
