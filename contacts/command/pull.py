import os

import jsondiff

import constant
import json
import model
import transformer
import utils
from data import icloud
from common.utils import file_io_utils, pretty_print_utils


def pull(cl_args):
    icloud_contacts, icloud_groups = utils.get_icloud_contacts_and_groups(
        cached=True, cache_path=cl_args.cache, config_path=cl_args.config
    )

    pulled_contacts = [
        transformer.icloud_contact_to_contact(icloud_contact)
        for icloud_contact in icloud_contacts
        if icloud_contact.contactId not in icloud.IGNORED_UUIDS
    ]
    current_contacts = file_io_utils.read_json_array_as_dataclass_objects(
        os.path.join(cl_args.data, constant.CONTACTS_FILE_NAME), model.Contact
    )

    icloud_id_to_pulled_contact_map = {
        contact.icloud.uuid: contact for contact in pulled_contacts
    }
    icloud_id_to_current_contact_map = {
        contact.icloud.uuid: contact for contact in current_contacts
    }

    for icloud_id in icloud_id_to_current_contact_map.keys():
        if icloud_id not in icloud_id_to_pulled_contact_map:
            continue

        pulled_contact = icloud_id_to_pulled_contact_map.get(icloud_id)
        current_contact = icloud_id_to_current_contact_map.get(icloud_id)

        diff = jsondiff.diff(
            pulled_contact.to_dict(),
            current_contact.to_dict(),
            marshal=True,
            syntax="explicit",
        )
        if diff:
            current_contact_display = pretty_print_utils.bordered(
                json.dumps(current_contact.to_dict(), indent=2)
            )
            diff_display = pretty_print_utils.bordered(json.dumps(diff, indent=2))
            print(pretty_print_utils.besides(current_contact_display, diff_display))

            accept_update = input("Accept update? [Y/N]: ")
            if accept_update.lower() == "y":
                icloud_id_to_current_contact_map[icloud_id] = pulled_contact

    file_io_utils.write_dataclass_objects_as_json_array(
        os.path.join(cl_args.data, constant.CONTACTS_FILE_NAME),
        list(icloud_id_to_current_contact_map.values()),
    )
