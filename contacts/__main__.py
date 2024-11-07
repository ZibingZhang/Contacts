from __future__ import annotations

import argparse

from contacts import command, parser
from contacts.common import error
from contacts.dao import icloud_dao


def _run_command(cl_args: argparse.Namespace) -> None:
    import logging
    import sys
    logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

    match cl_args.command:
        case command.Command.ADD:
            command.add.run()

        case command.Command.DUMP:
            command.dump.run()

        case command.Command.FAMILIES:
            command.families.run()

        case command.Command.LOAD:
            command.load.run(name=cl_args.name)

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
            match cl_args.tag_action:
                case command.TagSubcommand.LS:
                    command.tag_ls.run(tags=cl_args.tags)
                case command.TagSubcommand.MV:
                    command.tag_mv.run(old=cl_args.old, new=cl_args.new)
                case command.TagSubcommand.REPL:
                    command.tag_repl.run()
                case _:
                    raise RuntimeError("Missing subcommand")

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
