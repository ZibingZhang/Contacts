import model
from dao import icloud


def icloud_group_to_group(group: icloud._model.ICloudGroup) -> model.Group:
    return model.Group(
        icloud=model.group.ICloudMetadata(
            contact_uuids=group.contactIds, etag=group.etag, uuid=group.groupId
        ),
        name=group.name,
    )
