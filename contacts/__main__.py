from __future__ import annotations

import os
import parser
import typing

import command
from common import error
from dao import icloud

if typing.TYPE_CHECKING:
    import argparse


def _run_command(cl_args: argparse.Namespace) -> None:
    match cl_args.command:
        case command.Command.ADD:
            command.add.run(data_path=cl_args.data)

        case command.Command.PULL:
            _create_dir_if_not_exists(cl_args.cache)
            _create_dir_if_not_exists(cl_args.data)
            if not cl_args.cached:
                icloud.authenticate(config_path=cl_args.config)
            command.pull.run(
                cache_path=cl_args.cache, cached=cl_args.cached, data_path=cl_args.data
            )

        case command.Command.PUSH:
            _create_dir_if_not_exists(cl_args.cache)
            _error_if_not_exists(cl_args.data)
            icloud.authenticate(config_path=cl_args.config)
            command.push.run(
                cache_path=cl_args.cache,
                data_path=cl_args.data,
                force=cl_args.force,
                write=cl_args.write,
            )

        case command.Command.SYNC_GROUPS:
            icloud.authenticate(config_path=cl_args.config)
            command.sync_groups.run(cache_path=cl_args.cache, data_path=cl_args.data)

        case command.Command.TAG:
            _error_if_not_exists(cl_args.data)
            command.tag.run(
                data_path=cl_args.data,
                tag_action=cl_args.tag_action,
                action_specific_args=cl_args,
            )

        case command.Command.VALIDATE:
            command.validate.run(data_path=cl_args.data)


def _create_dir_if_not_exists(path):
    if not os.path.exists(path):
        os.mkdir(path)


def _error_if_not_exists(path):
    if not os.path.exists(path):
        raise ValueError(f"{path} does not exist.")


if __name__ == "__main__":
    cl_args = parser.parse_arguments()

    try:
        _run_command(cl_args)
    except error.CommandQuitError:
        print("Exiting")

    print("Done")
