"""iCloud managers."""
from contacts.dao.icloud.manager import contact_manager, icloud_session

__all__ = ["ICloudContactManager", "ICloudSession"]

ICloudContactManager = contact_manager.ICloudContactManager
ICloudSession = icloud_session.ICloudSession
