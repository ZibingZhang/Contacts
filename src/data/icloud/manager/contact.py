"""iCloud contacts api wrapper."""
import json
import re
import typing
import uuid

if typing.TYPE_CHECKING:
    from data.icloud.manager.session import ICloudSession


class ContactManager:
    """
    The 'Contacts' iCloud manager, connects to iCloud and returns contacts.
    """

    def __init__(
        self, service_root: str, session: 'ICloudSession', params: dict[str, str]
    ) -> None:
        self.session = session
        self.params = params
        self._service_root = service_root
        self._contacts_endpoint = "%s/co" % self._service_root
        self._contacts_refresh_url = "%s/startup" % self._contacts_endpoint
        self._contacts_next_url = "%s/contacts" % self._contacts_endpoint
        self._contacts_changeset_url = "%s/changeset" % self._contacts_endpoint
        self._contacts_update_url = "%s/card" % self._contacts_next_url
        self._groups_endpoint = "%s/groups" % self._contacts_endpoint
        self._groups_update_url = "%s/card" % self._groups_endpoint

        self.pref_token = ""
        self.sync_token_prefix = ""
        self.sync_token_number = -1
        self.params.update(
            {
                "clientVersion": "2.1",
                "locale": "en_US",
                "order": "last,first",
            }
        )

    @property
    def sync_token(self) -> str:
        return f"{self.sync_token_prefix}{self.sync_token_number}"

    def create_contact(self, new_contact: dict) -> None:
        """
        Creates a contact.
        """
        body = self._singleton_contact_body(new_contact)
        params = dict(self.params)
        params.update(
            {
                "prefToken": self.pref_token,
                "syncToken": self.sync_token,
            }
        )
        resp = self.session.post(
            self._contacts_update_url,
            params=params,
            data=json.dumps(body),
        ).json()
        self._update_sync_token(resp["syncToken"])

    def update_contact(self, updated_contact: dict) -> None:
        """
        Updates a contact.
        """
        self._update_etag(updated_contact)
        body = self._singleton_contact_body(updated_contact)
        params = dict(self.params)
        params.update(
            {
                "method": "PUT",
                "prefToken": self.pref_token,
                "syncToken": self.sync_token,
            }
        )
        resp = self.session.post(
            self._contacts_update_url,
            params=params,
            data=json.dumps(body),
        ).json()
        self._update_sync_token(resp["syncToken"])

    def create_group(self, group: dict) -> None:
        """
        Creates a contact group.
        """
        group["groupId"] = str(uuid.uuid4())
        body = self._singleton_group_body(group)
        params = dict(self.params)
        params.update(
            {
                "prefToken": self.pref_token,
                "syncToken": self.sync_token,
            }
        )
        resp = self.session.post(
            self._groups_update_url,
            params=params,
            data=json.dumps(body),
        ).json()
        self._update_sync_token(resp["syncToken"])

    def delete_group(self, group: dict) -> None:
        """
        Deletes a contact group.
        """
        self._update_etag(group)
        body = self._singleton_group_body(group)
        params = dict(self.params)
        params.update(
            {
                "method": "DELETE",
                "prefToken": self.pref_token,
                "syncToken": self.sync_token,
            }
        )
        resp = self.session.post(
            self._groups_update_url,
            params=params,
            data=json.dumps(body),
        ).json()
        self._update_sync_token(resp["syncToken"])

    def get_contacts_and_groups(self) -> dict:
        """
        Fetches the contacts and groups.
        """
        params_contacts = dict(self.params)
        params_contacts.update(
            {
                "order": "last,first",
            }
        )
        resp = self.session.get(
            self._contacts_refresh_url, params=params_contacts
        ).json()
        self.pref_token = resp["prefToken"]
        self._update_sync_token(resp["syncToken"])
        groups = resp["groups"]

        params_contacts = dict(self.params)
        params_contacts.update(
            {
                "prefToken": self.pref_token,
                "syncToken": self.sync_token,
                "limit": "0",
                "offset": "0",
            }
        )
        resp = self.session.get(self._contacts_next_url, params=params_contacts).json()
        contacts = resp["contacts"]
        return {"contacts": contacts, "groups": groups}

    def _update_sync_token(self, sync_token: str) -> None:
        self.sync_token_prefix = re.search(r"^.*S=", sync_token)[0]
        self.sync_token_number = int(re.search(r"\d+$", sync_token)[0])

    def _update_etag(self, obj: dict) -> None:
        etag = obj["etag"]
        last_sync_number = int(re.search(r"(?<=^C=)\d+", etag)[0])
        if last_sync_number >= self.sync_token_number:
            etag = re.sub(r"^C=\d+", f"C={self.sync_token_number}", etag)
            obj.update({"etag": etag})

    @staticmethod
    def _singleton_contact_body(contact: dict) -> dict:
        return {"contacts": [contact]}

    @staticmethod
    def _singleton_group_body(contact_group: dict) -> dict:
        return {"groups": [contact_group]}
