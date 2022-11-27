import configparser
import os
import parser

import transformer
from common.utils import file_io_utils
from data import icloud
import utils


CONTACTS_FILE_NAME = "contacts.json"
# GROUPS_FILE_NAME = "groups.json"


if __name__ == "__main__":
    args = parser.parse_arguments_with_init()

    icloud_contacts, icloud_groups = utils.get_icloud_contacts_and_groups(
        cached=True, cache_path=args.cache, config_path=args.config
    )

    # utils.icloud_manager_login(config_path=args.config)
    # icloud_contact_manager = icloud.ICloudManager().contact_manager
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

    file_io_utils.write_dataclass_objects_as_json_array(
        os.path.join(args.data, CONTACTS_FILE_NAME), contacts
    )
