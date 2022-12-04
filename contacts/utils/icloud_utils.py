"""Utilities for iCloud."""
import configparser
import os

from common import constant, decorator
from utils import file_io_utils

from data import icloud


@decorator.run_once
def login(*, config_path: str = constant.DEFAULT_CONFIG_FILE):
    config = configparser.ConfigParser()
    config.read(config_path)
    username = config["login"]["username"]
    password = config["login"]["password"]
    icloud.ICloudManager(username, password).login()


def get_contacts_and_groups(
    *, cache_path: str = constant.DEFAULT_CACHE_DIRECTORY, cached: bool = False
) -> tuple[list[icloud.ICloudContact], list[icloud.ICloudGroup]]:
    if cached:
        if cache_path is None:
            raise ValueError("Cache path not set")

        contacts = file_io_utils.read_json_array_as_dataclass_objects(
            os.path.join(cache_path, constant.ICLOUD_CONTACTS_FILE_NAME),
            icloud.ICloudContact,
        )
        groups = file_io_utils.read_json_array_as_dataclass_objects(
            os.path.join(cache_path, constant.ICLOUD_GROUPS_FILE_NAME),
            icloud.ICloudGroup,
        )
        return contacts, groups

    contact_manager = icloud.ICloudManager().contact_manager
    contacts, groups = contact_manager.get_contacts_and_groups()

    file_io_utils.write_dataclass_objects_as_json_array(
        os.path.join(cache_path, constant.ICLOUD_CONTACTS_FILE_NAME), contacts
    )
    file_io_utils.write_dataclass_objects_as_json_array(
        os.path.join(cache_path, constant.ICLOUD_GROUPS_FILE_NAME), groups
    )

    return contacts, groups
