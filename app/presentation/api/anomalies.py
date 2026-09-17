from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException

from app.application.use_cases.ingest_tickets import (
    IngestTicketsUseCase,
)
from app.domain.services.anomaly_service import (
    AnomalyService,
)
from app.infrastructure.repositories.csv_ticket_repository import (
    CsvTicketRepository,
)
from app.presentation.schemas.anomaly_schema import (
    AnomalyDetectionResponse,
    AnomalyResponse,
)


router = APIRouter(
    prefix="/api",
    tags=["Anomalies"],
)


def build_anomaly_service() -> AnomalyService:
    return AnomalyService()


@router.get(
    "/anomalies",
    response_model=AnomalyDetectionResponse,
)
def detect_anomalies(
    reference_time: Optional[datetime] = None,
):
    try:
        repository = CsvTicketRepository(
            "data/support_tickets.csv"
        )

        ingestion_use_case = IngestTicketsUseCase(
            repository
        )

        tickets = ingestion_use_case.execute()

        anomaly_service = build_anomaly_service()

        anomalies = anomaly_service.detect_all(
            tickets=tickets,
            reference_time=reference_time,
        )

        anomaly_responses = [
            AnomalyResponse(
                ticket_id=anomaly.ticket_id,
                reason=anomaly.reason,
                severity=anomaly.severity,
                details=anomaly.details,
            )
            for anomaly in anomalies
        ]

        return AnomalyDetectionResponse(
            total_anomalies=len(anomaly_responses),
            anomalies=anomaly_responses,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unexpected error during anomaly detection",
        ) from exc