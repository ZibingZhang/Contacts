import re

import model


def extract_name(contact: model.Contact) -> str:
    name = ""
    if contact.name.first_name is not None:
        name = contact.name.first_name
    if contact.name.last_name:
        if name:
            return name + " " + contact.name.last_name
        return contact.name.last_name
    return name


def add_tag(contact: model.Contact, tag: str) -> None:
    contact.tags = contact.tags + [tag]


def add_email_if_not_exists(contact: model.Contact, email: str, label: str) -> None:
    assert email.count("@") == 1
    local_part, domain = email.split("@")
    new_email_address = model.EmailAddresss(
        domain=domain, label=label, local_part=local_part
    )

    if contact.email_addresses is None:
        contact.email_addresses = [new_email_address]
        return

    for email_address in contact.email_addresses:
        if email_address.local_part == local_part and email_address.domain == domain:
            return
    contact.email_addresses.append(new_email_address)


def add_phone_number_if_not_exists(
    contact: model.Contact, country_code: model.CountryCode, number: str, label: str
) -> None:
    assert re.match(r"^\d+$", number)
    new_phone_number = model.PhoneNumber(
        country_code=country_code, number=number, label=label
    )

    if contact.phone_numbers is None:
        contact.phone_numbers = [new_phone_number]
        return

    for phone_number in contact.phone_numbers:
        if phone_number.country_code == country_code and phone_number.number == number:
            return
    contact.phone_numbers.append(new_phone_number)
