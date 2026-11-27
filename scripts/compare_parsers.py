import csv
import html
import time
from pathlib import Path

import pymupdf
import pypdf
import trafilatura

RAW = Path("data/raw")
OUTPUT = Path("data/parser_comparison.csv")


def pymupdf_parse(path):
    with pymupdf.open(path) as doc:
        pages = [page.get_text() for page in doc]
    return len(pages), sum(len(text) for text in pages)


def pypdf_parse(path):
    reader = pypdf.PdfReader(path)
    pages = [page.extract_text() or "" for page in reader.pages]
    return len(pages), sum(len(text) for text in pages)


def trafilatura_parse(path):
    # Trafilatura extracts HTML, not PDF directly.
    # Convert PDF page text to HTML before extraction.
    with pymupdf.open(path) as doc:
        pages = [page.get_text() for page in doc]

    content = (
        "<html><body>" + "".join(f"<p>{html.escape(text)}</p>" for text in pages) + "</body></html>"
    )

    result = trafilatura.extract(content) or ""
    return len(pages), len(result)


def main():
    files = sorted(RAW.rglob("*.pdf"))[:5]

    if not files:
        raise SystemExit("No PDF files found under data/raw")

    parsers = {
        "pymupdf": pymupdf_parse,
        "pypdf": pypdf_parse,
        "trafilatura": trafilatura_parse,
    }

    rows = []

    for path in files:
        for name, parser in parsers.items():
            start = time.perf_counter()
            error = ""

            try:
                pages, chars = parser(path)
            except Exception as exc:
                pages, chars = 0, 0
                error = str(exc)

            elapsed = round(time.perf_counter() - start, 3)

            row = {
                "file": str(path),
                "parser": name,
                "pages": pages,
                "characters": chars,
                "seconds": elapsed,
                "error": error,
            }
            rows.append(row)
            print(row)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    with OUTPUT.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nSaved comparison to {OUTPUT}")


if __name__ == "__main__":
    main()
