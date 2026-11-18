# PrecedentPal

A Supreme Court research assistant that finds precedents, separates majority and dissent, and checks whether a judgment was later overruled.

**Status:** Day 1 foundation (FastAPI skeleton, quality gates). Live URL from Day 5.

## Who it's for

Third-year law student on a Chennai law college moot court team researching constitutional and criminal precedents.

## The problem

Indian Supreme Court judgments can run to hundreds of pages and may contain multiple opinions. During moot-court research, students need to distinguish a binding majority holding from a separate or dissenting opinion. They also need to check how later benches treated a precedent instead of relying on an isolated quotation. Manually tracing those relationships across many judgments is slow and makes it easy to miss important qualifications.

## Data sources

Indian Supreme Court judgments 1950-2025 from the AWS Open Data registry (JSON + Parquet metadata), focused on 2000-2025.

- https://registry.opendata.aws/indian-supreme-court-judgments/
- https://www.sci.gov.in/
- Terms: Dataset licensed CC BY 4.0 (verify the dataset's current licence and attribution requirements before redistribution).

## Hardest problem (my interview story)

Long judgments with multiple opinions and citations: answers must say which opinion a passage comes from, and must check later judgments that cite the case to see if it was overruled.

## Signature feature

Citation graph: for any judgment, see which cases it relies on and which later cases followed, distinguished or overruled it.

## Target metric

Opinion attribution correct for 95%+ of 40 quotes; overruled status correct for 90%+ of 30 cases.

## Run it locally

```bash
uv sync
cp .env.example .env   # Windows: copy .env.example .env
uv run uvicorn precedentpal.api.main:create_app --factory --reload
```

Then open http://localhost:8000/docs

## Checks

```bash
uv run pytest
uv run ruff check .
```
