"""Command to pull contacts from a remote source."""
from __future__ import annotations

import time
from typing import cast

from contacts import model
from contacts.utils import (
    command_utils,
    dataclasses_utils,
    input_utils,
    json_utils,
    pretty_print_utils,
)


def run(*, cached: bool) -> None:
    icloud_contacts = command_utils.read_contacts_from_icloud(cached=cached)
    disk_contacts = command_utils.read_contacts_from_disk()

    icloud_id_to_icloud_contact_map: dict[str, model.Contact] = {
        cast(model.ICloudMetadata, contact.icloud).uuid: contact
        for contact in icloud_contacts
    }
    icloud_id_to_disk_contact_map: dict[str, model.Contact] = {
        contact.icloud.uuid: contact
        for contact in disk_contacts
        if contact.icloud is not None
    }

    for icloud_id in (
        icloud_id_to_icloud_contact_map.keys() - icloud_id_to_disk_contact_map.keys()
    ):
        icloud_contact = icloud_id_to_icloud_contact_map[icloud_id]
        print(pretty_print_utils.bordered(json_utils.dumps(icloud_contact.to_dict())))
        if input_utils.yes_no_input("Accept creation?"):
            icloud_contact.mtime = time.time()
            icloud_id_to_disk_contact_map[icloud_id] = icloud_contact

    for icloud_id in (
        icloud_id_to_disk_contact_map.keys() & icloud_id_to_icloud_contact_map.keys()
    ):
        icloud_contact = icloud_id_to_icloud_contact_map[icloud_id]
        disk_contact = icloud_id_to_disk_contact_map[icloud_id]

        updated_contact = disk_contact.copy()
        updated_contact.patch(icloud_contact)
        diff = dataclasses_utils.diff(disk_contact, updated_contact)

        if diff:
            if _only_etag_updated(diff):
                icloud_id_to_disk_contact_map[icloud_id] = updated_contact
                continue

            current_contact_display = pretty_print_utils.bordered(
                json_utils.dumps(disk_contact.to_dict())
            )
            diff_display = pretty_print_utils.bordered(json_utils.dumps(diff))
            print(pretty_print_utils.besides(current_contact_display, diff_display))

            if input_utils.yes_no_input("Accept update?"):
                updated_contact.mtime = time.time()
                icloud_id_to_disk_contact_map[icloud_id] = updated_contact

    command_utils.write_contacts_to_disk(list(icloud_id_to_disk_contact_map.values()))


def _only_etag_updated(diff: dict) -> bool:
    if set(diff.keys()) != {"$update"}:
        return False
    update = diff["$update"]
    if set(update.keys()) != {"icloud"}:
        return False
    icloud_diff = update["icloud"]
    if set(icloud_diff.keys()) == {"$update"}:
        icloud_update = icloud_diff["$update"]
        return set(icloud_update.keys()) == {"etag"}
    if set(icloud_diff.keys()) == {"$insert"}:
        icloud_insert = icloud_diff["$insert"]
        return set(icloud_insert.keys()) == {"etag"}
    return False
