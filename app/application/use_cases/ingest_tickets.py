
from typing import List

from app.domain.entities.ticket import Ticket
from app.domain.repositories.ticket_repository import TicketRepository


class IngestTicketsUseCase:

    def __init__(self, repository: TicketRepository):
        self.repository = repository

    def execute(self) -> List[Ticket]:
        self.repository.load()
        return self.repository.get_all()