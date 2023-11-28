"""Command to validate contacts."""
from __future__ import annotations

import collections
import re
from collections.abc import Sequence

from contacts import model
from contacts.utils import command_utils, contact_utils

_PATTERN_TO_HIGH_SCHOOL_NAME_MAP = {
    re.compile(r"^ABRSH$"): model.HighSchoolName.ACTON_BOXBOROUGH_REGIONAL_HIGH_SCHOOL,
    re.compile(r"^LHS$"): model.HighSchoolName.LEXINGTON_HIGH_SCHOOL,
    re.compile(r"^NHS\d{2}$"): model.HighSchoolName.NEEDHAM_HIGH_SCHOOL,
}

_PATTERN_TO_EXPECTED_TAG_MAP = {
    re.compile(r"^Climbing-.+$"): "Climbing",
    re.compile(r"^CTY.+$"): "CTY",
    re.compile(r"^HubSpot.+$"): "HubSpot",
    re.compile(r"^NHS.*$"): "NHS",
    re.compile(r"^NHS\d{2}$"): "NPS",
    re.compile(r"^(NHS|NPS).+$"): "Needham",
    re.compile(r"^NU.+$"): "NU",
    re.compile(r"^PowerAdvocate.+$"): "PowerAdvocate",
    re.compile(r"^SAB$"): "Boston",
    re.compile(r"^Sharks.+$"): "Sharks",
}


def run() -> None:
    contacts = command_utils.read_contacts_from_disk()
    _validate_names(contacts)
    for contact in contacts:
        _validate_email_addresses(contact)
        _validate_education(contact)
        _validate_tags(contact)


def _validate_names(contacts: Sequence[model.Contact]) -> None:
    names_counter: collections.Counter[str] = collections.Counter()
    for contact in contacts:
        names_counter[contact_utils.build_name_str(contact)] += 1
    for name in sorted(names_counter.keys()):
        if names_counter[name] > 1:
            print(f"Duplicate name {name}")


def _validate_email_addresses(contact: model.Contact) -> None:
    if contact.email_addresses is None:
        return None

    normalized_email_addresses = set()
    for email_address in contact.email_addresses:
        normalized_email_addresses.add(email_address.address.lower().replace(".", ""))
    if len(normalized_email_addresses) < len(contact.email_addresses):
        print(f"{contact_utils.build_name_str(contact)} has duplicate email addresses")


def _validate_education(contact: model.Contact) -> None:
    if not contact.tags:
        return None

    for pattern in _PATTERN_TO_HIGH_SCHOOL_NAME_MAP:
        if tag := _any_tag_matches_pattern(contact.tags, pattern):
            _expect_high_school(contact, tag, _PATTERN_TO_HIGH_SCHOOL_NAME_MAP[pattern])


def _expect_high_school(
    contact: model.Contact, tag: str, high_school_name: str
) -> None:
    contact_name = contact_utils.build_name_str(contact)
    if contact.education is None:
        print(f"{contact_name} missing education")
        return None
    if contact.education.high_school is None:
        print(f"{contact_name} missing high school")
        return None
    if contact.education.high_school.name == high_school_name is None:
        print(f"{contact_name} high school is not {high_school_name}")
    if (
        contact.education.high_school.name == model.HighSchoolName.NEEDHAM_HIGH_SCHOOL
        and contact.education.high_school.graduation_year is None
    ):
        graduation_year = 2000 + int(tag[-2:])
        if contact.education.high_school.graduation_year is None:
            print(f"{contact_name} missing high school graduation year")
        elif graduation_year != contact.education.high_school.graduation_year:
            print(f"{contact_name} mismatched high school graduation year")


def _validate_tags(contact: model.Contact) -> None:
    if not contact.tags:
        return None

    for pattern in _PATTERN_TO_EXPECTED_TAG_MAP:
        if _any_tag_matches_pattern(contact.tags, pattern):
            _expect_tag(contact, _PATTERN_TO_EXPECTED_TAG_MAP[pattern])


def _expect_tag(contact: model.Contact, tag: str) -> None:
    if contact.tags is None or tag not in contact.tags:
        print(f"{contact_utils.build_name_str(contact)} missing {tag} tag")


def _any_tag_matches_pattern(tags: list[str], pattern: re.Pattern) -> str | False:
    for tag in tags:
        if pattern.match(tag):
            return tag
    return False
