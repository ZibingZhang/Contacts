import configparser
import os

from contacts.common import constant


class ObsidianDao:
    def __init__(self, *, config_path: str = constant.CONFIG_FILE):
        config = configparser.ConfigParser()
        config.read(config_path)
        root = config["obsidian"]["root"]

        os.listdir(os.path.expanduser(root))
