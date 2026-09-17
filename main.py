from fastapi import FastAPI

from app.presentation.api.anomalies import (
    router as anomaly_router,
)
from app.presentation.api.health import (
    router as health_router,
)
from app.presentation.api.query import (
    router as query_router,
)


app = FastAPI(
    title="Support Ticket AI",
    version="1.0.0",
    description="AI-powered support ticket analytics system",
)


app.include_router(health_router)
app.include_router(query_router)
app.include_router(anomaly_router)