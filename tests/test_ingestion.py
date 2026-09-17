
from pathlib import Path

from app.application.use_cases.ingest_tickets import IngestTicketsUseCase
from app.infrastructure.repositories.csv_ticket_repository import (
    CsvTicketRepository,
)


def test_csv_ingestion():
    csv_path = Path("data/support_tickets.csv")

    repository = CsvTicketRepository(str(csv_path))
    use_case = IngestTicketsUseCase(repository)

    tickets = use_case.execute()

    assert len(tickets) == 500
    assert tickets[0].ticket_id != ""