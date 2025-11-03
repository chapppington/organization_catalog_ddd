from collections import defaultdict
from dataclasses import (
    dataclass,
    field,
)
from typing import Iterable

from application.commands.base import (
    BaseCommand,
    BaseCommandHandler,
    CommandResultType,
    CommandType,
)
from application.exceptions.mediator import CommandHandlersNotRegisteredException
from application.queries.base import (
    BaseQuery,
    BaseQueryHandler,
    QueryResultType,
    QueryType,
)


@dataclass(eq=False)
class Mediator:
    commands_map: dict[CommandType, BaseCommandHandler] = field(
        default_factory=lambda: defaultdict(list),
        kw_only=True,
    )

    queries_map: dict[QueryType, BaseQueryHandler] = field(
        default_factory=dict,
        kw_only=True,
    )

    def register_command(
        self,
        command: CommandType,
        command_handlers: Iterable[BaseCommandHandler[CommandType, CommandResultType]],
    ):
        self.commands_map[command].extend(command_handlers)

    def register_query(
        self,
        query: QueryType,
        query_handler: BaseQueryHandler[QueryType, QueryResultType],
    ):
        self.queries_map[query] = query_handler

    async def handle_command(self, command: BaseCommand) -> Iterable[CommandResultType]:
        command_type = command.__class__

        handlers = self.commands_map.get(command_type)

        if not handlers:
            raise CommandHandlersNotRegisteredException(command_type)

        return [await handler.handle(command) for handler in handlers]

    async def handle_query(self, query: BaseQuery) -> QueryResultType:
        return await self.queries_map[query.__class__].handle(query=query)
