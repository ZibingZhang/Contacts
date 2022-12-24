"""Convert a model.Contact into an icloud.model.ICloudContact."""
from __future__ import annotations

from contacts import model
from contacts.common import constant
from contacts.dao import icloud
from contacts.dao.icloud.model import notes as nt
from contacts.utils import uuid_utils


def contact_to_icloud_contact(contact: model.Contact) -> icloud.model.ICloudContact:
    """Convert a model.Contact into an icloud.model.ICloudContact.

    Args:
        contact: The contact to transform.

    Returns:
        The transformed icloud.model.ICloudContact.
    """
    if contact.icloud:
        contact_id = contact.icloud.uuid
    else:
        contact_id = uuid_utils.generate()

    icloud_contact = icloud.model.ICloudContact(
        birthday=contact.birthday,
        contactId=contact_id,
        firstName=contact.name.first_name,
        isCompany=False,
        isGuardianApproved=False,
        lastName=contact.name.last_name,
        nickName=contact.name.nickname,
        photo=contact.icloud.photo,
        prefix=contact.name.prefix,
        suffix=contact.name.suffix,
        whitelisted=False,
    )

    if contact.icloud:
        icloud_contact.etag = contact.icloud.etag

    if contact.tags:
        icloud_contact.companyName = ", ".join(contact.tags)

    if contact.email_addresses:
        icloud_contact.emailAddresses = _transform_email_addresses(
            contact.email_addresses
        )

    if contact.phone_numbers:
        icloud_contact.phones = _transform_phone_numbers(contact.phone_numbers)

    if contact.social_profiles:
        icloud_contact.profiles = _transform_social_profiles(contact.social_profiles)

    if contact.street_addresses:
        icloud_contact.streetAddresses = _transform_street_addresses(
            contact.street_addresses
        )

    if (
        contact.dated
        or contact.education
        or contact.friends_friend
        or contact.name.chinese_name
        or contact.notes
    ):
        icloud_contact.notes = nt.Notes.to_string(_extract_notes(contact))

    return icloud_contact


def _transform_email_addresses(
    email_addresses: list[model.EmailAddresss],
) -> list[icloud.model.EmailAddress]:
    icloud_email_addresses = []
    for email_address in email_addresses:
        icloud_email_addresses.append(
            icloud.model.EmailAddress(
                field=f"{email_address.local_part}@{email_address.domain}",
                label=email_address.label,
            )
        )
    return icloud_email_addresses


def _transform_phone_numbers(
    phone_numbers: list[model.PhoneNumber],
) -> list[icloud.model.Phone]:
    icloud_phones = []
    for phone_number in phone_numbers:
        icloud_phones.append(
            icloud.model.Phone(
                field=f"+{phone_number.country_code}{phone_number.number}",
                label=phone_number.label,
            )
        )
    return icloud_phones


def _transform_social_profiles(
    social_profiles: model.SocialProfiles,
) -> list[icloud.model.Profile]:
    icloud_profiles = []
    if social_profiles.facebook:
        facebook_profile = social_profiles.facebook
        icloud_profiles.append(
            icloud.model.Profile(
                field=(
                    f"http://www.facebook.com/"
                    f"{facebook_profile.username if facebook_profile.username else ''}"
                ),
                label="FACEBOOK",
                user=facebook_profile.username,
                userId=facebook_profile.user_id,
            )
        )
    if social_profiles.game_center:
        game_center_profile = social_profiles.game_center
        icloud_profiles.append(
            icloud.model.Profile(
                field=game_center_profile.link,
                label="GAMECENTER",
                user=game_center_profile.username,
            )
        )
    if social_profiles.instagram:
        instagram_profile = social_profiles.instagram
        icloud_profiles.append(
            icloud.model.Profile(
                field=f"http://www.instagram.com/{instagram_profile.username}",
                label="INSTAGRAM",
                user=instagram_profile.username,
            )
        )
    return icloud_profiles


def _transform_street_addresses(
    street_addresses: list[model.StreetAddress],
) -> list[icloud.model.StreetAddress]:
    icloud_street_addresses = []
    for street_address in street_addresses:
        icloud_street_address = icloud.model.StreetAddress(
            field=icloud.model.StreetAddressField(
                city=street_address.city,
                country=street_address.country,
                postalCode=street_address.postal_code,
                state=street_address.state,
            ),
            label=street_address.label,
        )
        if street_address.country:
            icloud_street_address.field.countryCode = (
                constant.COUNTRY_TO_COUNTRY_CODE_MAP[street_address.country]
            )
        if street_address.street:
            icloud_street_address.field.street = "\n".join(street_address.street)
        icloud_street_addresses.append(icloud_street_address)
    return icloud_street_addresses


def _extract_notes(contact: model.Contact) -> nt.Notes:
    notes = nt.Notes()
    if contact.name.chinese_name:
        notes.chinese_name = contact.name.chinese_name
    if contact.notes:
        notes.comment = contact.notes
    if contact.favorite:
        notes.favorite = nt.Favorites.from_dict(contact.favorite)
    if contact.friends_friend:
        notes.friends_friend = contact.friends_friend
    if contact.dated:
        notes.partner = contact.dated

    if contact.education:
        education = nt.Education()

        if contact.education.bachelor:
            education.bachelor = nt.School(name=contact.education.bachelor.name.value)
            if contact.education.bachelor.graduation_year:
                education.bachelor.grad_year = (
                    contact.education.bachelor.graduation_year
                )
            if contact.education.bachelor.majors:
                education.bachelor.majors = ", ".join(contact.education.bachelor.majors)
            if contact.education.bachelor.minors:
                education.bachelor.minors = ", ".join(contact.education.bachelor.minors)

        if contact.education.high_school:
            education.high_school = nt.School(
                name=contact.education.high_school.name.value
            )
            if contact.education.high_school.graduation_year:
                education.high_school.grad_year = (
                    contact.education.high_school.graduation_year
                )

        if contact.education.master:
            education.master = nt.School(name=contact.education.master.name.value)
            if contact.education.master.graduation_year:
                education.master.grad_year = contact.education.master.graduation_year
            if contact.education.master.majors:
                education.master.majors = ", ".join(contact.education.master.majors)
            if contact.education.master.minors:
                education.master.minors = ", ".join(contact.education.master.minors)

        notes.education = education

    return notes
