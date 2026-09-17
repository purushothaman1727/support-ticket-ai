
from abc import ABC, abstractmethod
from typing import List

from app.domain.entities.ticket import Ticket


class TicketRepository(ABC):

    @abstractmethod
    def get_all(self) -> List[Ticket]:
        """Return all tickets."""
        raise NotImplementedError

    @abstractmethod
    def load(self) -> None:
        """Load tickets from the data source."""
        raise NotImplementedError