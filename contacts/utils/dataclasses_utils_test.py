import model
import pytest


def test_patch_dataclass_error_if_patch_not_subclass():
    with pytest.raises(ValueError):
        name = model.Name()
        patch = model.PhoneNumber(
            country_code=model.CountryCode.NANP.value, number="911"
        )
        name.patch(patch)


def test_patch_dataclasses():
    contact = model.Contact(
        name=model.Name(first_name="John", last_name="Smith"),
        notes="notes",
        tags=["tag1", "tag2"],
    )
    patch = model.Contact(name=model.Name(first_name="Jane"), tags=["tag3"])

    contact.patch(patch)

    assert contact == model.Contact(
        name=model.Name(first_name="Jane", last_name="Smith"),
        notes="notes",
        tags=["tag3"],
    )
