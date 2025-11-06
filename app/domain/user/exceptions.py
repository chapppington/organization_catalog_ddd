from dataclasses import dataclass
from uuid import UUID

from domain.base.exceptions import ApplicationException


@dataclass(eq=False)
class UserException(ApplicationException):
    @property
    def message(self) -> str:
        return "User exception occurred"


@dataclass(eq=False)
class EmptyUsernameException(UserException):
    @property
    def message(self) -> str:
        return "Username is empty"


@dataclass(eq=False)
class InvalidUsernameException(UserException):
    username: str
    reason: str

    @property
    def message(self) -> str:
        return f"Invalid username '{self.username}': {self.reason}"


@dataclass(eq=False)
class UsernameTooLongException(UserException):
    username_length: int
    max_length: int

    @property
    def message(self) -> str:
        return (
            f"Username is too long. Current length is {self.username_length}, "
            f"maximum allowed length is {self.max_length}"
        )


@dataclass(eq=False)
class EmptyPasswordException(UserException):
    @property
    def message(self) -> str:
        return "Password is empty"


@dataclass(eq=False)
class PasswordTooShortException(UserException):
    password_length: int
    min_length: int

    @property
    def message(self) -> str:
        return (
            f"Password is too short. Current length is {self.password_length}, "
            f"minimum required length is {self.min_length}"
        )


@dataclass(eq=False)
class InvalidPasswordException(UserException):
    reason: str

    @property
    def message(self) -> str:
        return f"Invalid password: {self.reason}"


@dataclass(eq=False)
class APIKeyNotFoundException(UserException):
    api_key: UUID

    @property
    def message(self) -> str:
        return f"API key {self.api_key} not found"


@dataclass(eq=False)
class APIKeyBannedException(UserException):
    api_key: UUID

    @property
    def message(self) -> str:
        return f"API key {self.api_key} is banned"


@dataclass(eq=False)
class InvalidAPIKeyException(UserException):
    api_key: str
    reason: str

    @property
    def message(self) -> str:
        return f"Invalid API key '{self.api_key}': {self.reason}"


@dataclass(eq=False)
class UserNotFoundException(UserException):
    user_id: UUID

    @property
    def message(self) -> str:
        return f"User with id {self.user_id} not found"


@dataclass(eq=False)
class UserAlreadyExistsException(UserException):
    username: str

    @property
    def message(self) -> str:
        return f"User with username '{self.username}' already exists"


@dataclass(eq=False)
class InvalidCredentialsException(UserException):
    @property
    def message(self) -> str:
        return "Invalid credentials"
