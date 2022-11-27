import os

import constant
import transformer
import utils
from data import icloud
from common.utils import file_io_utils


def pull(cl_args):
    icloud_contacts, icloud_groups = utils.get_icloud_contacts_and_groups(
        cached=False, cache_path=cl_args.cache, config_path=cl_args.config
    )

    contacts = [
        transformer.icloud_contact_to_contact(icloud_contact)
        for icloud_contact in icloud_contacts
        if icloud_contact.contactId not in icloud.IGNORED_UUIDS
    ]

    file_io_utils.write_dataclass_objects_as_json_array(
        os.path.join(cl_args.data, constant.CONTACTS_FILE_NAME), contacts
    )
