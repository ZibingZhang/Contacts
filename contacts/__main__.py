import os
import parser

import command
from utils import icloud_utils


def _create_dir_if_not_exists(path):
    if not os.path.exists(path=path):
        os.mkdir(path=path)


if __name__ == "__main__":
    cl_args = parser.parse_arguments()

    match cl_args.command:
        case "add":
            command.add(data_path=cl_args.data)
        case "pull":
            _create_dir_if_not_exists(cl_args.cache)
            _create_dir_if_not_exists(cl_args.data)
            if not cl_args.cached:
                icloud_utils.login(config_path=cl_args.config)
            command.pull(
                cache_path=cl_args.cache,
                cached=cl_args.cached,
                data_path=cl_args.data,
            )
        case "push":
            _create_dir_if_not_exists(cl_args.cache)
            _create_dir_if_not_exists(cl_args.data)
            icloud_utils.login(config_path=cl_args.config)
            command.push(
                cache_path=cl_args.cache,
                data_path=cl_args.data,
                write=cl_args.write,
            )

    print("Done")
