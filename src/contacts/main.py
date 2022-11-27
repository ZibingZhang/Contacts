import configparser

import transformer
from common.utils import file_io_utils
from data import icloud

ICLOUD_CONTACTS_FILE_NAME = "icloud-contacts.json"
ICLOUD_GROUPS_FILE_NAME = "icloud-groups.json"

CONTACTS_FILE_NAME = "contacts.json"
# GROUPS_FILE_NAME = "groups.json"


def get_icloud_contact_manager() -> icloud.ICloudContactManager:
    config = configparser.ConfigParser()
    config.read("config.ini")
    username = config["login"]["username"]
    password = config["login"]["password"]
    return icloud.ICloudContactManager(username, password)


def get_icloud_contacts_and_groups(
    cached: bool = False,
) -> tuple[list[icloud.ICloudContact], list[icloud.ICloudGroup]]:
    if cached:
        contacts = file_io_utils.read_json_array_as_dataclass_objects(
            ICLOUD_CONTACTS_FILE_NAME, icloud.ICloudContact
        )
        groups = file_io_utils.read_json_array_as_dataclass_objects(
            ICLOUD_GROUPS_FILE_NAME, icloud.ICloudGroup
        )
        return contacts, groups

    contact_manager = get_icloud_contact_manager()
    contacts, groups = contact_manager.get_contacts_and_groups()

    file_io_utils.write_dataclass_objects_as_json_array(
        ICLOUD_CONTACTS_FILE_NAME, contacts
    )
    file_io_utils.write_dataclass_objects_as_json_array(ICLOUD_GROUPS_FILE_NAME, groups)

    return contacts, groups


def get_test_contact(
    icloud_contacts: list[icloud.ICloudContact],
    uuid: str = "623ae0b7-eb13-47bb-8ccf-09f2eae2e4a3",
) -> icloud.ICloudContact:
    for contact in icloud_contacts:
        if str(contact.contactId) == uuid:
            return contact
    raise ValueError


if __name__ == "__main__":
    icloud_contacts, icloud_groups = get_icloud_contacts_and_groups(cached=True)

    # icloud_contact_manager = get_icloud_contact_manager()
    # updated_contacts = []
    # for icloud_contact in icloud_contacts:
    #     if icloud_contact.contactId in icloud.IGNORED_UUIDS:
    #         continue
    #
    #     updated = False
    #
    #     if updated:
    #         updated_contacts.append(icloud_contact)
    #
    # if updated_contacts:
    #     icloud_contact_manager.update_contacts(updated_contacts)

    contacts = [
        transformer.icloud_contact_to_contact(icloud_contact)
        for icloud_contact in icloud_contacts
        if icloud_contact.contactId not in icloud.IGNORED_UUIDS
    ]

    file_io_utils.write_dataclass_objects_as_json_array(CONTACTS_FILE_NAME, contacts)
