from typing import Literal, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


class LLMQueryIntent(BaseModel):
    model_config = ConfigDict(extra="forbid")

    operation: Literal[
        "count",
        "average_rating",
        "top_resolved_agent",
        "critical_unresolved",
        "resolution_time_anomaly",
        "lowest_average_rating_agent",
        "top_resolved_agent_this_month"
    ]

    status: Optional[
        Literal["Open", "Resolved", "Escalated"]
    ] = None

    category: Optional[
        Literal["Billing", "Technical", "General"]
    ] = None

    priority: Optional[
        Literal["Low", "Medium", "High", "Critical"]
    ] = None

    agent_id: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=100,
    )

    max_resolution_hours: Optional[float] = Field(
        default=None,
        gt=0,
        le=10000,
    )

    @field_validator("agent_id")
    @classmethod
    def validate_agent_id(cls, value: Optional[str]):
        if value is not None and not value.strip():
            raise ValueError("agent_id cannot be empty")

        return value.strip() if value else value