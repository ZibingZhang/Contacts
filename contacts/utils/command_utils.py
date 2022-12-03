"""High-level utilities for commands."""
import os

import model
from common import constant
from utils import file_io_utils, icloud_utils, progress_utils

from data import icloud


@progress_utils.annotate("Reading contact from disk")
def read_contact_from_disk(*, data_path: str, file_name: str) -> model.Contact:
    contact = file_io_utils.read_json_object_as_dataclass_object(
        os.path.join(data_path, file_name), model.Contact
    )
    return contact


@progress_utils.annotate("Reading contacts from disk")
def read_contacts_from_disk(
    *, data_path: str = "data", file_name: str = constant.CONTACTS_FILE_NAME
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


@progress_utils.annotate("Writing contacts to disk")
def write_contacts_to_disk(
    contacts: list[model.Contact],
    *,
    data_path: str = "data",
    file_name: str = constant.CONTACTS_FILE_NAME,
) -> None:
    file_io_utils.write_dataclass_objects_as_json_array(
        os.path.join(data_path, file_name),
        contacts,
    )
    progress_utils.message(f"Wrote {len(contacts)} contact(s)")


@progress_utils.annotate("Writing new contacts to iCloud")
def write_new_contacts_to_icloud(icloud_contacts: list[icloud.ICloudContact]) -> None:
    if len(icloud_contacts) > 0:
        contacts_manager = icloud.ICloudManager().contact_manager
        contacts_manager.create_contacts(icloud_contacts)
    progress_utils.message(f"Wrote {len(icloud_contacts)} new contact(s)")


@progress_utils.annotate("Writing updated contacts to iCloud")
def write_updated_contacts_to_icloud(
    icloud_contacts: list[icloud.ICloudContact],
) -> None:
    if len(icloud_contacts) > 0:
        contacts_manager = icloud.ICloudManager().contact_manager
        contacts_manager.update_contacts(icloud_contacts)
    progress_utils.message(f"Wrote {len(icloud_contacts)} updated contact(s)")
