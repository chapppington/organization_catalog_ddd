import re
from dataclasses import dataclass

from domain.base.value_object import BaseValueObject
from domain.organization.exceptions import (
    EmptyOrganizationNameException,
    EmptyOrganizationPhoneException,
    InvalidOrganizationPhoneException,
)


@dataclass(frozen=True)
class OrganizationNameValueObject(BaseValueObject):
    value: str

    def validate(self):
        if not self.value:
            raise EmptyOrganizationNameException()

    def as_generic_type(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class OrganizationPhoneValueObject(BaseValueObject):
    value: str

    def validate(self):
        if not self.value:
            raise EmptyOrganizationPhoneException()

        # Remove common formatting characters (spaces, dashes, parentheses, plus)
        digits_only = re.sub(r"[^\d]", "", self.value)

        # Phone number validation rules:
        # - Must contain only digits (after removing formatting)
        # - Length between 10 and 15 digits (international standard)
        # - Can start with + in the original value
        if len(digits_only) < 10 or len(digits_only) > 15:
            raise InvalidOrganizationPhoneException(phone=self.value)

        # Check if original value contains only valid phone characters
        # Allow: digits, +, spaces, dashes, parentheses
        phone_pattern = r"^[\+]?[\d\s\-\(\)]{10,}$"
        if not re.match(phone_pattern, self.value):
            raise InvalidOrganizationPhoneException(phone=self.value)

        # Ensure it contains at least some digits
        if not digits_only:
            raise InvalidOrganizationPhoneException(phone=self.value)

    def as_generic_type(self) -> str:
        return str(self.value)
