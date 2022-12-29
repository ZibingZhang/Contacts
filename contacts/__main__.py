from __future__ import annotations

import typing

from contacts import command, parser
from contacts.common import error
from contacts.dao import icloud_dao

if typing.TYPE_CHECKING:
    import argparse


def _run_command(cl_args: argparse.Namespace) -> None:
    match cl_args.command:
        case command.Command.ADD:
            command.add.run()

        case command.Command.DUMP:
            command.dump.run()

        case command.Command.LOAD:
            command.load.run()

        case command.Command.PULL:
            if not cl_args.cached:
                icloud_dao.authenticate()
            command.pull.run(cached=cl_args.cached)

        case command.Command.PUSH:
            icloud_dao.authenticate()
            command.push.run(force=cl_args.force, write=cl_args.write)

        case command.Command.SYNC_GROUPS:
            icloud_dao.authenticate()
            command.sync_groups.run()

        case command.Command.TAG:
            command.tag.run(tag_action=cl_args.tag_action, action_specific_args=cl_args)

        case command.Command.VALIDATE:
            command.validate.run()

        case _:
            raise NotImplementedError("Unimplemented command")


if __name__ == "__main__":
    cl_args = parser.parse_arguments()

    try:
        _run_command(cl_args)
    except error.CommandQuitError:
        print("Exiting")

    print("Done")
