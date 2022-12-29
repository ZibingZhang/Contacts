"""Command to tag contacts."""
from __future__ import annotations

import time
from typing import cast

from contacts.utils import command_utils, dataclasses_utils, input_utils, json_utils, pretty_print_utils


def run() -> None:
    contacts = command_utils.read_contacts_from_disk()
    id_to_contact_map = {contact.id: contact for contact in contacts}

    updated_contact = command_utils.read_loaded_contact_from_disk()
    current_contact = id_to_contact_map[updated_contact.id]

    diff = dataclasses_utils.diff(current_contact, updated_contact)
    if diff:
        current_contact_display = pretty_print_utils.bordered(
            json_utils.dumps(current_contact.to_dict())
        )
        diff_display = pretty_print_utils.bordered(json_utils.dumps(diff))
        print(pretty_print_utils.besides(current_contact_display, diff_display))

        if input_utils.yes_no_input("Accept update?"):
            updated_contact.mtime = time.time()
            id_to_contact_map[updated_contact.id] = updated_contact
            command_utils.write_contacts_to_disk(cast(list, id_to_contact_map.values()))
