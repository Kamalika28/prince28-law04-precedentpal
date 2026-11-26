from __future__ import annotations

import argparse
import csv
import math
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT / "data" / "raw"
DATASET_REPORT = ROOT / "DATASET.md"
CAPACITY_REPORT = ROOT / "docs" / "CAPACITY.md"
SOURCES_CSV = ROOT / "data" / "sources.csv"


def read_sources():
    source_files = [
        SOURCES_CSV,
        ROOT / "data" / "candidate_sources.csv",
        ROOT / "data" / "additional_sources.csv",
    ]
    sources = {}

    for source_file in source_files:
        if not source_file.exists():
            continue

        with source_file.open(encoding="utf-8-sig", newline="") as file:
            for row in csv.DictReader(file):
                url = row["url"].strip()
                if url:
                    sources[url] = row

    return list(sources.values())


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Generate dataset and capacity reports from collected PDFs."
    )
    parser.add_argument("--full-files", type=int, default=20000)
    parser.add_argument("--embed-usd", type=float, default=0.20)
    parser.add_argument("--dims", type=int, default=1024)
    parser.add_argument("--chunk-tokens", type=int, default=500)
    parser.add_argument("--usd-inr", type=float, default=95)

    args = parser.parse_args()

    if args.full_files <= 0:
        parser.error("--full-files must be greater than zero.")
    if args.embed_usd < 0:
        parser.error("--embed-usd cannot be negative.")
    if args.dims <= 0:
        parser.error("--dims must be greater than zero.")
    if args.chunk_tokens <= 0:
        parser.error("--chunk-tokens must be greater than zero.")
    if args.usd_inr <= 0:
        parser.error("--usd-inr must be greater than zero.")

    return args


def inspect_pdfs():
    pdfs = sorted(RAW_DIR.rglob("*.pdf"))

    processed = 0
    pages = 0
    characters = 0
    total_bytes = 0
    low_text = []
    failures = []

    for pdf in pdfs:
        try:
            with pymupdf.open(pdf) as document:
                file_pages = len(document)
                file_characters = sum(len(page.get_text()) for page in document)

            processed += 1
            pages += file_pages
            characters += file_characters
            total_bytes += pdf.stat().st_size

            if file_characters < 100:
                low_text.append(str(pdf.relative_to(ROOT)))

        except Exception as exc:
            failures.append(f"{pdf.name}: {type(exc).__name__}: {exc}")

    return (
        len(pdfs),
        processed,
        pages,
        characters,
        total_bytes,
        low_text,
        failures,
    )


def write_dataset_report(
    found,
    processed,
    pages,
    characters,
    total_bytes,
    current_tokens,
    projected_tokens,
    projected_chunks,
    args,
    low_text,
    failures,
):
    storage_mb = total_bytes / (1024**2)
    average_pages = pages / processed if processed else 0
    average_characters = characters / processed if processed else 0

    projected_storage_mb = storage_mb * args.full_files / processed
    sources = read_sources()
    source_rows = "\n".join(
        f"| [{row['source']}]({row['url']}) | {row['licence']} | {row['title']} |"
        for row in sources
    )

    report = f"""<!-- generated:start -->
# Dataset: PrecedentPal

A Supreme Court research assistant that finds precedents, separates majority
and dissent, and checks whether a judgment was later overruled.

## Collection targets

- Start target: 1,000 constitutional judgments from 2015–2025.
- Full target: 20,000+ judgments from 2000–2025.
- Current collection: {processed} processed PDFs. This is not yet a verified
  count of qualifying constitutional judgments.

## Sources and licences

| Source | Licence | Document |
|---|---|---|
{source_rows}

## Collection rules

- Respect robots.txt and applicable website terms.
- Maximum four concurrent requests.
- At least 0.5 seconds between requests to the same host.
- Each answer should link to the original judgment.
- No personal data is intentionally collected.

## Known gaps

- Downloaded PDF volume is measured separately from legal relevance.
- The current collection requires legal relevance and duplicate screening.
- The source list includes judgments outside the 2015–2025 start-target period.

## Collection summary

| Metric | Result |
|---|---:|
| PDF files found | {found:,} |
| PDFs processed successfully | {processed:,} |
| Total pages | {pages:,} |
| Extracted characters | {characters:,} |
| Current PDF storage | {storage_mb:.2f} MB |
| Estimated current tokens | {current_tokens:,} |
| Average pages per PDF | {average_pages:.1f} |
| Average characters per PDF | {average_characters:,.0f} |

## Collection progress

- Successfully processed PDFs: {processed:,}
- Projection target: {args.full_files:,}
- Working scope: 1,000 downloaded judgment PDFs, pending legal relevance screening.
- The 1,000-PDF collection target is reached only if 1,000 PDFs process successfully.
- Downloaded PDFs still require legal relevance and duplicate screening.
## Processing quality

- PDFs with very little extracted text: {len(low_text)}
- PDFs with processing errors: {len(failures)}
- Token estimates use approximately four characters per token.
- Token counts are estimates, not tokenizer measurements.

## Projected processing

| Metric | Current sample | Projection |
|---|---:|---:|
| Pages | {pages:,} | {pages * args.full_files / processed if processed else 0:,.0f} |
| Estimated tokens | {current_tokens:,} | {projected_tokens:,} |
| Chunks | {math.ceil(current_tokens / args.chunk_tokens):,} | {projected_chunks:,} |
| PDF storage | {storage_mb:.2f} MB | {projected_storage_mb:.2f} MB |

## Limitations

1. A downloaded PDF is not automatically a qualifying constitutional judgment.
2. The collection requires legal relevance screening and duplicate checks.
3. Text extraction success does not guarantee that every page is complete.
4. Projected figures are estimates based on the current sample.

## Low-text PDFs

"""

    if low_text:
        report += "\n".join(f"- `{name}`" for name in low_text)
    else:
        report += "None detected using the 100-character threshold."

    report += "\n\n## Processing errors\n\n"

    if failures:
        report += "\n".join(f"- {failure}" for failure in failures)
    else:
        report += "None."

    DATASET_REPORT.write_text(
        report + "\n\n<!-- generated:end -->\n",
        encoding="utf-8",
    )


