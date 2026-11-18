# PrecedentPal requirements

## Functional requirements

1. **List judgments:** `GET /v1/documents` returns at most 100 records per request and supports offset pagination.
2. **Search judgments:** `GET /v1/documents?q=...` performs case-insensitive matching across indexed text fields and returns the total number of matches.
3. **Retrieve one judgment:** `GET /v1/documents/{id}` returns the matching record or an RFC 9457-style 404 response.
4. **Readiness:** `GET /ready` reports whether the configured records file loaded successfully; return HTTP 503 when it did not.
5. **Trace requests:** Every HTTP response includes an `X-Request-ID`; every request log event includes the same identifier.

## Non-functional requirements

1. **Latency:** For a local corpus of 1,000 records, p95 list/search response time should be below 500 ms on the development laptop.
2. **Pagination safety:** A request must never return more than 100 records, regardless of client input.
3. **Reliability:** The initial API test suite must contain at least 6 automated tests and pass with `uv run pytest`.
4. **Code quality:** `uv run ruff check .` must pass before a change is accepted.
5. **Secret hygiene:** `.env` and raw datasets must be excluded from Git; pre-commit secret scanning must run on every local commit.
