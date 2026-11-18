"""Shared dependencies for API routes."""

from fastapi import Request

from precedentpal.store import RecordStore


def get_store(request: Request) -> RecordStore:
    return request.app.state.store
