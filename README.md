# PrecedentPal

A Supreme Court research assistant that finds precedents, separates majority and dissent, and checks whether a judgment was later overruled.

**Status:** Day 1 foundation (FastAPI skeleton, quality gates). Live URL from Day 5.

## Who it's for

Third-year law student on a Chennai law college moot court team researching constitutional and criminal precedents.

## The problem

Supreme Court judgments are often hundreds of pages long and may contain multiple opinions from different judges. While researching cases, students can struggle to distinguish the majority opinion from dissenting opinions. They may also rely on a judgment without realizing that a later court decision has overruled or questioned it. This makes legal research time-consuming and increases the risk of using incorrect or outdated precedents.

## Data sources

Indian Supreme Court judgments 1950-2025 from the AWS Open Data registry (JSON + Parquet metadata), focused on 2000-2025.

- https://registry.opendata.aws/indian-supreme-court-judgments/
- https://www.sci.gov.in/
- Terms: Dataset licensed CC BY 4.0.

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
