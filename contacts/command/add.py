from common import constant
from utils import command_utils, contact_utils, input_utils


def run() -> None:
    new_contacts = command_utils.read_contacts_from_disk(
        file_name=constant.NEW_CONTACT_FILE_NAME
    )

    contacts = command_utils.read_contacts_from_disk()

    for new_contact in new_contacts:
        new_contact_name = contact_utils.build_name_str(new_contact)
        for contact in contacts:
            if new_contact_name == contact_utils.build_name_str(contact):
                if not input_utils.yes_no_input(
                    f"A contact already exists with this name: {contact.to_json()}\n"
                    f"Do you want to continue?"
                ):
                    break
        else:
            contacts.append(new_contact)
            print(f"Adding new contact {new_contact_name}")
            command_utils.write_contacts_to_disk(contacts)
