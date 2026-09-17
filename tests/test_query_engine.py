
from pathlib import Path

from app.application.dto.query_dto import TicketQuery
from app.application.use_cases.ingest_tickets import IngestTicketsUseCase
from app.application.use_cases.query_tickets import QueryTicketsUseCase
from app.domain.services.ticket_query_service import TicketQueryService
from app.infrastructure.repositories.csv_ticket_repository import (
    CsvTicketRepository,
)


def get_tickets():
    csv_path = Path("data/support_tickets.csv")

    repository = CsvTicketRepository(str(csv_path))
    ingestion = IngestTicketsUseCase(repository)

    return ingestion.execute()


def test_count_open_tickets():
    tickets = get_tickets()

    query_service = TicketQueryService()
    use_case = QueryTicketsUseCase(query_service)

    query = TicketQuery(
        operation="count",
        status="Open",
    )

    result = use_case.execute(tickets, query)

    assert result.data["count"] >= 0


def test_average_technical_rating():
    tickets = get_tickets()

    query_service = TicketQueryService()
    use_case = QueryTicketsUseCase(query_service)

    query = TicketQuery(
        operation="average_rating",
        category="Technical",
    )

    result = use_case.execute(tickets, query)

    assert result.data["average_rating"] is None or (
        1 <= result.data["average_rating"] <= 5
    )


def test_top_resolved_agent():
    tickets = get_tickets()

    query_service = TicketQueryService()
    use_case = QueryTicketsUseCase(query_service)

    query = TicketQuery(
        operation="top_resolved_agent",
    )

    result = use_case.execute(tickets, query)

    assert "agents" in result.data