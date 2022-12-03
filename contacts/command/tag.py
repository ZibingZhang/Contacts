from __future__ import annotations

import argparse
import enum
import typing

from common import error
from utils import command_utils, contact_utils, input_utils

if typing.TYPE_CHECKING:
    import model


class TagAction(str, enum.Enum):
    LS = "ls"
    MV = "mv"
    REPL = "repl"


def run(
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


def _tag_ls(contacts: list[model.Contact]) -> None:
    all_tags = _get_all_tags(contacts)
    all_tags_by_row = [all_tags[i : i + 5] for i in range(0, len(all_tags), 5)]
    for row in all_tags_by_row:
        for tag in row:
            print(tag.ljust(20), end="")
        print("")


def _tag_mv(data_path: str, contacts: list[model.Contact], old: str, new: str) -> None:
    print(f"Changing tag from {old} to {new}.")

    all_tags = _get_all_tags(contacts)
    if new in all_tags:
        if not input_utils.yes_no_input("Tag already exists. Do you wish to continue?"):
            return

    count = 0
    for contact in contacts:
        if old in (contact.tags or []):
            contact.tags.remove(old)
            contact.tags.append(new)
            contact.tags.sort()
            count += 1

    if input_utils.yes_no_input(f"Update {count} contact(s)?"):
        command_utils.write_contacts_to_disk(data_path=data_path, contacts=contacts)


def _tag_repl(data_path: str, contacts: list[model.Contact]) -> None:
    while True:
        try:
            _add_tags_to_contact(data_path, contacts)
        except error.CommandSkipError:
            print("Skipping...")


def _get_all_tags(contacts: list[model.Contact]) -> list[str]:
    return list(
        sorted(set(tag for contact in contacts for tag in (contact.tags or [])))
    )


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
    return f"{contact_utils.extract_name(contact).ljust(25)} :           {contact.tags}"
