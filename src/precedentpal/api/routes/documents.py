"""Read-only judgment search endpoints."""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query

from precedentpal.api.deps import get_store
from precedentpal.store import RecordStore

router = APIRouter(prefix="/v1/documents", tags=["documents"])


@router.get("")
def list_documents(
    q: str | None = Query(default=None, max_length=200),
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    store: RecordStore = Depends(get_store),
) -> dict[str, Any]:
    matches = store.list(q)
    return {
        "total": len(matches),
        "limit": limit,
        "offset": offset,
        "items": matches[offset : offset + limit],
    }


@router.get("/{document_id}")
def get_document(
    document_id: str, store: RecordStore = Depends(get_store)
) -> dict[str, Any]:
    record = store.get(document_id)
    if record is None:
        raise HTTPException(
            status_code=404, detail=f"No document with id '{document_id}'."
        )
    return record
