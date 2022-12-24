"""Command to validate contacts."""
from __future__ import annotations

import collections
import re

from contacts import model
from contacts.utils import command_utils, contact_utils

PATTERN_TO_HIGH_SCHOOL_NAME_MAP = {
    re.compile(r"^ABRSH$"): model.HighSchoolName.ACTON_BOXBOROUGH_REGIONAL_HIGH_SCHOOL,
    re.compile(r"^LHS$"): model.HighSchoolName.LEXINGTON_HIGH_SCHOOL,
    re.compile(r"^NHS\d{2}$"): model.HighSchoolName.NEEDHAM_HIGH_SCHOOL,
}


def run() -> None:
    contacts = command_utils.read_contacts_from_disk()
    _validate_names(contacts)
    for contact in contacts:
        _validate_email_addresses(contact)
        _validate_education(contact)
        _validate_tags(contact)


def _validate_names(contacts: list[model.Contact]) -> None:
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
        normalized_email_addresses.add(
            (email_address.local_part + email_address.domain).lower().replace(".", "")
        )
    if len(normalized_email_addresses) < len(contact.email_addresses):
        print(f"{contact_utils.build_name_str(contact)} has duplicate email addresses")


def _validate_education(contact: model.Contact) -> None:
    if not contact.tags:
        return None

    for pattern in PATTERN_TO_HIGH_SCHOOL_NAME_MAP.keys():
        if _any_tag_matches_pattern(contact.tags, pattern):
            _expect_high_school(contact, PATTERN_TO_HIGH_SCHOOL_NAME_MAP[pattern])


def _expect_high_school(contact: model.Contact, high_school_name: str) -> None:
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
        print(f"{contact_name} missing graduation year")


def _validate_tags(contact: model.Contact) -> None:
    if not contact.tags:
        return None

    if _any_tag_matches_pattern(contact.tags, re.compile(r"^Climbing-.+$")):
        _expect_tag(contact, "Climbing")

    if _any_tag_matches_pattern(contact.tags, re.compile(r"^CTY.+$")):
        _expect_tag(contact, "CTY")

    if _any_tag_matches_pattern(contact.tags, re.compile(r"^HubSpot.+$")):
        _expect_tag(contact, "HubSpot")

    if _any_tag_matches_pattern(contact.tags, re.compile(r"^(NHS|NPS).+$")):
        _expect_tag(contact, "Needham")

    if _any_tag_matches_pattern(contact.tags, re.compile(r"^NU.+$")):
        _expect_tag(contact, "NU")

    if _any_tag_matches_pattern(contact.tags, re.compile(r"^PowerAdvocate.+$")):
        _expect_tag(contact, "PowerAdvocate")

    if _any_tag_matches_pattern(contact.tags, re.compile(r"^Sharks.+$")):
        _expect_tag(contact, "Sharks")


def _expect_tag(contact: model.Contact, tag: str) -> None:
    if contact.tags is None or tag not in contact.tags:
        print(f"{contact_utils.build_name_str(contact)} missing {tag} tag")


def _any_tag_matches_pattern(tags: list[str], pattern: re.Pattern) -> bool:
    return any(pattern.match(tag) for tag in tags)
