"""Constants."""
from __future__ import annotations

from contacts import model

DEFAULT_CACHE_DIRECTORY = "cache"
DEFAULT_DATA_DIRECTORY = "data"
DEFAULT_CONFIG_FILE = "config.ini"

CONTACTS_FILE_NAME = "contacts.json"
NEW_CONTACT_FILE_NAME = "new-contacts.json"

ICLOUD_CONTACTS_FILE_NAME = "icloud-contacts.json"
ICLOUD_GROUPS_FILE_NAME = "icloud-groups.json"

COUNTRY_TO_COUNTRY_CODE_MAP = {model.Country.UNITED_STATES: "us"}
