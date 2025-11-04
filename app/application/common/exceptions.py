from dataclasses import dataclass

from domain.base.exceptions import ApplicationException


class UnexpectedException(ApplicationException):
    pass


class CommitException(UnexpectedException):
    pass


class RollbackException(UnexpectedException):
    pass


class RepoException(UnexpectedException):
    pass


@dataclass(eq=False)
class MappingException(ApplicationException):
    _text: str

    @property
    def title(self) -> str:
        return self._text
