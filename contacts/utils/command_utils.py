"""High-level utilities for commands."""
from __future__ import annotations

import json
import os.path
from collections.abc import Sequence

from contacts import model
from contacts.common import constant
from contacts.dao import icloud_dao, obsidian_dao
from contacts.utils import (
    contact_utils,
    file_io_utils,
    input_utils,
    json_utils,
    progress_utils,
)


@progress_utils.annotate("Reading contacts from disk")
def read_contacts_from_disk(
    *, file_name: str = constant.CONTACTS_FILE_NAME
) -> list[model.Contact]:
    contacts = file_io_utils.read_json_array_as_dataclass_objects(
        os.path.join(constant.DATA_DIRECTORY, file_name),
        model.Contact,
    )
    progress_utils.message(f"Read {len(contacts)} contact(s)")
    return contacts


@progress_utils.annotate("Reading contacts from iCloud")
def read_contacts_from_icloud(cached: bool = False) -> list[model.Contact]:
    contacts, _ = icloud_dao.read_contacts_and_groups(cached=cached)
    progress_utils.message(f"Read {len(contacts)} contact(s)")
    return contacts


@progress_utils.annotate("Reading groups from iCloud")
def read_groups_from_icloud() -> list[model.Group]:
    _, groups = icloud_dao.read_contacts_and_groups()
    progress_utils.message(f"Read {len(groups)} groups(s)")
    return groups


@progress_utils.annotate("Writing contacts to disk")
def write_contacts_to_disk(
    contacts: Sequence[model.Contact], *, file_name: str = constant.CONTACTS_FILE_NAME
) -> None:
    file_io_utils.write_contacts_as_json_array(
        os.path.join(constant.DATA_DIRECTORY, file_name),
        contacts,
    )
    obsidian_dao.upsert_contacts(contacts)
    progress_utils.message(f"Wrote {len(contacts)} contact(s) to disk")


@progress_utils.annotate("Loading contact")
def write_loaded_contact_to_disk(contact: model.Contact) -> None:
    with open(
        os.path.join(constant.DATA_DIRECTORY, constant.LOADED_CONTACT_FILE_NAME), "w"
    ) as f:
        f.write(json_utils.dumps(contact.to_dict()))


@progress_utils.annotate("Reading loaded contact")
def read_loaded_contact_from_disk() -> model.Contact:
    with open(
        os.path.join(constant.DATA_DIRECTORY, constant.LOADED_CONTACT_FILE_NAME)
    ) as f:
        return model.Contact.from_json(f.read())


@progress_utils.annotate("Creating new iCloud contacts")
def write_new_contacts_to_icloud(contacts: list[model.Contact]) -> None:
    if len(contacts) > 0:
        icloud_dao.upsert_contacts(contacts)
    progress_utils.message(f"Created {len(contacts)} contact(s)")


@progress_utils.annotate("Updating iCloud contacts")
def write_updated_contacts_to_icloud(
    contacts: list[model.Contact],
) -> None:
    if len(contacts) > 0:
        icloud_dao.update_contacts(contacts)
    progress_utils.message(f"Updated {len(contacts)} contact(s)")


@progress_utils.annotate("Creating iCloud groups")
def write_new_group_to_icloud(icloud_group: model.Group) -> None:
    icloud_dao.create_group(icloud_group)
    progress_utils.message(
        f"Created group {icloud_group.name} "
        f"with {len(icloud_group.icloud.contact_uuids)} contact(s)"
    )


@progress_utils.annotate("Updating iCloud groups")
def write_updated_group_to_icloud(
    icloud_group: model.Group,
) -> None:
    icloud_dao.update_group(icloud_group)
    progress_utils.message(
        f"Updated group {icloud_group.name} "
        f"with {len(icloud_group.icloud.contact_uuids)} contact(s)"
    )


def get_contact_by_name(contacts: list[model.Contact]) -> model.Contact | None:
    name = input_utils.basic_input(
        "Enter the name of the contact to select", lower=True
    )

    matching_contacts = _get_matching_contacts(contacts, name)
    if len(matching_contacts) == 0:
        return None
    elif len(matching_contacts) == 1:
        return matching_contacts[0]
    else:
        for i, contact in enumerate(matching_contacts):
            print(f"{i + 1}. {contact_utils.build_name_and_tags_str(contact)}")

        selection_inp = input_utils.input_with_skip("Select the contact")
        while True:
            try:
                selection = int(selection_inp)
                if selection < 1:
                    selection_inp = input_utils.input_with_skip(
                        "Too low. Select the contact"
                    )
                    continue
                if selection > len(matching_contacts):
                    selection_inp = input_utils.input_with_skip(
                        "Too high. Select the contact"
                    )
                    continue
                break
            except ValueError:
                selection_inp = input_utils.input_with_skip(
                    "Not a number. Select the contact"
                )

        return matching_contacts[selection - 1]


def _get_matching_contacts(
    contacts: list[model.Contact], name: str
) -> list[model.Contact]:
    name = " ".join(name.strip().split())
    matching_contacts = []

    if name.count(" ") == 1:
        first_name, last_name = name.split()
        for contact in contacts:
            if (
                first_name in f"{contact.name.first_name}".lower()
                or first_name in f"{contact.name.nickname}".lower()
            ) and last_name in f"{contact.name.last_name}".lower():
                matching_contacts.append(contact)
                continue

    for contact in contacts:
        contact_name = (
            f"{contact.name.first_name} "
            f"{contact.name.nickname} "
            f"{contact.name.middle_name} "
            f"{contact.name.last_name}"
        ).lower()
        if name in contact_name:
            matching_contacts.append(contact)
    return matching_contacts
