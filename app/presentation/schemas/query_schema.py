from typing import Any, Dict

from pydantic import BaseModel, Field


class NaturalLanguageQueryRequest(BaseModel):
    question: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Natural language question",
    )


class NaturalLanguageQueryResponse(BaseModel):
    operation: str
    answer: str
    data: Dict[str, Any]