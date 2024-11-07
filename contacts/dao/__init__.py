from contacts.dao.icloud.icloud_dao import ICloudDao
from contacts.dao.local.local_dao import LocalDao

__all__ = ["icloud_dao", "local_dao"]

icloud_dao = ICloudDao()
local_dao = LocalDao()
