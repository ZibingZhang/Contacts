"""Command to pull contacts from a remote source."""
from __future__ import annotations

from contacts.utils import (
    command_utils,
    dataclasses_utils,
    input_utils,
    json_utils,
    pretty_print_utils,
)


def run(*, cached: bool) -> None:
    pulled_contacts = command_utils.read_contacts_from_icloud(cached=cached)
    disk_contacts = command_utils.read_contacts_from_disk()

    icloud_id_to_pulled_contact_map = {
        contact.icloud.uuid: contact for contact in pulled_contacts
    }
    icloud_id_to_current_contact_map = {
        contact.icloud.uuid: contact for contact in disk_contacts
    }

    for icloud_id in (
        icloud_id_to_pulled_contact_map.keys() - icloud_id_to_current_contact_map.keys()
    ):
        pulled_contact = icloud_id_to_pulled_contact_map.get(icloud_id)
        print(pretty_print_utils.bordered(json_utils.dumps(pulled_contact.to_dict())))
        if input_utils.yes_no_input("Accept creation?"):
            icloud_id_to_current_contact_map[icloud_id] = pulled_contact

    for icloud_id in (
        icloud_id_to_current_contact_map.keys() & icloud_id_to_pulled_contact_map.keys()
    ):
        pulled_contact = icloud_id_to_pulled_contact_map.get(icloud_id)
        current_contact = icloud_id_to_current_contact_map.get(icloud_id)
        updated_contact = current_contact.copy()
        updated_contact.patch(pulled_contact)

        diff = dataclasses_utils.diff(current_contact, updated_contact)
        if diff:
            if _only_etag_updated(diff):
                icloud_id_to_current_contact_map[icloud_id] = updated_contact
                continue

            current_contact_display = pretty_print_utils.bordered(
                json_utils.dumps(current_contact.to_dict())
            )
            diff_display = pretty_print_utils.bordered(json_utils.dumps(diff))
            print(pretty_print_utils.besides(current_contact_display, diff_display))

            if input_utils.yes_no_input("Accept update?"):
                icloud_id_to_current_contact_map[icloud_id] = updated_contact

    command_utils.write_contacts_to_disk(
        list(icloud_id_to_current_contact_map.values())
    )


def _only_etag_updated(diff: dict) -> bool:
    if set(diff.keys()) != {"$update"}:
        return False
    update = diff.get("$update")
    if set(update.keys()) != {"icloud"}:
        return False
    icloud_diff = update.get("icloud")
    if set(icloud_diff.keys()) == {"$update"}:
        icloud_update = icloud_diff.get("$update")
        return set(icloud_update.keys()) == {"etag"}
    if set(icloud_diff.keys()) == {"$insert"}:
        icloud_insert = icloud_diff.get("$insert")
        return set(icloud_insert.keys()) == {"etag"}
    return False
