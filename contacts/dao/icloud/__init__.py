"""The iCloud data source."""
from __future__ import annotations

import configparser
import os

import model
from common import constant, decorator
from dao.icloud import _manager, _model, _transformer
from utils import file_io_utils

__all__ = [
    "read_contacts_and_groups",
    "create_contacts",
    "update_contacts",
    "create_group",
    "update_group",
]


_ALERT_UUIDS = [
    "4B949DAF-F587-47DF-95C2-857B85800ADC",
    "0A4DED51-0751-4B30-AD58-27E8556D5D91",
]
_TEST_CONTACT_UUIDS = [
    "129C6305-F868-4711-B139-C209B4AF3852",
    "50786E4F-651F-4393-8F9C-060C40A22BB5",
    "623AE0B7-EB13-47BB-8CCF-09F2EAE2E4A3",
]
_OTHER_UUIDS = [
    "FAB3DDA6-7529-4D3C-8714-35EF820DCCA8",  # italkbb
]
_IGNORED_UUIDS = _ALERT_UUIDS + _TEST_CONTACT_UUIDS + _OTHER_UUIDS


_contact_manager: _manager.ICloudContactManager | None = None
_updated_sync_token: bool = False


@decorator.run_once
def authenticate(*, config_path: str = constant.DEFAULT_CONFIG_FILE):
    config = configparser.ConfigParser()
    config.read(config_path)
    username = config["login"]["username"]
    password = config["login"]["password"]
    icloud_manager = _manager.ICloudManager(username, password)
    icloud_manager.login()
    global _contact_manager
    _contact_manager = icloud_manager.contact_manager


def read_contacts_and_groups(
    *, cache_path: str = constant.DEFAULT_CACHE_DIRECTORY, cached: bool = False
) -> tuple[list[model.Contact], list[model.Group]]:
    if cached:
        if not os.path.isdir(cache_path):
            raise ValueError(f"Cache path is not a directory, {cache_path}")

        contacts_file_path = os.path.join(
            cache_path, constant.ICLOUD_CONTACTS_FILE_NAME
        )
        if not os.path.isfile(contacts_file_path):
            raise ValueError(f"Contacts file does not exist, {contacts_file_path}")

        groups_file_path = os.path.join(cache_path, constant.ICLOUD_GROUPS_FILE_NAME)
        if not os.path.isfile(contacts_file_path):
            raise ValueError(f"Groups file does not exist, {groups_file_path}")

        icloud_contacts = file_io_utils.read_json_array_as_dataclass_objects(
            contacts_file_path,
            _model.ICloudContact,
        )
        icloud_groups = file_io_utils.read_json_array_as_dataclass_objects(
            groups_file_path,
            _model.ICloudGroup,
        )

    else:
        contact_manager = _get_contact_manager()
        icloud_contacts, icloud_groups = contact_manager.get_contacts_and_groups()

        file_io_utils.write_dataclass_objects_as_json_array(
            os.path.join(cache_path, constant.ICLOUD_CONTACTS_FILE_NAME),
            icloud_contacts,
        )
        file_io_utils.write_dataclass_objects_as_json_array(
            os.path.join(cache_path, constant.ICLOUD_GROUPS_FILE_NAME), icloud_groups
        )

    contacts = [
        _transformer.icloud_contact_to_contact(icloud_contact)
        for icloud_contact in icloud_contacts
        if icloud_contact.contactId not in _IGNORED_UUIDS
    ]
    groups = [
        _transformer.icloud_group_to_group(icloud_group)
        for icloud_group in icloud_groups
    ]

    return contacts, groups


def create_contacts(contacts: list[model.Contact]) -> None:
    contact_manager = _get_contact_manager()
    icloud_contacts = [
        _transformer.contact_to_icloud_contact(contact) for contact in contacts
    ]
    contact_manager.create_contacts(icloud_contacts)


def update_contacts(contacts: list[model.Contact]) -> None:
    contact_manager = _get_contact_manager()
    icloud_contacts = [
        _transformer.contact_to_icloud_contact(contact) for contact in contacts
    ]
    contact_manager.update_contacts(icloud_contacts)


def create_group(group: model.Group) -> None:
    contact_manager = _get_contact_manager()
    contact_manager.create_group(_transformer.group_to_icloud_group(group))


def update_group(group: model.Group) -> None:
    contact_manager = _get_contact_manager()
    contact_manager.update_group(_transformer.group_to_icloud_group(group))


def _get_contact_manager() -> _manager.ICloudContactManager:
    global _contact_manager
    if _contact_manager is None:
        raise RuntimeError("Authentication required")
    return _contact_manager


def _require_updated_sync_token() -> None:
    global _updated_sync_token
    if not _updated_sync_token:
        read_contacts_and_groups()
        _updated_sync_token = True
