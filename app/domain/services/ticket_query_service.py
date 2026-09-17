
from datetime import timedelta
from statistics import median
from collections import Counter
from typing import List

from app.application.dto.query_dto import QueryResult, TicketQuery
from app.domain.entities.ticket import Ticket


class TicketQueryService:

    def execute(
        self,
        tickets: List[Ticket],
        query: TicketQuery,
    ) -> QueryResult:

        filtered_tickets = self._filter_tickets(tickets, query)

        if query.operation == "count":
            return self._count_tickets(filtered_tickets, query)

        if query.operation == "average_rating":
            return self._average_rating(filtered_tickets, query)

        if query.operation == "top_resolved_agent":
            return self._top_resolved_agent(filtered_tickets, query)

        if query.operation == "top_resolved_agent_this_month":
            return self._top_resolved_agent_this_month(
                filtered_tickets,
                query,
            )

        if query.operation == "lowest_average_rating_agent":
            return self._lowest_average_rating_agent(
                filtered_tickets,
                query,
            )

        if query.operation == "critical_unresolved":
            return self._critical_unresolved(
                filtered_tickets,
                query,
            )

        if query.operation == "resolution_time_anomaly":
            return self._resolution_time_anomaly(
                filtered_tickets,
                query,
            )

        raise ValueError(
            f"Unsupported query operation: {query.operation}"
        )

    def _filter_tickets(
        self,
        tickets: List[Ticket],
        query: TicketQuery,
    ) -> List[Ticket]:

        filtered = tickets

        if query.status is not None:
            filtered = [
                ticket
                for ticket in filtered
                if ticket.status.lower() == query.status.lower()
            ]

        if query.category is not None:
            filtered = [
                ticket
                for ticket in filtered
                if ticket.category.lower() == query.category.lower()
            ]

        if query.priority is not None:
            filtered = [
                ticket
                for ticket in filtered
                if ticket.priority.lower() == query.priority.lower()
            ]

        if query.agent_id is not None:
            filtered = [
                ticket
                for ticket in filtered
                if ticket.agent_id
                and ticket.agent_id.lower() == query.agent_id.lower()
            ]

        return filtered

    @staticmethod
    def _count_tickets(
        tickets: List[Ticket],
        query: TicketQuery,
    ) -> QueryResult:

        count = len(tickets)

        return QueryResult(
            operation=query.operation,
            answer=f"Total matching tickets: {count}",
            data={"count": count},
        )

    @staticmethod
    def _average_rating(
        tickets: List[Ticket],
        query: TicketQuery,
    ) -> QueryResult:

        ratings = [
            ticket.customer_rating
            for ticket in tickets
            if ticket.customer_rating is not None
        ]

        if not ratings:
            return QueryResult(
                operation=query.operation,
                answer="No customer ratings available.",
                data={
                    "average_rating": None,
                    "rated_tickets": 0,
                },
            )

        average = sum(ratings) / len(ratings)

        return QueryResult(
            operation=query.operation,
            answer=f"Average customer rating: {average:.2f}",
            data={
                "average_rating": round(average, 2),
                "rated_tickets": len(ratings),
            },
        )

    @staticmethod
    def _top_resolved_agent(
        tickets: List[Ticket],
        query: TicketQuery,
    ) -> QueryResult:

        resolved_tickets = [
            ticket
            for ticket in tickets
            if ticket.status.lower() == "resolved"
            and ticket.agent_id is not None
        ]

        return TicketQueryService._build_agent_count_result(
            resolved_tickets,
            query,
            "all time",
        )

    @staticmethod
    def _top_resolved_agent_this_month(
        tickets: List[Ticket],
        query: TicketQuery,
    ) -> QueryResult:

        if not tickets:
            return QueryResult(
                operation=query.operation,
                answer="No tickets available.",
                data={
                    "top_agents": [],
                    "resolved_count": 0,
                    "agents": [],
                },
            )

        # Dataset-relative latest month.
        latest_date = max(
            ticket.created_at
            for ticket in tickets
        )

        monthly_tickets = [
            ticket
            for ticket in tickets
            if ticket.created_at.year == latest_date.year
            and ticket.created_at.month == latest_date.month
            and ticket.status.lower() == "resolved"
            and ticket.agent_id is not None
        ]

        return TicketQueryService._build_agent_count_result(
            monthly_tickets,
            query,
            (
                f"{latest_date.year}-"
                f"{latest_date.month:02d}"
            ),
        )

    @staticmethod
    def _build_agent_count_result(
        tickets: List[Ticket],
        query: TicketQuery,
        period: str,
    ) -> QueryResult:

        agent_counts = Counter(
            ticket.agent_id
            for ticket in tickets
            if ticket.agent_id is not None
        )

        if not agent_counts:
            return QueryResult(
                operation=query.operation,
                answer=f"No resolved tickets available for {period}.",
                data={
                    "top_agents": [],
                    "resolved_count": 0,
                    "agents": [],
                    "period": period,
                },
            )

        sorted_agents = sorted(
            agent_counts.items(),
            key=lambda item: (-item[1], item[0]),
        )

        max_count = sorted_agents[0][1]

        top_agents = [
            agent_id
            for agent_id, count in sorted_agents
            if count == max_count
        ]

        agents = [
            {
                "agent_id": agent_id,
                "resolved_count": count,
            }
            for agent_id, count in sorted_agents
        ]

        if len(top_agents) == 1:
            answer = (
                f"Agent {top_agents[0]} resolved "
                f"the most tickets in {period}: {max_count}"
            )
        else:
            agent_names = " and ".join(top_agents)

            answer = (
                f"Agents {agent_names} resolved "
                f"the most tickets in {period}: {max_count} each"
            )

        return QueryResult(
            operation=query.operation,
            answer=answer,
            data={
                "top_agents": top_agents,
                "resolved_count": max_count,
                "agents": agents,
                "period": period,
            },
        )

    @staticmethod
    def _lowest_average_rating_agent(
        tickets: List[Ticket],
        query: TicketQuery,
    ) -> QueryResult:

        agent_ratings = {}

        for ticket in tickets:
            if (
                ticket.agent_id is not None
                and ticket.customer_rating is not None
            ):
                agent_ratings.setdefault(
                    ticket.agent_id,
                    [],
                ).append(ticket.customer_rating)

        if not agent_ratings:
            return QueryResult(
                operation=query.operation,
                answer="No agent ratings available.",
                data={
                    "lowest_agents": [],
                    "lowest_average_rating": None,
                    "agents": [],
                },
            )

        agent_averages = [
            {
                "agent_id": agent_id,
                "average_rating": round(
                    sum(ratings) / len(ratings),
                    2,
                ),
                "rated_tickets": len(ratings),
            }
            for agent_id, ratings in agent_ratings.items()
        ]

        agent_averages.sort(
            key=lambda item: (
                item["average_rating"],
                item["agent_id"],
            )
        )

        lowest_rating = agent_averages[0]["average_rating"]

        lowest_agents = [
            item["agent_id"]
            for item in agent_averages
            if item["average_rating"] == lowest_rating
        ]

        if len(lowest_agents) == 1:
            answer = (
                f"Agent {lowest_agents[0]} has the lowest "
                f"average rating: {lowest_rating:.2f}"
            )
        else:
            answer = (
                f"Agents {', '.join(lowest_agents)} have the lowest "
                f"average rating: {lowest_rating:.2f}"
            )

        return QueryResult(
            operation=query.operation,
            answer=answer,
            data={
                "lowest_agents": lowest_agents,
                "lowest_average_rating": lowest_rating,
                "agents": agent_averages,
            },
        )

    @staticmethod
    def _critical_unresolved(
        tickets: List[Ticket],
        query: TicketQuery,
    ) -> QueryResult:

        if query.max_resolution_hours is None:
            raise ValueError(
                "max_resolution_hours is required."
            )

        if not tickets:
            return QueryResult(
                operation=query.operation,
                answer="No tickets available.",
                data={
                    "count": 0,
                    "tickets": [],
                },
            )

        # Dataset-relative reference time for reproducibility.
        reference_time = max(
            ticket.created_at
            for ticket in tickets
        )

        cutoff_time = (
            reference_time
            - timedelta(
                hours=query.max_resolution_hours
            )
        )

        matching_tickets = [
            ticket
            for ticket in tickets
            if ticket.priority.lower() == "critical"
            and ticket.status.lower() != "resolved"
            and ticket.created_at <= cutoff_time
        ]

        return QueryResult(
            operation=query.operation,
            answer=(
                f"Critical unresolved tickets older than "
                f"{query.max_resolution_hours} hours: "
                f"{len(matching_tickets)}"
            ),
            data={
                "count": len(matching_tickets),
                "reference_time": reference_time.isoformat(),
                "cutoff_time": cutoff_time.isoformat(),
                "tickets": [
                    ticket.ticket_id
                    for ticket in matching_tickets
                ],
            },
        )

    @staticmethod
    def _resolution_time_anomaly(
        tickets: List[Ticket],
        query: TicketQuery,
    ) -> QueryResult:

        resolved_tickets = [
            ticket
            for ticket in tickets
            if ticket.status.lower() == "resolved"
            and ticket.resolution_time_hrs is not None
            and ticket.resolution_time_hrs >= 0
        ]

        if not resolved_tickets:
            return QueryResult(
                operation=query.operation,
                answer="No resolved tickets available.",
                data={
                    "count": 0,
                    "tickets": [],
                },
            )

        latest_date = max(
            ticket.created_at
            for ticket in resolved_tickets
        )

        week_start = (
            latest_date
            - timedelta(days=latest_date.weekday())
        ).replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )

        week_end = week_start + timedelta(days=7)

        weekly_tickets = [
            ticket
            for ticket in resolved_tickets
            if week_start
            <= ticket.created_at
            < week_end
        ]

        if len(weekly_tickets) < 4:
            return QueryResult(
                operation=query.operation,
                answer=(
                    "Not enough resolved tickets "
                    "in the latest dataset week."
                ),
                data={
                    "count": 0,
                    "week_start": week_start.isoformat(),
                    "week_end": week_end.isoformat(),
                    "tickets": [],
                },
            )

        resolution_times = [
            ticket.resolution_time_hrs
            for ticket in weekly_tickets
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
            threshold = median_time + (
                3 * median_deviation
            )

        anomalies = [
            ticket
            for ticket in weekly_tickets
            if ticket.resolution_time_hrs > threshold
        ]

        return QueryResult(
            operation=query.operation,
            answer=(
                f"Found {len(anomalies)} resolution-time "
                f"anomalies in the latest dataset week."
            ),
            data={
                "count": len(anomalies),
                "week_start": week_start.isoformat(),
                "week_end": week_end.isoformat(),
                "threshold_hrs": round(threshold, 2),
                "tickets": [
                    {
                        "ticket_id": ticket.ticket_id,
                        "resolution_time_hrs": (
                            ticket.resolution_time_hrs
                        ),
                    }
                    for ticket in anomalies
                ],
            },
        )