def write_capacity_report(
    found,
    processed,
    pages,
    total_bytes,
    current_tokens,
    projected_tokens,
    projected_chunks,
    embedding_cost_inr,
    vector_storage_mb,
    projected_pdf_mb,
    args,
):
    current_chunks = math.ceil(current_tokens / args.chunk_tokens)

    report = f"""<!-- generated:start -->
# Capacity Planning Report

## Assumptions

| Parameter | Value |
|---|---:|
| Projection target | {args.full_files:,} PDFs |
| Embedding price | ${args.embed_usd:.2f} per million tokens |
| Embedding dimensions | {args.dims:,} |
| Chunk size | {args.chunk_tokens:,} tokens |
| USD to INR rate | INR {args.usd_inr:.2f} |

These are planning assumptions, not confirmed provider prices.

## Current sample

| Metric | Result |
|---|---:|
| PDFs found | {found:,} |
| PDFs processed | {processed:,} |
| Pages | {pages:,} |
| Estimated tokens | {current_tokens:,} |
| Estimated chunks | {current_chunks:,} |
| PDF storage | {total_bytes / (1024**2):.2f} MB |

## Projected full corpus

| Metric | Projection |
|---|---:|
| PDFs | {args.full_files:,} |
| Estimated tokens | {projected_tokens:,} |
| Estimated chunks | {projected_chunks:,} |
| PDF storage | {projected_pdf_mb:.2f} MB |
| Raw vector storage | {vector_storage_mb:.2f} MB |
| Embedding cost | INR {embedding_cost_inr:,.2f} |

## Calculation method

- Tokens are estimated as extracted characters divided by four.
- The projection scales the sample average by the target PDF count.
- Chunks are estimated using the configured chunk size.
- Vector storage assumes four bytes per dimension (float32).
- PDF storage uses the average size of the current sample.
- Chunk overlap is not included.

## Four engineering questions

1. **Is embedding cost a problem?**
   Estimated cost is INR {embedding_cost_inr:,.2f} for 20,000 PDFs
   using the assumed price of $0.20 per million tokens. This is an estimate,
   not a confirmed provider quote.

2. **Do vectors and text fit in free Postgres?**
   Raw vectors alone require {vector_storage_mb:.2f} MB.
   Extracted text and database overhead add more storage.
   Not yet verified: compare the combined requirement with the storage
   limit shown in the Postgres provider dashboard.

3. **Which estimate is least certain, and how can it be improved?**
   The token estimate is least certain because it uses characters divided
   by four. Measure actual token counts with the embedding provider's
   tokenizer on a representative sample, then update the projection.

4. **What changes if the corpus grows 10x?**
   Storage, embedding workload, and estimated embedding cost grow roughly
   10x if average document size stays similar.
   Use incremental batch processing, deduplication, and storage monitoring.
## Limitations

These are estimates, not measured production usage. They exclude
database indexes, metadata overhead, backups, network transfer,
and chunk overlap.
"""

    CAPACITY_REPORT.parent.mkdir(parents=True, exist_ok=True)
    CAPACITY_REPORT.write_text(
        report + "\n\n<!-- generated:end -->\n",
        encoding="utf-8",
    )


def main():
    args = parse_args()

    if not RAW_DIR.exists():
        raise SystemExit(f"PDF directory does not exist: {RAW_DIR}")

    (
        found,
        processed,
        pages,
        characters,
        total_bytes,
        low_text,
        failures,
    ) = inspect_pdfs()

    if processed == 0:
        raise SystemExit("No PDFs were successfully processed.")

    current_tokens = round(characters / 4)
    tokens_per_pdf = current_tokens / processed
    projected_tokens = round(tokens_per_pdf * args.full_files)

    projected_chunks = math.ceil(projected_tokens / args.chunk_tokens)

    embedding_cost_usd = (projected_tokens / 1_000_000) * args.embed_usd

    embedding_cost_inr = embedding_cost_usd * args.usd_inr

    vector_bytes = projected_chunks * args.dims * 4
    vector_storage_mb = vector_bytes / (1024**2)

    average_pdf_bytes = total_bytes / processed
    projected_pdf_mb = (average_pdf_bytes * args.full_files) / (1024**2)

    write_dataset_report(
        found,
        processed,
        pages,
        characters,
        total_bytes,
        current_tokens,
        projected_tokens,
        projected_chunks,
        args,
        low_text,
        failures,
    )

    write_capacity_report(
        found,
        processed,
        pages,
        total_bytes,
        current_tokens,
        projected_tokens,
        projected_chunks,
        embedding_cost_inr,
        vector_storage_mb,
        projected_pdf_mb,
        args,
    )

    print(f"files={found} pages={pages}")
    print(f"characters={characters:,}")
    print(f"tokens_per_page={current_tokens / pages:.1f}")
    print(f"projected_tokens={projected_tokens:,}")
    print(f"projected_chunks={projected_chunks:,}")
    print(f"embedding_cost=Rs {embedding_cost_inr:,.2f}")
    print(f"vectors={vector_storage_mb:.2f} MB")
    print(f"pdf_storage={total_bytes / (1024**2):.2f} MB")
    print(f"low_text={len(low_text)} errors={len(failures)}")
    print("Wrote DATASET.md and docs/CAPACITY.md")


if __name__ == "__main__":
    main()
