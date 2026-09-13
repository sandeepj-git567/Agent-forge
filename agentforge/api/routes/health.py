"""
Health and Readiness Check Router
"""
from fastapi import APIRouter

from agentforge.api.schemas import HealthResponse, ReadinessResponse
from agentforge.config.settings import settings
from agentforge.tools.registry import default_tool_registry

router = APIRouter(tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def get_health() -> HealthResponse:
    """Check basic application health."""
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        environment=settings.APP_ENV
    )


@router.get("/health/ready", response_model=ReadinessResponse)
async def get_readiness() -> ReadinessResponse:
    """Check application readiness including tool registry and ADK configuration status."""
    adk_status = "configured" if settings.is_api_key_configured else "offline_fallback"
    tools_count = len(default_tool_registry.list_tools())

    return ReadinessResponse(
        status="ready",
        services={
            "adk_runtime": adk_status,
            "tools_registry": f"{tools_count}_tools_loaded",
            "guardrails": "active"
        }
    )
