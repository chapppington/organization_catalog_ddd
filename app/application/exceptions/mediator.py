from dataclasses import dataclass

from application.exceptions.base import LogicException


@dataclass(eq=False)
class CommandHandlersNotRegisteredException(LogicException):
    command_type: type

    @property
    def message(self) -> str:
        return f"Command handlers not registered for command type: {self.command_type.__name__}"
