import configparser

import transformer
from common.utils import file_io_utils
from data import icloud

ICLOUD_CONTACTS_FILE_NAME = "icloud-contacts.json"
ICLOUD_GROUPS_FILE_NAME = "icloud-groups.json"

CONTACTS_FILE_NAME = "contacts.json"
# GROUPS_FILE_NAME = "groups.json"


def get_icloud_contacts_and_groups(
    cached: bool,
) -> tuple[list[icloud.ICloudContact], list[icloud.ICloudGroup]]:
    if cached:
        contacts = file_io_utils.read_json_array_as_dataclass_objects(
            ICLOUD_CONTACTS_FILE_NAME, icloud.ICloudContact
        )
        groups = file_io_utils.read_json_array_as_dataclass_objects(
            ICLOUD_GROUPS_FILE_NAME, icloud.ICloudGroup
        )
        return contacts, groups

    config = configparser.ConfigParser()
    config.read("config.ini")
    username = config["login"]["username"]
    password = config["login"]["password"]

    session_manager = icloud.ICloudSessionManager(username, password)
    session_manager.login()
    contacts_manager = icloud.ICloudContactManager(session_manager)

    contacts, groups = contacts_manager.get_contacts_and_groups()

    file_io_utils.write_dataclass_objects_as_json_array(
        ICLOUD_CONTACTS_FILE_NAME, contacts
    )
    file_io_utils.write_dataclass_objects_as_json_array(ICLOUD_GROUPS_FILE_NAME, groups)

    return contacts, groups


if __name__ == "__main__":
    from common import patch

    patch.json_encode_uuid()

    icloud_contacts, icloud_groups = get_icloud_contacts_and_groups(cached=False)

    contacts = [
        transformer.icloud_contact_to_contact(icloud_contact)
        for icloud_contact in icloud_contacts
    ]

    file_io_utils.write_dataclass_objects_as_json_array(CONTACTS_FILE_NAME, contacts)
