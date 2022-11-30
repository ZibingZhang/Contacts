import argparse


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

    base_parser = argparse.ArgumentParser(add_help=False)
    base_parser.add_argument("--cache", default="cache", help="path to cache directory")
    base_parser.add_argument(
        "--config", default="config.ini", help="path to configuration file"
    )
    base_parser.add_argument(
        "--data", default="data", help="path to contacts data directory"
    )
    base_parser.add_argument(
        "--force", default=False, help="perform the action user validation"
    )

    sync_parser = argparse.ArgumentParser(add_help=False)
    sync_parser.add_argument(
        "--source", default="icloud", help="source to pull contacts from"
    )

    pull_parser = command_parser.add_parser(
        "add",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        parents=[base_parser, sync_parser],
        help="add a contact",
    )

    pull_parser = command_parser.add_parser(
        "pull",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        parents=[base_parser, sync_parser],
        help="pull contacts from remote source",
    )
    pull_parser.add_argument(
        "--cached", action="store_true", default=False, help="pull contacts from cache"
    )

    push_parser = command_parser.add_parser(
        "push",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        parents=[base_parser],
        help="push contacts to remote source",
    )
    push_parser.add_argument(
        "--write",
        action="store_true",
        default=False,
        help="write the contact creations / updates",
    )

    return parser
