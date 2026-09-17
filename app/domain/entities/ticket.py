
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass(frozen=True)
class Ticket:
    ticket_id: str
    created_at: datetime
    category: str
    priority: str
    status: str
    response_time_hrs: float
    resolution_time_hrs: Optional[float]
    agent_id: str
    customer_rating: Optional[int]
    issue_summary: str