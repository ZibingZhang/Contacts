"""iCloud request and response models."""
from contacts.dao.icloud.model import icloud_contact, icloud_group

ICloudContact = icloud_contact.ICloudContact
ICloudGroup = icloud_group.ICloudGroup

Date = icloud_contact.Date
EmailAddress = icloud_contact.EmailAddress
IMField = icloud_contact.IMField
IM = icloud_contact.IM
Phone = icloud_contact.Phone
Profile = icloud_contact.Profile
RelatedName = icloud_contact.RelatedName
StreetAddressField = icloud_contact.StreetAddressField
StreetAddress = icloud_contact.StreetAddress
Url = icloud_contact.Url
