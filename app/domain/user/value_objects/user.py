import re
from dataclasses import dataclass

from domain.base.value_object import BaseValueObject
from domain.user.exceptions import (
    EmptyUsernameException,
    InvalidUsernameException,
    UsernameTooLongException,
)


MIN_USERNAME_LENGTH = 3
MAX_USERNAME_LENGTH = 255


@dataclass(frozen=True)
class UsernameValueObject(BaseValueObject):
    value: str

    def validate(self):
        if not self.value:
            raise EmptyUsernameException()

        if len(self.value) < MIN_USERNAME_LENGTH:
            raise InvalidUsernameException(
                username=self.value,
                reason=f"Username must be at least {MIN_USERNAME_LENGTH} characters long",
            )

        if len(self.value) > MAX_USERNAME_LENGTH:
            raise UsernameTooLongException(
                username_length=len(self.value),
                max_length=MAX_USERNAME_LENGTH,
            )

        # Username can contain letters, digits, and underscores
        # Must start with a letter or digit
        username_pattern = r"^[a-zA-Z0-9][a-zA-Z0-9_]*$"
        if not re.match(username_pattern, self.value):
            raise InvalidUsernameException(
                username=self.value,
                reason="Username can only contain letters, digits, and underscores, and must start with a letter or digit",
            )

    def as_generic_type(self) -> str:
        return str(self.value)
