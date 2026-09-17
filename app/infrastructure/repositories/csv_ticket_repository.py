
import csv
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from app.domain.entities.ticket import Ticket
from app.domain.repositories.ticket_repository import TicketRepository


class CsvTicketRepository(TicketRepository):

    REQUIRED_COLUMNS = {
        "ticket_id",
        "created_at",
        "category",
        "priority",
        "status",
        "response_time_hrs",
        "resolution_time_hrs",
        "agent_id",
        "customer_rating",
        "issue_summary",
    }

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self._tickets: List[Ticket] = []

    def load(self) -> None:
        if not self.file_path.exists():
            raise FileNotFoundError(
                f"CSV file not found: {self.file_path}"
            )

        with self.file_path.open(
            mode="r",
            encoding="utf-8-sig",
            newline="",
        ) as file:
            reader = csv.DictReader(file)

            if reader.fieldnames is None:
                raise ValueError("CSV file has no header")

            missing_columns = (
                self.REQUIRED_COLUMNS - set(reader.fieldnames)
            )

            if missing_columns:
                raise ValueError(
                    f"Missing columns: {sorted(missing_columns)}"
                )

            tickets = []

            for row_number, row in enumerate(reader, start=2):
                try:
                    ticket = self._to_ticket(row)
                    tickets.append(ticket)
                except (ValueError, TypeError) as exc:
                    raise ValueError(
                        f"Invalid data at CSV row {row_number}: {exc}"
                    ) from exc

            self._tickets = tickets

    def get_all(self) -> List[Ticket]:
        return list(self._tickets)

    @staticmethod
    def _to_ticket(row: dict) -> Ticket:
        ticket_id = _required_text(row, "ticket_id")
        category = _required_text(row, "category")
        priority = _required_text(row, "priority")
        status = _required_text(row, "status")
        agent_id = _required_text(row, "agent_id")
        issue_summary = _required_text(row, "issue_summary")

        created_at = datetime.strptime(
            _required_text(row, "created_at"),
            "%d-%m-%Y %H:%M",
    )

        response_time_hrs = float(
            _required_text(row, "response_time_hrs")
        )

        resolution_time_hrs = _optional_float(
            row.get("resolution_time_hrs")
        )

        customer_rating = _optional_int(
            row.get("customer_rating")
        )

        if response_time_hrs < 0:
            raise ValueError("Response time cannot be negative")

        if resolution_time_hrs is not None and resolution_time_hrs < 0:
            raise ValueError("Resolution time cannot be negative")

        if customer_rating is not None and not 1 <= customer_rating <= 5:
            raise ValueError("Customer rating must be between 1 and 5")

        return Ticket(
            ticket_id=ticket_id,
            created_at=created_at,
            category=category,
            priority=priority,
            status=status,
            response_time_hrs=response_time_hrs,
            resolution_time_hrs=resolution_time_hrs,
            agent_id=agent_id,
            customer_rating=customer_rating,
            issue_summary=issue_summary,
        )


def _required_text(row: dict, column: str) -> str:
    value = row.get(column)

    if value is None or not value.strip():
        raise ValueError(f"{column} is required")

    return value.strip()


def _optional_float(value: Optional[str]) -> Optional[float]:
    if value is None or not value.strip():
        return None

    return float(value)


def _optional_int(value: Optional[str]) -> Optional[int]:
    if value is None or not value.strip():
        return None

    return int(value)