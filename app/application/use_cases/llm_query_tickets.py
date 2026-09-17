
from typing import List

from app.application.dto.query_dto import QueryResult
from app.application.ports.llm_provider import LLMProvider
from app.domain.entities.ticket import Ticket
from app.domain.entities.ticket_query import TicketQuery
from app.domain.services.ticket_query_service import TicketQueryService


class LLMQueryTicketsUseCase:

    def __init__(
        self,
        llm_provider: LLMProvider,
        query_service: TicketQueryService,
    ):
        self.llm_provider = llm_provider
        self.query_service = query_service

    def execute(
        self,
        tickets: List[Ticket],
        question: str,
    ) -> QueryResult:

        # Step 1: Convert natural language into intent
        intent = self.llm_provider.extract_query_intent(
            question
        )

        # Step 2: Convert intent into domain query
        query = TicketQuery(
            operation=intent.operation,
            status=intent.status,
            category=intent.category,
            priority=intent.priority,
            agent_id=intent.agent_id,
            max_resolution_hours=(
                intent.max_resolution_hours
            ),
        )

        # Step 3: Execute deterministic query
        result = self.query_service.execute(
            tickets=tickets,
            query=query,
        )

        return result