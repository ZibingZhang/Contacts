"""Transformers between models and iCloud models."""
from contacts.dao.icloud.transformer import (
    contact_to_icloud_contact,
    group_to_icloud_group,
    icloud_contact_to_contact,
    icloud_group_to_group,
)

contact_to_icloud_contact = contact_to_icloud_contact.contact_to_icloud_contact
group_to_icloud_group = group_to_icloud_group.group_to_icloud_group
icloud_contact_to_contact = icloud_contact_to_contact.icloud_contact_to_contact
icloud_group_to_group = icloud_group_to_group.icloud_group_to_group
