from __future__ import annotations

import os.path
import parser
import typing

import command
from common import constant, error
from dao import icloud

if typing.TYPE_CHECKING:
    import argparse


def _run_command(cl_args: argparse.Namespace) -> None:
    match cl_args.command:
        case command.Command.ADD:
            command.add.run()

        case command.Command.PULL:
            _create_if_dir_not_exists(constant.DEFAULT_CACHE_DIRECTORY)
            _create_if_dir_not_exists(constant.DEFAULT_DATA_DIRECTORY)
            if not cl_args.cached:
                icloud.authenticate()
            command.pull.run(cached=cl_args.cached)

        case command.Command.PUSH:
            _create_if_dir_not_exists(constant.DEFAULT_CACHE_DIRECTORY)
            _error_if_dir_not_exists(constant.DEFAULT_DATA_DIRECTORY)
            icloud.authenticate()
            command.push.run(force=cl_args.force, write=cl_args.write)

        case command.Command.SYNC_GROUPS:
            icloud.authenticate()
            command.sync_groups.run()

        case command.Command.TAG:
            _error_if_dir_not_exists(constant.DEFAULT_DATA_DIRECTORY)
            command.tag.run(tag_action=cl_args.tag_action, action_specific_args=cl_args)

        case command.Command.VALIDATE:
            command.validate.run()


def _create_if_dir_not_exists(path):
    if not os.path.exists(path):
        os.mkdir(path)


def _error_if_dir_not_exists(path):
    if not os.path.exists(path):
        raise ValueError(f"Directory {path} does not exist.")
    if not os.path.isdir(path):
        raise ValueError(f"{path} is not a directory.")


if __name__ == "__main__":
    cl_args = parser.parse_arguments()

    try:
        _run_command(cl_args)
    except error.CommandQuitError:
        print("Exiting")

    print("Done")
