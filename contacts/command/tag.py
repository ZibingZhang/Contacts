"""Command to tag contacts."""
from __future__ import annotations

import argparse
import enum
import typing
from collections.abc import Sequence

from contacts.common import error
from contacts.utils import command_utils, contact_utils, input_utils

if typing.TYPE_CHECKING:
    from contacts import model


class TagAction(enum.StrEnum):
    LS = "ls"
    MV = "mv"
    REPL = "repl"


def run(*, tag_action: TagAction, action_specific_args: argparse.Namespace) -> None:
    contacts = command_utils.read_contacts_from_disk()

    match tag_action:
        case TagAction.LS:
            _tag_ls(contacts)
        case TagAction.MV:
            _tag_mv(contacts, action_specific_args.old, action_specific_args.new)
        case TagAction.REPL:
            _tag_repl(contacts)


def _tag_ls(contacts: Sequence[model.Contact]) -> None:
    all_tags = _get_all_tags(contacts)
    all_tags_by_row = [all_tags[i : i + 5] for i in range(0, len(all_tags), 5)]
    for row in all_tags_by_row:
        for tag in row:
            print(tag.ljust(20), end="")
        print("")


def _tag_mv(contacts: Sequence[model.Contact], old: str, new: str) -> None:
    print(f"Changing tag from {old} to {new}.")

    all_tags = _get_all_tags(contacts)
    if new in all_tags:
        if not input_utils.yes_no_input("Tag already exists. Do you wish to continue?"):
            return None

    count = 0
    for contact in contacts:
        if contact.tags is not None and old in contact.tags:
            contact.tags.remove(old)
            contact.tags += [new]
            count += 1

    if input_utils.yes_no_input(f"Update {count} contact(s)?"):
        command_utils.write_contacts_to_disk(contacts)


def _tag_repl(contacts: Sequence[model.Contact]) -> None:
    print("Adding tags to contacts...")
    while True:
        try:
            _add_tags_to_contact(contacts)
        except error.CommandSkipError:
            print("Skipping...")


def _get_all_tags(contacts: Sequence[model.Contact]) -> list[str]:
    return list(
        sorted(set(tag for contact in contacts for tag in (contact.tags or [])))
    )


def _add_tags_to_contact(contacts: Sequence[model.Contact]) -> None:
    contact = command_utils.get_contact_by_name(contacts)
    if contact is None:
        return None

    print(contact_utils.build_name_and_tags_str(contact))
    while True:
        new_tags = [
            tag.strip()
            for tag in input_utils.input_with_skip("Enter the tags to add").split(",")
        ]
        tags = sorted(set((contact.tags or []) + new_tags))

        print(f"tags: {tags}")
        if input_utils.yes_no_input("Continue with this set of tags?"):
            break

    contact.tags = tags
    command_utils.write_contacts_to_disk(contacts)
