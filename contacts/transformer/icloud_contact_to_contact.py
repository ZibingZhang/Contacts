from __future__ import annotations

import re
import typing

import model
from transformer import notes as nt

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

    if icloud_contact.streetAddresses:
        contact.street_addresses = _transform_street_addresses(
            icloud_contact.streetAddresses
        )

    if icloud_contact.notes:
        _extract_from_notes(contact, nt.from_string(icloud_contact.notes))

    return contact


def _transform_email_addresses(
    icloud_email_addresses: list[icloud.model.EmailAddress],
) -> list[model.EmailAddresss]:
    email_addresses = []
    for icloud_email_address in icloud_email_addresses:
        assert icloud_email_address.field.count("@") == 1
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
            raise ValueError(f"Invalid phone number format: {icloud_phone.field}")
        for country_code in model.CountryCode:
            if not icloud_phone.field.startswith(f"+{country_code}"):
                continue
            phone_numbers.append(
                model.PhoneNumber(
                    country_code=country_code,
                    label=icloud_phone.label,
                    number=icloud_phone.field.split(f"+{country_code}")[1],
                )
            )
            break
        else:
            raise ValueError(f"Unsupported country code: {icloud_phone.field}")
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
            case "INSTAGRAM":
                social_profiles.instagram = model.InstagramProfile(
                    username=icloud_profile.user
                )
            case _:
                raise ValueError(
                    f"Unsupported social profile label: {icloud_profile.label}"
                )
    return social_profiles


def _transform_street_addresses(
    icloud_street_addresses: list[icloud.model.StreetAddress],
) -> list[model.StreetAddress]:
    street_addresses = []
    for icloud_street_address in icloud_street_addresses:
        street_addresses.append(
            model.StreetAddress(
                city=icloud_street_address.field.city,
                country=icloud_street_address.field.country,
                label=icloud_street_address.label,
                postal_code=icloud_street_address.field.postalCode,
                state=icloud_street_address.field.state,
                street=icloud_street_address.field.street.splitlines(),
            )
        )
    return street_addresses


def _extract_from_notes(contact: model.Contact, notes: nt.Notes) -> None:
    if notes.chinese_name:
        contact.name.chinese_name = notes.chinese_name
    if notes.comment:
        contact.notes = notes.comment
    if notes.favorite:
        contact.favorite = notes.favorite
    if notes.friends_friend:
        contact.friends_friend = notes.friends_friend
    if notes.partner:
        contact.dated = notes.partner

    if notes.education:
        education = model.Education()

        if notes.education.bachelor:
            education.bachelor = model.University(
                name=model.UniversityName(notes.education.bachelor.name)
            )
            if notes.education.bachelor.grad_year:
                education.bachelor.graduation_year = notes.education.bachelor.grad_year
            if notes.education.bachelor.majors:
                education.bachelor.majors = notes.education.bachelor.majors.split(", ")
            if notes.education.bachelor.minors:
                education.bachelor.minors = notes.education.bachelor.minors.split(", ")

        if notes.education.high_school:
            education.high_school = model.HighSchool(
                name=model.HighSchoolName(notes.education.high_school.name)
            )
            if notes.education.high_school.grad_year:
                education.high_school.graduation_year = (
                    notes.education.high_school.grad_year
                )

        if notes.education.master:
            education.master = model.University(
                name=model.UniversityName(notes.education.master.name)
            )
            if notes.education.master.grad_year:
                education.master.graduation_year = notes.education.master.grad_year
            if notes.education.master.majors:
                education.master.majors = notes.education.master.majors.split(", ")
            if notes.education.master.minors:
                education.master.minors = notes.education.master.minors.split(", ")

        contact.education = education
