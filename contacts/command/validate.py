import re

import model
from utils import command_utils, contact_utils


PATTERN_TO_HIGH_SCHOOL_NAME_MAP = {
    re.compile(r"^ABRSH$"): model.HighSchoolName.ACTON_BOXBOROUGH_REGIONAL_HIGH_SCHOOL,
    re.compile(r"^LHS$"): model.HighSchoolName.LEXINGTON_HIGH_SCHOOL,
    re.compile(r"^NHS\d{2}$"): model.HighSchoolName.NEEDHAM_HIGH_SCHOOL,
}


def run(*, data_path: str) -> None:
    contacts = command_utils.read_contacts_from_disk(data_path=data_path)
    for contact in contacts:
        _validate_tags(contact)
        _validate_education(contact)


def _validate_tags(contact: model.Contact) -> None:
    if not contact.tags:
        return

    if _any_tag_matches_pattern(contact.tags, re.compile(r"^Climbing-.+$")):
        _expect_tag(contact, "Climbing")

    if _any_tag_matches_pattern(contact.tags, re.compile(r"^CTY.+$")):
        _expect_tag(contact, "CTY")

    if _any_tag_matches_pattern(contact.tags, re.compile(r"^(NHS|NPS).+$")):
        _expect_tag(contact, "Needham")

    if _any_tag_matches_pattern(contact.tags, re.compile(r"^NU.+$")):
        _expect_tag(contact, "NU")


def _expect_tag(contact: model.Contact, tag: str) -> None:
    if tag not in contact.tags:
        print(f"{contact_utils.name_string(contact)} missing {tag} tag")


def _validate_education(contact: model.Contact) -> None:
    if not contact.tags:
        return

    for pattern in PATTERN_TO_HIGH_SCHOOL_NAME_MAP.keys():
        if _any_tag_matches_pattern(contact.tags, pattern):
            _expect_high_school(contact, PATTERN_TO_HIGH_SCHOOL_NAME_MAP.get(pattern))

    for pattern in PATTERN_TO_HIGH_SCHOOL_NAME_MAP.keys():
        if _any_tag_matches_pattern(contact.tags, pattern):
            _expect_high_school(contact, PATTERN_TO_HIGH_SCHOOL_NAME_MAP.get(pattern))


def _expect_high_school(contact: model.Contact, high_school_name: str) -> None:
    contact_name = contact_utils.name_string(contact)
    if not contact.education:
        print(f"{contact_name} missing education")
        return
    if not contact.education.high_school:
        print(f"{contact_name} missing high school")
        return
    if not contact.education.high_school.name == high_school_name:
        print(f"{contact_name} high school is not {high_school_name}")
    if not contact.education.high_school.graduation_year:
        print(f"{contact_name} missing graduation year")


def _any_tag_matches_pattern(tags: list[str], pattern: re.Pattern) -> bool:
    return any(pattern.match(tag) for tag in tags)
