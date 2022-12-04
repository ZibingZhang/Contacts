"""High-level utilities for commands."""
import os

import model
from common import constant
from utils import file_io_utils, icloud_utils, progress_utils

from data import icloud


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
def read_contacts_from_icloud(
    *, cache_path: str, cached: bool
) -> list[icloud.ICloudContact]:
    icloud_contacts, _ = icloud_utils.get_contacts_and_groups(
        cache_path=cache_path, cached=cached
    )
    progress_utils.message(f"Read {len(icloud_contacts)} contact(s)")
    return icloud_contacts


@progress_utils.annotate("Reading groups from iCloud")
def read_groups_from_icloud(
    *, cache_path: str, cached: bool
) -> list[icloud.ICloudGroup]:
    _, icloud_groups = icloud_utils.get_contacts_and_groups(
        cache_path=cache_path, cached=cached
    )
    progress_utils.message(f"Read {len(icloud_groups)} groups(s)")
    return icloud_groups


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
def write_new_contacts_to_icloud(icloud_contacts: list[icloud.ICloudContact]) -> None:
    if len(icloud_contacts) > 0:
        contacts_manager = icloud.ICloudManager().contact_manager
        contacts_manager.create_contacts(icloud_contacts)
    progress_utils.message(f"Created {len(icloud_contacts)} contact(s)")


@progress_utils.annotate("Creating iCloud group")
def write_new_group_to_icloud(icloud_group: icloud.ICloudGroup) -> None:
    contacts_manager = icloud.ICloudManager().contact_manager
    contacts_manager.create_group(icloud_group)
    progress_utils.message(
        f"Created group {icloud_group.name} with {len(icloud_group.contactIds)} contact(s)"
    )


@progress_utils.annotate("Updating iCloud contacts")
def write_updated_contacts_to_icloud(
    icloud_contacts: list[icloud.ICloudContact],
) -> None:
    if len(icloud_contacts) > 0:
        contacts_manager = icloud.ICloudManager().contact_manager
        contacts_manager.update_contacts(icloud_contacts)
    progress_utils.message(f"Updated {len(icloud_contacts)} contact(s)")


@progress_utils.annotate("Updating iCloud group")
def write_updated_group_to_icloud(
    icloud_group: icloud.ICloudGroup,
) -> None:
    contacts_manager = icloud.ICloudManager().contact_manager
    contacts_manager.update_group(icloud_group)
    progress_utils.message(
        f"Updated group {icloud_group.name} with {len(icloud_group.contactIds)} contact(s)"
    )
