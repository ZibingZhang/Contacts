import argparse
import os


def parse_arguments_with_init() -> argparse.Namespace:
    args = _parser.parse_args()
    _create_dir_if_not_exists(args.cache)
    _create_dir_if_not_exists(args.data)
    return args


_parser = argparse.ArgumentParser()
_parser.add_argument("--cache", default="cache", help="path to cache directory")
_parser.add_argument(
    "--config", default="config.ini", help="path to configuration file"
)
_parser.add_argument("--data", default="data", help="path to contacts data")


def _create_dir_if_not_exists(path):
    if not os.path.exists(path=path):
        os.mkdir(path=path)
