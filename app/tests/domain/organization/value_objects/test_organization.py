import pytest

from domain.organization.exceptions import (
    EmptyOrganizationNameException,
    EmptyOrganizationPhoneException,
    InvalidOrganizationPhoneException,
)
from domain.organization.value_objects import (
    OrganizationNameValueObject,
    OrganizationPhoneValueObject,
)


@pytest.mark.parametrize(
    "name,should_raise",
    [
        ("ООО Рога и Копыта", False),
        ("ИП Иванов", False),
        ("Торговый дом", False),
        ("", True),
    ],
)
def test_organization_name_value_object(name, should_raise):
    if should_raise:
        with pytest.raises(EmptyOrganizationNameException):
            OrganizationNameValueObject(value=name)
    else:
        obj = OrganizationNameValueObject(value=name)
        assert obj.as_generic_type() == name


@pytest.mark.parametrize(
    "phone,should_raise",
    [
        ("+7 (495) 123-45-67", False),
        ("8-923-666-13-13", False),
        ("+7 (495) 222-22-22", False),
        ("+7 (495) 333-33-33", False),
        ("+1 (555) 123-4567", False),
        ("5551234567", False),
        ("", True),
        ("123", True),
        ("2-222-222", True),  # Too short (only 7 digits)
        ("3-333-333", True),  # Too short (only 7 digits)
        ("++1234567890", True),
        ("invalid-phone", True),
        ("abc", True),
    ],
)
def test_organization_phone_value_object(phone, should_raise):
    if should_raise:
        with pytest.raises(
            (EmptyOrganizationPhoneException, InvalidOrganizationPhoneException),
        ):
            OrganizationPhoneValueObject(value=phone)
    else:
        obj = OrganizationPhoneValueObject(value=phone)
        assert obj.as_generic_type() == phone
