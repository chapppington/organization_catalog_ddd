from dataclasses import dataclass

from domain.base.exceptions import ApplicationException


class CommitException(ApplicationException):
    pass


class RollbackException(ApplicationException):
    pass


class RepoException(ApplicationException):
    pass


@dataclass(eq=False)
class MappingException(ApplicationException):
    _text: str

    @property
    def title(self) -> str:
        return self._text
