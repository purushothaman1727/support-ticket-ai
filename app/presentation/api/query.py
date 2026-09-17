from fastapi import APIRouter, HTTPException

from app.application.use_cases.ingest_tickets import (
    IngestTicketsUseCase,
)
from app.application.use_cases.llm_query_tickets import (
    LLMQueryTicketsUseCase,
)
from app.domain.services.ticket_query_service import (
    TicketQueryService,
)
from app.infrastructure.config import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT,
)
from app.infrastructure.llm.ollama_client import OllamaClient
from app.infrastructure.repositories.csv_ticket_repository import (
    CsvTicketRepository,
)
from app.presentation.schemas.query_schema import (
    NaturalLanguageQueryRequest,
    NaturalLanguageQueryResponse,
)


router = APIRouter(
    prefix="/api",
    tags=["Query"],
)


def build_llm_query_use_case():
    repository = CsvTicketRepository(
        "data/support_tickets.csv"
    )

    ingestion_use_case = IngestTicketsUseCase(
        repository
    )

    query_service = TicketQueryService()

    llm_provider = OllamaClient(
        base_url=OLLAMA_BASE_URL,
        model=OLLAMA_MODEL,
        timeout=OLLAMA_TIMEOUT,
    )

    query_use_case = LLMQueryTicketsUseCase(
        llm_provider=llm_provider,
        query_service=query_service,
    )

    return query_use_case, ingestion_use_case


@router.post(
    "/query",
    response_model=NaturalLanguageQueryResponse,
)
def query_tickets(
    request: NaturalLanguageQueryRequest,
):
    try:
        query_use_case, ingestion_use_case = (
            build_llm_query_use_case()
        )

        tickets = ingestion_use_case.execute()

        result = query_use_case.execute(
            tickets=tickets,
            question=request.question,
        )

        return NaturalLanguageQueryResponse(
            operation=result.operation,
            answer=result.answer,
            data=result.data,
        )

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except RuntimeError as exc:
        raise HTTPException(
            status_code=502,
            detail=str(exc),
        ) from exc

    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unexpected error while processing query",
        ) from exc