from __future__ import annotations

import argparse
import enum
import re
import typing

from common import error
from utils import command_utils, contact_utils, input_utils

if typing.TYPE_CHECKING:
    import model


class TagAction(str, enum.Enum):
    LS = "ls"
    MV = "mv"
    REPL = "repl"
    VALIDATE = "validate"


def tag(
    *, data_path: str, tag_action: TagAction, action_specific_args: argparse.Namespace
) -> None:
    contacts = command_utils.read_contacts_from_disk(data_path=data_path)

    match tag_action:
        case TagAction.LS:
            _tag_ls(contacts)
        case TagAction.MV:
            _tag_mv(
                data_path, contacts, action_specific_args.old, action_specific_args.new
            )
        case TagAction.REPL:
            _tag_repl(data_path, contacts)
        case TagAction.VALIDATE:
            _tag_validate(contacts)


def _tag_ls(contacts: list[model.Contact]) -> None:
    tags = sorted(set(tag for contact in contacts for tag in contact.tags or []))
    tags_by_row = [tags[i : i + 5] for i in range(0, len(tags), 5)]
    for row in tags_by_row:
        for tag in row:
            print(tag.ljust(20), end="")
        print("")


def _tag_mv(data_path: str, contacts: list[model.Contact], old: str, new: str) -> None:
    print(f"Changing tag from {old} to {new}.")

    all_tags = set(tag for contact in contacts for tag in (contact.tags or []))
    if new in all_tags:
        if not input_utils.yes_no_input("Tag already exists. Do you wish to continue?"):
            return

    count = 0
    for contact in contacts:
        if old in (contact.tags or []):
            contact.tags.remove(old)
            contact.tags.append(new)
            contact.tags = sorted(set(contact.tags))
            count += 1

    if input_utils.yes_no_input(f"Update {count} contact(s)?"):
        command_utils.write_contacts_to_disk(data_path=data_path, contacts=contacts)


def _tag_repl(data_path: str, contacts: list[model.Contact]) -> None:
    while True:
        try:
            _add_tags_to_contact(data_path, contacts)
        except error.CommandSkipError:
            print("Skipping...")


def _add_tags_to_contact(data_path, contacts: list[model.Contact]):
    name = input_utils.basic_input("Enter the name of the contact to add tags to")

    matching_contacts = _get_matching_contacts(contacts, name)
    if len(matching_contacts) == 0:
        return
    elif len(matching_contacts) == 1:
        selected_contact = matching_contacts[0]
    else:
        for i, contact in enumerate(matching_contacts):
            print(f"{i + 1}. {_build_contact_name_and_tags(contact)}")

        selection = input_utils.input_with_skip("Select the contact to add tags to")
        while True:
            try:
                selection = int(selection)
                if selection < 1:
                    selection = input_utils.input_with_skip(
                        "Too low. Select the contact to add tags to"
                    )
                    continue
                if selection > len(matching_contacts):
                    selection = input_utils.input_with_skip(
                        "Too high. Select the contact to add tags to"
                    )
                    continue
                break
            except ValueError:
                selection = input_utils.input_with_skip(
                    "Not a number. Select the contact to add tags to"
                )

        selected_contact = matching_contacts[selection - 1]

    print(_build_contact_name_and_tags(selected_contact))
    while True:
        new_tags = [
            tag.strip()
            for tag in input_utils.input_with_skip(
                "Enter the tags to add", lower=False
            ).split(",")
        ]
        tags = sorted(set((selected_contact.tags or []) + new_tags))

        print(f"tags: {tags}")
        if input_utils.yes_no_input("Continue with this set of tags?"):
            break

    selected_contact.tags = tags
    command_utils.write_contacts_to_disk(data_path=data_path, contacts=contacts)


def _get_matching_contacts(
    contacts: list[model.Contact], name: str
) -> list[model.Contact]:
    name = " ".join(name.strip().split())
    matching_contacts = []

    if name.count(" ") == 1:
        first_name, last_name = name.split()
        for contact in contacts:
            if (
                first_name in f"{contact.name.first_name}".lower()
                and last_name in f"{contact.name.last_name}".lower()
            ):
                matching_contacts.append(contact)
                continue

    for contact in contacts:
        contact_name = (
            f"{contact.name.first_name} "
            f"{contact.name.middle_name} "
            f"{contact.name.last_name}"
        ).lower()
        if name in contact_name:
            matching_contacts.append(contact)
    return matching_contacts


def _build_contact_name_and_tags(contact: model.Contact) -> str:
    return f"{contact_utils.name_string(contact).ljust(25)} :           {contact.tags}"


def _tag_validate(contacts: list[model.Contact]) -> None:
    for contact in contacts:
        if not contact.tags:
            continue

        if _any_tag_matches_patterns(contact.tags, [re.compile(r"^Climbing-\S+$")]):
            _expect_tag(contact, "Climbing")

        if _any_tag_matches_patterns(contact.tags, [re.compile(r"^CTY\S+$")]):
            _expect_tag(contact, "CTY")

        if _any_tag_matches_patterns(
            contact.tags, [re.compile(r"^(NHS|NPS)\d{2}$"), re.compile(r"^NHS-STAFF$")]
        ):
            _expect_tag(contact, "Needham")

        if _any_tag_matches_patterns(
            contact.tags, [re.compile(r"^NU-\w+\d+$"), re.compile(r"^NU\w{2}$")]
        ):
            _expect_tag(contact, "NU")


def _any_tag_matches_patterns(tags: list[str], patterns: list[re.Pattern]) -> bool:
    return any(pattern.match(tag) for tag in tags for pattern in patterns)


def _expect_tag(contact: model.Contact, tag: str) -> None:
    if tag not in contact.tags:
        print(f"{contact_utils.name_string(contact)} missing {tag} tag")
