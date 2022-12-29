"""Command to tag contacts."""
from __future__ import annotations

from contacts.utils import command_utils


def run() -> None:
    contacts = command_utils.read_contacts_from_disk()
    contact = command_utils.get_contact_by_name(contacts)
    if contact is None:
        return None
    command_utils.write_loaded_contact_to_disk(contact)
