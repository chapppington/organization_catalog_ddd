from dataclasses import dataclass

from domain.base.value_object import BaseValueObject
from domain.organization.exceptions import EmptyActivityNameException


@dataclass(frozen=True)
class ActivityNameValueObject(BaseValueObject):
    value: str

    def validate(self):
        if not self.value:
            raise EmptyActivityNameException()

    def as_generic_type(self) -> str:
        return str(self.value)
