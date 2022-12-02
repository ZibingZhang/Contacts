import argparse

import command
from command import tag


def parse_arguments() -> argparse.Namespace:
    return _create_parser().parse_args()


def _create_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    command_parser = parser.add_subparsers(
        dest="command",
        required=True,
        help="commands",
    )

    base_parser = build_base_parser()
    sync_parser = build_sync_parser()

    build_add_command_parser(command_parser, [base_parser])
    build_pull_command_parser(command_parser, [base_parser, sync_parser])
    build_push_command_parser(command_parser, [base_parser, sync_parser])
    build_tag_command_parser(command_parser, [base_parser])
    build_validate_command_parser(command_parser, [base_parser])

    return parser


def build_base_parser() -> argparse.ArgumentParser:
    base_parser = argparse.ArgumentParser(add_help=False)
    base_parser.add_argument(
        "--data", default="data", help="path to contacts data directory"
    )
    return base_parser


def build_sync_parser() -> argparse.ArgumentParser:
    sync_parser = argparse.ArgumentParser(add_help=False)
    sync_parser.add_argument("--cache", default="cache", help="path to cache directory")
    sync_parser.add_argument(
        "--config", default="config.ini", help="path to configuration file"
    )
    sync_parser.add_argument(
        "--force",
        action="store_true",
        default=False,
        help="perform the action user validation",
    )
    sync_parser.add_argument(
        "--source", default="icloud", help="source to pull contacts from"
    )
    return sync_parser


def build_add_command_parser(
    command_parser: argparse._SubParsersAction, parents: list[argparse.ArgumentParser]
) -> argparse.ArgumentParser:
    add_command_parser = command_parser.add_parser(
        command.Command.ADD,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        parents=parents,
        help="add a contact",
    )
    return add_command_parser


def build_pull_command_parser(
    command_parser: argparse._SubParsersAction, parents: list[argparse.ArgumentParser]
) -> argparse.ArgumentParser:
    pull_parser = command_parser.add_parser(
        command.Command.PULL,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        parents=parents,
        help="pull contacts from remote source",
    )
    pull_parser.add_argument(
        "--cached", action="store_true", default=False, help="pull contacts from cache"
    )
    return pull_parser


def build_push_command_parser(
    command_parser: argparse._SubParsersAction, parents: list[argparse.ArgumentParser]
) -> argparse.ArgumentParser:
    push_parser = command_parser.add_parser(
        command.Command.PUSH,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        parents=parents,
        help="push contacts to remote source",
    )
    push_parser.add_argument(
        "--write",
        action="store_true",
        default=False,
        help="write the contact creations / updates",
    )
    return push_parser


def build_tag_command_parser(
    command_parser: argparse._SubParsersAction, parents: list[argparse.ArgumentParser]
) -> argparse.ArgumentParser:
    tag_parser = command_parser.add_parser(
        command.Command.TAG,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        parents=parents,
        help="tag contacts",
    )

    tag_action_parser = tag_parser.add_subparsers(dest="tag_action", help="tag actions")

    tag_action_parser.add_parser(tag.TagAction.LS.value, help="list all tags")
    mv_tag_action_parser = tag_action_parser.add_parser(
        tag.TagAction.MV.value, help="rename a tag"
    )
    tag_action_parser.add_parser(
        tag.TagAction.REPL.value, help="repl to add tags to contacts"
    )

    mv_tag_action_parser.add_argument(
        "old",
    )
    mv_tag_action_parser.add_argument(
        "new",
    )

    return tag_parser


def build_validate_command_parser(
    command_parser: argparse._SubParsersAction, parents: list[argparse.ArgumentParser]
) -> argparse.ArgumentParser:
    validate_parser = command_parser.add_parser(
        command.Command.VALIDATE,
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        parents=parents,
        help="validate contacts",
    )
    return validate_parser
