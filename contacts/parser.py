import argparse


def parse_arguments_with_init() -> argparse.Namespace:
    cl_args = _create_parser().parse_args()
    return cl_args


def _create_parser():
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    command_parser = parser.add_subparsers(
        dest="command",
        required=True,
        help="commands",
    )

    pull_parser = command_parser.add_parser(
        "pull",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        help="pull contacts from remote source",
    )

    pull_parser.add_argument("--cache", default="cache", help="path to cache directory")
    pull_parser.add_argument(
        "--config", default="config.ini", help="path to configuration file"
    )
    pull_parser.add_argument(
        "--data", default="data", help="path to contacts data directory"
    )
    pull_parser.add_argument(
        "--source", default="icloud", help="source to pull contacts from"
    )

    return parser
