from typing import Any, Dict, List

from pydantic import BaseModel


class AnomalyResponse(BaseModel):
    ticket_id: str
    reason: str
    severity: str
    details: Dict[str, Any]


class AnomalyDetectionResponse(BaseModel):
    total_anomalies: int
    anomalies: List[AnomalyResponse]