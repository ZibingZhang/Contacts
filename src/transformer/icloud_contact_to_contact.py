from __future__ import annotations

import typing

import model

if typing.TYPE_CHECKING:
    from data import icloud


def icloud_contact_to_contact(icloud_contact: icloud.ICloudContact) -> model.Contact:
    return model.Contact(
        name=model.Name(
            first_name=icloud_contact.firstName,
            nickname=icloud_contact.nickName,
            last_name=icloud_contact.lastName,
        )
    )
