"""Read-only judgment search endpoints."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Query

from precedentpal.api.deps import get_store
from precedentpal.store import RecordStore

router = APIRouter(prefix="/v1/documents", tags=["documents"])


@router.get("")
def list_documents(
    store: Annotated[RecordStore, Depends(get_store)],
    q: Annotated[str | None, Query(max_length=200)] = None,
    limit: Annotated[int, Query(ge=1, le=100)] = 20,
    offset: Annotated[int, Query(ge=0)] = 0,
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
    document_id: str,
    store: Annotated[RecordStore, Depends(get_store)],
) -> dict[str, Any]:
    record = store.get(document_id)
    if record is None:
        raise HTTPException(
            status_code=404, detail=f"No document with id '{document_id}'."
        )
    return record
