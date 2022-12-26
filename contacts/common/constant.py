"""Constants."""
from __future__ import annotations

from contacts import model

CACHE_DIRECTORY = "cache"
DATA_DIRECTORY = "data"
CONFIG_FILE = "config.ini"

CONTACTS_FILE_NAME = "contacts.json"
NEW_CONTACT_FILE_NAME = "new-contacts.json"

ICLOUD_CONTACTS_FILE_NAME = "icloud-contacts.json"
ICLOUD_GROUPS_FILE_NAME = "icloud-groups.json"

COUNTRY_TO_COUNTRY_CODE_MAP = {model.Country.UNITED_STATES.value: "us"}
