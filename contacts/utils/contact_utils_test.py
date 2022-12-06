import model
import pytest
from contact_utils import (
    add_email_address_if_not_exists,
    add_phone_number_if_not_exists,
    build_name_str,
)


def test_extract_name():
    assert (
        build_name_str(
            model.Contact(name=model.Name(first_name="John", last_name="Smith"))
        )
        == "John Smith"
    )


def test_extract_name_without_last_name():
    assert build_name_str(model.Contact(name=model.Name(first_name="John"))) == "John"


def test_add_email_address_to_contact():
    contact = model.Contact(name=model.Name())
    local_part = "john.smith"
    domain = "gmail.com"
    email_address = f"{local_part}@{domain}"
    label = "HOME"

    add_email_address_if_not_exists(contact, email_address, label)

    assert len(contact.email_addresses) == 1
    assert contact.email_addresses[0] == model.EmailAddresss(
        local_part=local_part, domain=domain, label=label
    )


def test_add_email_address_to_contact_does_nothing_if_already_exists():
    local_part = "john.smith"
    domain = "gmail.com"
    email_address = f"{local_part}@{domain}"
    label = "HOME"
    contact = model.Contact(
        name=model.Name(),
        email_addresses=[
            model.EmailAddresss(local_part=local_part, domain=domain, label=label)
        ],
    )

    assert len(contact.email_addresses) == 1

    add_email_address_if_not_exists(contact, email_address, label)

    assert len(contact.email_addresses) == 1


def test_add_email_address_error_if_multiple_at_characters():
    with pytest.raises(AssertionError):
        add_email_address_if_not_exists(
            model.Contact(name=model.Name()), "email@with@ats", "HOME"
        )


def test_add_phone_number_to_contact():
    contact = model.Contact(name=model.Name())
    country_code = model.CountryCode.NANP
    number = "911"
    label = "HOME"

    add_phone_number_if_not_exists(contact, country_code, number, label)

    assert len(contact.phone_numbers) == 1
    assert contact.phone_numbers[0] == model.PhoneNumber(
        country_code=country_code, number=number, label=label
    )


def test_add_phone_number_to_contact_does_nothing_if_already_exists():
    country_code = model.CountryCode.NANP
    number = "911"
    label = "HOME"
    contact = model.Contact(
        name=model.Name(),
        phone_numbers=[
            model.PhoneNumber(country_code=country_code, number=number, label=label)
        ],
    )

    assert len(contact.phone_numbers) == 1

    add_phone_number_if_not_exists(contact, country_code, number, label)

    assert len(contact.phone_numbers) == 1


def test_add_phone_number_error_if_number_not_all_digits():
    with pytest.raises(AssertionError):
        add_phone_number_if_not_exists(
            model.Contact(name=model.Name()), model.CountryCode.NANP, "123a", "HOME"
        )
