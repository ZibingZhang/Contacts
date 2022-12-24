"""Transformers between models and iCloud models."""
from contacts.dao.icloud.transformer import (
    contact_to_icloud_contact as _contact_to_icloud_contact,
)
from contacts.dao.icloud.transformer import (
    group_to_icloud_group as _group_to_icloud_group,
)
from contacts.dao.icloud.transformer import (
    icloud_contact_to_contact as _icloud_contact_to_contact,
)
from contacts.dao.icloud.transformer import (
    icloud_group_to_group as _icloud_group_to_group,
)

contact_to_icloud_contact = _contact_to_icloud_contact.contact_to_icloud_contact
group_to_icloud_group = _group_to_icloud_group.group_to_icloud_group
icloud_contact_to_contact = _icloud_contact_to_contact.icloud_contact_to_contact
icloud_group_to_group = _icloud_group_to_group.icloud_group_to_group
