"""Command to list all tags."""
from __future__ import annotations

from contacts.utils import command_utils, contact_utils


def run() -> None:
    contacts = command_utils.read_contacts_from_disk()

    all_tags = contact_utils.extract_tags(contacts)
    all_tags_by_row = [all_tags[i : i + 5] for i in range(0, len(all_tags), 5)]
    for row in all_tags_by_row:
        for tag in row:
            print(tag.ljust(20), end="")
        print("")
