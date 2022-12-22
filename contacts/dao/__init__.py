from contacts.dao import icloud, obsidian

__all__ = ["icloud_dao"]

icloud_dao = icloud.ICloudDao()
obsidian_dao = obsidian.ObsidianDao()
