import os
import parser

import command


def _create_dir_if_not_exists(path):
    if not os.path.exists(path=path):
        os.mkdir(path=path)


if __name__ == "__main__":
    cl_args = parser.parse_arguments_with_init()

    match cl_args.command:
        case "pull":
            _create_dir_if_not_exists(cl_args.cache)
            _create_dir_if_not_exists(cl_args.data)
            command.pull(cl_args)
