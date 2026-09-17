from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class TicketQuery:
    operation: str
    status: Optional[str] = None
    category: Optional[str] = None
    priority: Optional[str] = None
    agent_id: Optional[str] = None
    max_resolution_hours: Optional[float] = None