from __future__ import annotations

import re
import typing

import model
from transformer import notes

if typing.TYPE_CHECKING:
    from data import icloud


PHONE_NUMBER_REGEX = re.compile(r"^\+\d+$")


def icloud_contact_to_contact(icloud_contact: icloud.ICloudContact) -> model.Contact:
    # TODO: add support for these fields
    if (
        icloud_contact.IMs
        or icloud_contact.dates
        or icloud_contact.department
        or icloud_contact.jobTitle
        or icloud_contact.phoneticCompanyName
        or icloud_contact.phoneticFirstName
        or icloud_contact.phoneticLastName
        or icloud_contact.relatedNames
        or icloud_contact.suffix
        or icloud_contact.urls
    ):
        raise ValueError(icloud_contact)

    contact = model.Contact(
        birthday=icloud_contact.birthday,
        icloud=model.ICloud(
            etag=icloud_contact.etag,
            photo=icloud_contact.photo,
            uuid=icloud_contact.contactId,
        ),
        name=model.Name(
            prefix=icloud_contact.prefix,
            first_name=icloud_contact.firstName,
            nickname=icloud_contact.nickName,
            last_name=icloud_contact.lastName,
            suffix=icloud_contact.suffix,
        ),
    )

    if icloud_contact.companyName:
        contact.tags = icloud_contact.companyName.split(", ")

    if icloud_contact.emailAddresses:
        contact.email_addresses = _transform_email_addresses(
            icloud_contact.emailAddresses
        )

    if icloud_contact.phones:
        contact.phone_numbers = _transform_phone_numbers(icloud_contact.phones)

    if icloud_contact.profiles:
        contact.social_profiles = _transform_social_profiles(icloud_contact.profiles)

    if icloud_contact.notes:
        _transform_notes(contact, notes.from_string(icloud_contact.notes))

    return contact


def _transform_email_addresses(
    icloud_email_addresses: list[icloud.model.EmailAddress],
) -> list[model.EmailAddresss]:
    email_addresses = []
    for icloud_email_address in icloud_email_addresses:
        if icloud_email_address.field.count("@") != 1:
            raise ValueError
        local_part, domain = icloud_email_address.field.split("@")
        email_addresses.append(
            model.EmailAddresss(
                domain=domain, label=icloud_email_address.label, local_part=local_part
            )
        )
    return email_addresses


def _transform_phone_numbers(
    icloud_phones: list[icloud.model.Phone],
) -> list[model.PhoneNumber]:
    phone_numbers = []
    for icloud_phone in icloud_phones:
        if not PHONE_NUMBER_REGEX.match(icloud_phone.field):
            raise ValueError
        for country_code in model.CountryCode:
            if not icloud_phone.field.startswith(f"+{country_code}"):
                continue
            phone_numbers.append(
                model.PhoneNumber(
                    countryCode=country_code,
                    label=icloud_phone.label,
                    number=int(icloud_phone.field.split(f"+{country_code}")[1]),
                )
            )
            break
        else:
            raise ValueError
    return phone_numbers


def _transform_social_profiles(
    icloud_profiles: list[icloud.model.Profile],
) -> model.SocialProfiles:
    social_profiles = model.SocialProfiles()
    for icloud_profile in icloud_profiles:
        match icloud_profile.label:
            case "FACEBOOK":
                social_profiles.facebook = model.FacebookProfile(
                    user_id=icloud_profile.userId, username=icloud_profile.user
                )
            case "GAMECENTER":
                social_profiles.game_center = model.GameCenterProfile(
                    link=icloud_profile.field, username=icloud_profile.user
                )
            case _:
                raise ValueError
    return social_profiles


def _transform_notes(contact: model.Contact, notes: notes.Notes) -> None:
    if notes.chinese_name:
        contact.name.chinese_name = notes.chinese_name
    if notes.comment:
        contact.notes = notes.comment
    if notes.family:
        contact.family = notes.family
    if notes.partner:
        contact.dated = notes.partner
