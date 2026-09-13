from datetime import datetime, timezone
from fastapi import APIRouter, status
from pydantic import BaseModel, Field
from app.core.config import settings

router = APIRouter()


class HealthResponse(BaseModel):
    status: str = Field(default="healthy", description="Operational status of the service")
    service: str = Field(default="stanleaf-backend", description="Service identifier")
    version: str = Field(..., description="Application version")
    environment: str = Field(..., description="Execution environment")
    timestamp: str = Field(..., description="UTC ISO-8601 timestamp")


@router.get(
    "/health",
    response_model=HealthResponse,
    status_code=status.HTTP_200_OK,
    summary="Service Health Check",
    description="Returns operational health status and service metadata for Stanleaf backend.",
)
async def check_health() -> HealthResponse:
    return HealthResponse(
        status="healthy",
        service="stanleaf-backend",
        version=settings.VERSION,
        environment=settings.ENVIRONMENT,
        timestamp=datetime.now(timezone.utc).isoformat(),
    )
