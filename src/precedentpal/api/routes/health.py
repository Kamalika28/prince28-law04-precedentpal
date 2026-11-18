"""Liveness and readiness endpoints."""

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse

router = APIRouter(tags=["health"])


@router.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/ready")
def ready(request: Request) -> JSONResponse | dict:
    store = request.app.state.store
    payload = {
        "status": "ready" if store.loaded else "not_ready",
        "checks": {"records_loaded": store.loaded},
        "records_count": len(store.records),
    }
    if not store.loaded:
        return JSONResponse(payload, status_code=503)
    return payload
