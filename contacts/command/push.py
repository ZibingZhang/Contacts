import command
import transformer
from utils import (
    command_utils,
    dataclasses_utils,
    input_utils,
    json_utils,
    pretty_print_utils,
)


def run(*, cache_path: str, data_path: str, force: bool, write: bool) -> None:
    contacts = command_utils.read_contacts_from_disk(data_path=data_path)

    pushed_contacts = [
        transformer.contact_to_icloud_contact(contact) for contact in contacts
    ]

    icloud_contacts = command_utils.read_contacts_from_icloud(
        cache_path=cache_path, cached=False
    )
    for icloud_contact in icloud_contacts:
        icloud_contact.normalized = None

    icloud_id_to_pushed_contact_map = {
        contact.contactId: contact for contact in pushed_contacts
    }
    icloud_id_to_icloud_contact_map = {
        contact.contactId: contact for contact in icloud_contacts
    }

    pushed_contact_ids = icloud_id_to_pushed_contact_map.keys()
    icloud_contact_ids = icloud_id_to_icloud_contact_map.keys()

    new_contacts = []
    for icloud_id in pushed_contact_ids - icloud_contact_ids:
        new_contact = icloud_id_to_pushed_contact_map.get(icloud_id)

        print(pretty_print_utils.bordered(json_utils.dumps(new_contact.to_dict())))

        if input_utils.yes_no_input("Accept creation?"):
            icloud_id_to_icloud_contact_map[icloud_id] = new_contact
            new_contacts.append(new_contact)

    if write:
        command_utils.write_new_contacts_to_icloud(icloud_contacts=new_contacts)
    else:
        print(f"Would have created {len(new_contacts)} contact(s)")

    updated_contacts = []
    for icloud_id in pushed_contact_ids & icloud_contact_ids:
        pushed_contact = icloud_id_to_pushed_contact_map.get(icloud_id)
        icloud_contact = icloud_id_to_icloud_contact_map.get(icloud_id)

        diff = dataclasses_utils.diff(icloud_contact, pushed_contact)
        if diff:
            current_contact_display = pretty_print_utils.bordered(
                json_utils.dumps(icloud_contact.to_dict())
            )
            diff_display = pretty_print_utils.bordered(json_utils.dumps(diff))
            print(pretty_print_utils.besides(current_contact_display, diff_display))

            updates = diff.get("$update")
            if updates is not None and "notes" in updates:
                print(
                    pretty_print_utils.besides(
                        pretty_print_utils.bordered(icloud_contact.notes),
                        pretty_print_utils.bordered(pushed_contact.notes),
                    )
                )

            if force or input_utils.yes_no_input("Accept update?"):
                icloud_id_to_icloud_contact_map[icloud_id] = pushed_contact
                updated_contacts.append(pushed_contact)

    if write:
        command_utils.write_updated_contacts_to_icloud(icloud_contacts=updated_contacts)
    else:
        print(f"Would have updated {len(updated_contacts)} contact(s)")

    if write and (len(new_contacts) > 0 or len(updated_contacts) > 0):
        print("Pulling contact(s) to sync etag(s)...")
        _pull_contacts_to_sync_etag(cache_path, data_path)


def _pull_contacts_to_sync_etag(cache_path: str, data_path: str) -> None:
    command.pull.run(
        cache_path=cache_path,
        cached=False,
        data_path=data_path,
    )
