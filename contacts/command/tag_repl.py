"""Command to start the tag repl."""
from __future__ import annotations

from collections.abc import Sequence

from contacts import model
from contacts.common import error
from contacts.utils import command_utils, contact_utils, input_utils


def run() -> None:
    print("Adding tags to contacts...")
    while True:
        try:
            contacts = command_utils.read_contacts_from_disk()
            _add_tags_to_contact(contacts)
        except error.CommandSkipError:
            print("Skipping...")


def _add_tags_to_contact(contacts: Sequence[model.Contact]) -> None:
    contact = command_utils.get_contact_by_name(contacts)
    if contact is None:
        return None

    print(contact_utils.build_name_and_tags_str(contact))
    while True:
        new_tags = [
            tag.strip()
            for tag in input_utils.input_with_skip("Enter the tags to add").split(",")
        ]
        tags = sorted(set((contact.tags or []) + new_tags))

        print(f"tags: {tags}")
        if input_utils.yes_no_input("Continue with this set of tags?"):
            break

    contact.tags = tags
    command_utils.write_contacts_to_disk(contacts)
