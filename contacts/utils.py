import configparser
import os

import constant
from common.utils import file_io_utils
from data import icloud


def icloud_manager_login(config_path: str = None):
    config = configparser.ConfigParser()
    config.read(config_path)
    username = config["login"]["username"]
    password = config["login"]["password"]
    icloud.ICloudManager(username, password).login()


def get_icloud_contacts_and_groups(
    cached: bool, cache_path: str | None = None, config_path: str | None = None
) -> tuple[list[icloud.ICloudContact], list[icloud.ICloudGroup]]:
    if cached:
        if cache_path is None:
            raise ValueError

        contacts = file_io_utils.read_json_array_as_dataclass_objects(
            os.path.join(cache_path, constant.ICLOUD_CONTACTS_FILE_NAME),
            icloud.ICloudContact,
        )
        groups = file_io_utils.read_json_array_as_dataclass_objects(
            os.path.join(cache_path, constant.ICLOUD_GROUPS_FILE_NAME),
            icloud.ICloudGroup,
        )
        return contacts, groups

    if not config_path:
        raise ValueError

    icloud_manager_login(config_path=config_path)

    contact_manager = icloud.ICloudManager().contact_manager
    contacts, groups = contact_manager.get_contacts_and_groups()

    file_io_utils.write_dataclass_objects_as_json_array(
        os.path.join(cache_path, constant.ICLOUD_CONTACTS_FILE_NAME), contacts
    )
    file_io_utils.write_dataclass_objects_as_json_array(
        os.path.join(cache_path, constant.ICLOUD_GROUPS_FILE_NAME), groups
    )

    return contacts, groups
