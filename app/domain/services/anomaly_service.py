
from dataclasses import dataclass
from datetime import datetime, timedelta
from statistics import median
from typing import List, Optional

from app.domain.entities.ticket import Ticket


@dataclass(frozen=True)
class Anomaly:
    ticket_id: str
    reason: str
    severity: str
    details: dict


class AnomalyService:

    def _get_reference_time(
        self,
        tickets: List[Ticket],
        reference_time: Optional[datetime],
    ) -> Optional[datetime]:
        """
        Use the provided reference time.

        If no reference time is provided, use the latest
        ticket creation time from the dataset.
        """

        if reference_time is not None:
            return reference_time

        if not tickets:
            return None

        return max(
            ticket.created_at
            for ticket in tickets
        )

    def find_unresolved_high_priority_tickets(
        self,
        tickets: List[Ticket],
        reference_time: Optional[datetime] = None,
        age_hours: float = 24.0,
    ) -> List[Anomaly]:

        resolved_reference_time = (
            self._get_reference_time(
                tickets=tickets,
                reference_time=reference_time,
            )
        )

        if resolved_reference_time is None:
            return []

        cutoff_time = (
            resolved_reference_time
            - timedelta(hours=age_hours)
        )

        anomalies = []

        for ticket in tickets:

            is_high_priority = (
                ticket.priority.lower()
                in {"high", "critical"}
            )

            is_unresolved = (
                ticket.status.lower() != "resolved"
            )

            is_old = (
                ticket.created_at < cutoff_time
            )

            if (
                is_high_priority
                and is_unresolved
                and is_old
            ):

                ticket_age = (
                    resolved_reference_time
                    - ticket.created_at
                ).total_seconds() / 3600

                anomalies.append(
                    Anomaly(
                        ticket_id=ticket.ticket_id,
                        reason=(
                            "Unresolved high-priority ticket "
                            "older than 24 hours"
                        ),
                        severity=ticket.priority,
                        details={
                            "priority": ticket.priority,
                            "status": ticket.status,
                            "age_hours": round(
                                ticket_age,
                                2,
                            ),
                        },
                    )
                )

        return anomalies

    def find_long_resolution_times(
        self,
        tickets: List[Ticket],
    ) -> List[Anomaly]:

        resolved_tickets = [
            ticket
            for ticket in tickets
            if (
                ticket.resolution_time_hrs is not None
                and ticket.resolution_time_hrs >= 0
            )
        ]

        if len(resolved_tickets) < 4:
            return []

        resolution_times = [
            ticket.resolution_time_hrs
            for ticket in resolved_tickets
        ]

        median_time = median(resolution_times)

        deviations = [
            abs(time - median_time)
            for time in resolution_times
        ]

        median_deviation = median(deviations)

        if median_deviation == 0:
            threshold = median_time * 2
        else:
            threshold = (
                median_time
                + 3 * median_deviation
            )

        anomalies = []

        for ticket in resolved_tickets:

            resolution_time = (
                ticket.resolution_time_hrs
            )

            if resolution_time > threshold:

                anomalies.append(
                    Anomaly(
                        ticket_id=ticket.ticket_id,
                        reason=(
                            "Abnormally long resolution time"
                        ),
                        severity="Medium",
                        details={
                            "resolution_time_hrs": (
                                resolution_time
                            ),
                            "threshold_hrs": round(
                                threshold,
                                2,
                            ),
                        },
                    )
                )

        return anomalies

    def detect_all(
        self,
        tickets: List[Ticket],
        reference_time: Optional[datetime] = None,
    ) -> List[Anomaly]:

        unresolved_anomalies = (
            self.find_unresolved_high_priority_tickets(
                tickets=tickets,
                reference_time=reference_time,
            )
        )

        resolution_anomalies = (
            self.find_long_resolution_times(
                tickets=tickets,
            )
        )

        return (
            unresolved_anomalies
            + resolution_anomalies
        )