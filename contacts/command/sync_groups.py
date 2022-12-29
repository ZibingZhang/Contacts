"""Command to update remote contact groups."""
import time
from collections.abc import Callable

from contacts import model
from contacts.utils import command_utils, uuid_utils


def run() -> None:
    contacts = command_utils.read_contacts_from_disk()
    icloud_groups = command_utils.read_groups_from_icloud(cached=False)
    group_name_to_group_map = {
        icloud_group.name: icloud_group for icloud_group in icloud_groups
    }

    for name, predicate in GROUP_NAME_TO_PREDICATE_MAP.items():
        contact_uuids = [
            contact.icloud.uuid
            for contact in contacts
            if contact.icloud is not None and predicate(contact)
        ]
        if name not in group_name_to_group_map.keys():
            command_utils.write_new_group_to_icloud(
                model.Group(
                    icloud=model.group.ICloudMetadata(
                        contact_uuids=contact_uuids,
                        uuid=uuid_utils.generate(),
                    ),
                    name=name,
                )
            )
        else:
            group = group_name_to_group_map[name]
            group.icloud.contact_uuids = contact_uuids
            command_utils.write_updated_group_to_icloud(group)
        time.sleep(1)


def _has_tag_predicate_factory(tag: str) -> Callable[[model.Contact], bool]:
    def has_tag_predicate(contact: model.Contact) -> bool:
        return contact.tags is not None and tag in contact.tags

    return has_tag_predicate


def _has_phone_number_predicate(contact: model.Contact) -> bool:
    return contact.phone_numbers is not None


GROUP_NAME_TO_PREDICATE_MAP: dict[str, Callable[[model.Contact], bool]] = {
    "CTY": _has_tag_predicate_factory("CTY"),
    "HubSpot": _has_tag_predicate_factory("HubSpot"),
    "Needham": _has_tag_predicate_factory("Needham"),
    "Northeastern": _has_tag_predicate_factory("NU"),
    "Phone Numbers": _has_phone_number_predicate,
    "PowerAdvocate": _has_tag_predicate_factory("PowerAdvocate"),
    "Sharks": _has_tag_predicate_factory("Sharks"),
}
