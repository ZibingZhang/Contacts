"""Command to rename a tag."""
from __future__ import annotations

from contacts.utils import command_utils, contact_utils, input_utils


def run(old: str, new: str) -> None:
    contacts = command_utils.read_contacts_from_disk()

    print(f"Changing tag from {old} to {new}.")

    all_tags = contact_utils.extract_tags(contacts)
    if new in all_tags:
        if not input_utils.yes_no_input("Tag already exists. Do you wish to continue?"):
            return None

    count = 0
    for contact in contacts:
        if contact.tags is not None and old in contact.tags:
            contact.tags.remove(old)
            contact.tags += [new]
            count += 1

    if input_utils.yes_no_input(f"Update {count} contact(s)?"):
        command_utils.write_contacts_to_disk(contacts)
