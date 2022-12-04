import model
from dao import icloud


def group_to_icloud_group(group: model.Group) -> icloud._model.ICloudGroup:
    return icloud._model.ICloudGroup(
        contactIds=group.icloud.contact_uuids,
        etag=group.icloud.etag,
        groupId=group.icloud.uuid,
        name=group.name,
        isGuardianApproved=False,
        whitelisted=False,
    )
