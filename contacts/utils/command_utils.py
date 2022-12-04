"""High-level utilities for commands."""
import os

import model
from common import constant
from dao import icloud
from utils import file_io_utils, progress_utils


@progress_utils.annotate("Reading contacts from disk")
def read_contacts_from_disk(
    *,
    data_path: str = constant.DEFAULT_DATA_DIRECTORY,
    file_name: str = constant.CONTACTS_FILE_NAME,
) -> list[model.Contact]:
    contacts = file_io_utils.read_json_array_as_dataclass_objects(
        os.path.join(data_path, file_name), model.Contact
    )
    progress_utils.message(f"Read {len(contacts)} contact(s)")
    return contacts


@progress_utils.annotate("Reading contacts from iCloud")
def read_contacts_from_icloud(*, cache_path: str, cached: bool) -> list[model.Contact]:
    contacts, _ = icloud.read_contacts_and_groups(cache_path=cache_path, cached=cached)
    progress_utils.message(f"Read {len(contacts)} contact(s)")
    return contacts


@progress_utils.annotate("Reading groups from iCloud")
def read_groups_from_icloud(*, cache_path: str, cached: bool) -> list[model.Group]:
    _, groups = icloud.read_contacts_and_groups(cache_path=cache_path, cached=cached)
    progress_utils.message(f"Read {len(groups)} groups(s)")
    return groups


@progress_utils.annotate("Writing contacts to disk")
def write_contacts_to_disk(
    contacts: list[model.Contact],
    *,
    data_path: str = constant.DEFAULT_DATA_DIRECTORY,
    file_name: str = constant.CONTACTS_FILE_NAME,
) -> None:
    file_io_utils.write_dataclass_objects_as_json_array(
        os.path.join(data_path, file_name),
        contacts,
    )
    progress_utils.message(f"Wrote {len(contacts)} contact(s) to disk")


@progress_utils.annotate("Creating new iCloud contacts")
def write_new_contacts_to_icloud(contacts: list[model.Contact]) -> None:
    if len(contacts) > 0:
        icloud.create_contacts(contacts)
    progress_utils.message(f"Created {len(contacts)} contact(s)")


@progress_utils.annotate("Updating iCloud contacts")
def write_updated_contacts_to_icloud(
    contacts: list[model.Contact],
) -> None:
    if len(contacts) > 0:
        icloud.update_contacts(contacts)
    progress_utils.message(f"Updated {len(contacts)} contact(s)")


@progress_utils.annotate("Creating iCloud groups")
def write_new_group_to_icloud(icloud_group: model.Group) -> None:
    icloud.create_group(icloud_group)
    progress_utils.message(
        f"Created group {icloud_group.name} "
        f"with {len(icloud_group.icloud.contact_uuids)} contact(s)"
    )


@progress_utils.annotate("Updating iCloud groups")
def write_updated_group_to_icloud(
    icloud_group: model.Group,
) -> None:
    icloud.update_group(icloud_group)
    progress_utils.message(
        f"Updated group {icloud_group.name} "
        f"with {len(icloud_group.icloud.contact_uuids)} contact(s)"
    )
