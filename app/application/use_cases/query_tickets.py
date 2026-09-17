from typing import List

from app.application.dto.query_dto import QueryResult
from app.domain.entities.ticket import Ticket
from app.domain.entities.ticket_query import TicketQuery
from app.domain.services.ticket_query_service import TicketQueryService


class QueryTicketsUseCase:

    def __init__(
        self,
        query_service: TicketQueryService,
    ):
        self.query_service = query_service

    def execute(
        self,
        tickets: List[Ticket],
        query: TicketQuery,
    ) -> QueryResult:

        return self.query_service.execute(
            tickets=tickets,
            query=query,
        )