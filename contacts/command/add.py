import uuid

import constant
import model
from utils import command_utils


def add(*, data_path) -> None:
    new_contact = command_utils.read_contact_from_disk(
        data_path=data_path, file_name=constant.NEW_CONTACT_FILE_NAME
    )
    new_contact.icloud = model.ICloud(uuid=str(uuid.uuid4()).upper())

    contacts = command_utils.read_contacts_from_disk(data_path=data_path)

    new_contact_name = f"{new_contact.name.first_name} {new_contact.name.last_name}"
    for contact in contacts:
        if new_contact_name == f"{contact.name.first_name} {contact.name.last_name}":
            cont = input(
                f"A contact already exists with this name: {contact.to_json()}\n"
                f"Do you want to continue? [Y/N]: "
            )
            if cont.lower() != "y":
                return

    contacts.append(new_contact)
    command_utils.write_contacts_to_disk(data_path=data_path, contacts=contacts)
