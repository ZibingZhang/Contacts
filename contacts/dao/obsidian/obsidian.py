import configparser
import os

from contacts.common import constant


class ObsidianDao:
    def __init__(self, *, config_path: str = constant.DEFAULT_CONFIG_FILE):
        config = configparser.ConfigParser()
        config.read(config_path)
        root = config["obsidian"]["root"]

        os.listdir(root)
