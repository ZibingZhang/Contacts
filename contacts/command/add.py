import uuid

import model
from common import constant
from utils import command_utils, contact_utils, input_utils


def run(*, data_path) -> None:
    new_contacts = command_utils.read_contacts_from_disk(
        data_path=data_path, file_name=constant.NEW_CONTACT_FILE_NAME
    )

    contacts = command_utils.read_contacts_from_disk(data_path=data_path)

    for new_contact in new_contacts:
        new_contact.icloud = model.ICloud(uuid=str(uuid.uuid4()).upper())

        new_contact_name = contact_utils.extract_name(new_contact)
        for contact in contacts:
            if new_contact_name == contact_utils.extract_name(contact):
                if not input_utils.yes_no_input(
                    f"A contact already exists with this name: {contact.to_json()}\n"
                    f"Do you want to continue?"
                ):
                    break
        else:
            contacts.append(new_contact)
            print(f"Adding new contact {new_contact_name}")
            command_utils.write_contacts_to_disk(data_path=data_path, contacts=contacts)
