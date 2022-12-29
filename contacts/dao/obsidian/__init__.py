from __future__ import annotations

import configparser
import os.path
import string
from collections.abc import Sequence

from contacts import model
from contacts.common import constant

_SEPERATOR = "-----------------"
_TEMPLATE = string.Template(
    f"""---
tags:
- contact

obsidian:
    display_name: "$display_name"
    phone_numbers: "$phone_numbers"
    tags: "$tags"
---

# $display_name

{_SEPERATOR}"""
)


class ObsidianDao:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read(constant.CONFIG_FILE)
        root = config["obsidian"]["root"]
        self._contacts_dir = os.path.expanduser(
            os.path.join(root, "data", "contacts", "objects")
        )

    def upsert_contacts(self, contacts: Sequence[model.Contact]) -> None:
        for contact in contacts:
            if contact.id is None:
                continue

            path = os.path.join(self._contacts_dir, f"{contact.id}.md")

            if not os.path.exists(path):
                self._write_contact(path, contact)
                continue

            mtime = os.path.getmtime(path)
            if contact.mtime is None or contact.mtime > mtime:
                self._write_contact(path, contact)

    def _write_contact(self, path: str, contact: model.Contact) -> None:
        header = _TEMPLATE.substitute(
            display_name=self._build_display_name(contact.name),
            phone_numbers=self._build_phone_numbers(contact.phone_numbers),
            tags=self._build_tags(contact.tags),
        )

        if not os.path.exists(path):
            with open(path, "w") as f:
                f.write(header)
                return None

        with open(path, "r+") as f:
            contact_file = f.read()
            _, body = contact_file.split(_SEPERATOR)
            f.seek(0)
            f.truncate()
            f.write(header + body)

    @staticmethod
    def _build_display_name(name: model.Name) -> str:
        name_parts = []
        if first_name := name.first_name:
            name_parts.append(first_name)
        if nickname := name.nickname:
            name_parts.append(f"({nickname})")
        if last_name := name.last_name:
            name_parts.append(last_name)
        return " ".join(name_parts)

    @staticmethod
    def _build_phone_numbers(phone_numbers: list[model.PhoneNumber] | None) -> str:
        if phone_numbers is None:
            return ""
        return ", ".join(
            f"+{phone_number.country_code}{phone_number.number}"
            for phone_number in phone_numbers
        )

    @staticmethod
    def _build_tags(tags: list[str] | None) -> str:
        return "" if tags is None else ", ".join(tags)
