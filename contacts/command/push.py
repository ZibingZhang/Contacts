import json
import os

import constant
import model
import transformer
from common.utils import (
    dataclasses_utils,
    file_io_utils,
    icloud_utils,
    pretty_print_utils,
)

from data import icloud


def push(cl_args) -> None:
    contacts = file_io_utils.read_json_array_as_dataclass_objects(
        os.path.join(cl_args.data, constant.CONTACTS_FILE_NAME), model.Contact
    )

    pushed_contacts = [
        transformer.contact_to_icloud_contact(contact) for contact in contacts
    ]
    icloud_contacts, _ = icloud_utils.get_contacts_and_groups(
        cached=False, cache_path=cl_args.cache, config_path=cl_args.config
    )
    for icloud_contact in icloud_contacts:
        icloud_contact.normalized = None

    icloud_id_to_pushed_contact_map = {
        contact.contactId: contact for contact in pushed_contacts
    }
    icloud_id_to_current_contact_map = {
        contact.contactId: contact for contact in icloud_contacts
    }

    pushed_contact_ids = icloud_id_to_pushed_contact_map.keys()
    current_contact_ids = icloud_id_to_current_contact_map.keys()

    for icloud_id in pushed_contact_ids - current_contact_ids:
        # TODO: create contact
        ...

    updated_contacts = []
    for icloud_id in pushed_contact_ids & current_contact_ids:
        pushed_contact = icloud_id_to_pushed_contact_map.get(icloud_id)
        current_contact = icloud_id_to_current_contact_map.get(icloud_id)

        diff = dataclasses_utils.diff(current_contact, pushed_contact)
        if diff:
            current_contact_display = pretty_print_utils.bordered(
                json.dumps(current_contact.to_dict(), indent=2)
            )
            diff_display = pretty_print_utils.bordered(json.dumps(diff, indent=2))
            print(pretty_print_utils.besides(current_contact_display, diff_display))

            updates = diff.get("$update")
            if updates is not None and "notes" in updates:
                print(
                    pretty_print_utils.besides(
                        pretty_print_utils.bordered(current_contact.notes),
                        pretty_print_utils.bordered(pushed_contact.notes),
                    )
                )
            accept_update = input("Accept update? [Y/N]: ")
            if accept_update.lower() == "y":
                icloud_id_to_current_contact_map[icloud_id] = pushed_contact
                updated_contacts.append(pushed_contact)

    if cl_args.write:
        contacts_manager = icloud.ICloudManager().contact_manager
        contacts_manager.update_contacts(updated_contacts)
    else:
        print("Would've written " + str(len(updated_contacts)) + " contacts")

    file_io_utils.write_dataclass_objects_as_json_array(
        os.path.join(cl_args.cache, constant.ICLOUD_CONTACTS_FILE_NAME),
        list(icloud_id_to_current_contact_map.values()),
    )
