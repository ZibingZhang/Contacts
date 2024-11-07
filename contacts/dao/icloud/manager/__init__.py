"""iCloud managers."""
from contacts.dao.icloud.manager import contact_manager, icloud_manager, icloud_session

__all__ = ["ICloudContactManager", "ICloudManager", "ICloudSession"]

ICloudContactManager = contact_manager.ICloudContactManager
ICloudManager = icloud_manager.ICloudManager
ICloudSession = icloud_session.ICloudSession
