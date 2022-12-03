from __future__ import annotations

import re
import uuid

import model
from common import constant
from transformer import notes as nt

from data import icloud

PHONE_NUMBER_REGEX = re.compile(r"^\+\d+$")


def contact_to_icloud_contact(contact: model.Contact) -> icloud.ICloudContact:
    if not contact.icloud:
        contact.icloud = model.ICloud(uuid=str(uuid.uuid4()).upper())

    icloud_contact = icloud.ICloudContact(
        birthday=contact.birthday,
        contactId=contact.icloud.uuid,
        etag=contact.icloud.etag,
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
        icloud_contact.notes = nt.to_string(_extract_notes(contact))

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
) -> [icloud.model.Profile]:
    icloud_profiles = []
    if social_profiles.facebook:
        social_profile = social_profiles.facebook
        icloud_profiles.append(
            icloud.model.Profile(
                field=(
                    f"http://www.facebook.com/"
                    f"{social_profile.username if social_profile.username else ''}"
                ),
                label="FACEBOOK",
                user=social_profile.username,
                userId=social_profile.user_id,
            )
        )
    if social_profiles.game_center:
        social_profile = social_profiles.game_center
        icloud_profiles.append(
            icloud.model.Profile(
                field=social_profile.link,
                label="GAMECENTER",
                user=social_profile.username,
            )
        )
    if social_profiles.instagram:
        social_profile = social_profiles.instagram
        icloud_profiles.append(
            icloud.model.Profile(
                field=f"http://www.instagram.com/{social_profile.username}",
                label="INSTAGRAM",
                user=social_profile.username,
            )
        )
    return icloud_profiles


def _transform_street_addresses(
    street_addresses: list[model.StreetAddress],
) -> list[icloud.model.StreetAddress]:
    icloud_street_addresses = []
    for street_address in street_addresses:
        icloud_street_addresses.append(
            icloud.model.StreetAddress(
                field=icloud.model.StreetAddressField(
                    city=street_address.city,
                    country=street_address.country,
                    countryCode=constant.COUNTRY_TO_COUNTRY_CODE_MAP.get(
                        street_address.country
                    ),
                    postalCode=street_address.postal_code,
                    state=street_address.state,
                    street="\n".join(street_address.street),
                ),
                label=street_address.label,
            )
        )
    return icloud_street_addresses


def _extract_notes(contact: model.Contact) -> nt.Notes:
    notes = nt.Notes()
    if contact.name.chinese_name:
        notes.chinese_name = contact.name.chinese_name
    if contact.notes:
        notes.comment = contact.notes
    if contact.favorite:
        notes.favorite = contact.favorite
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
                education.master.graduation_year = (
                    contact.education.master.graduation_year
                )
            if contact.education.master.majors:
                education.master.majors = ", ".join(contact.education.master.majors)
            if contact.education.master.minors:
                education.master.minors = ", ".join(contact.education.master.minors)

        notes.education = education

    return notes
