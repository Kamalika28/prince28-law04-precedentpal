import re
from pathlib import Path

import pandas as pd
from bs4 import BeautifulSoup

YEARS = [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025]
TERMS = [
    # Constitutional doctrines
    "constitution of india",
    "constitutional validity",
    "constitutional amendment",
    "constitutional interpretation",
    "constitutional bench",
    "basic structure",
    "basic features",
    "fundamental rights",
    "fundamental right",
    "directive principles",
    "judicial review",
    "separation of powers",
    "federalism",
    "secularism",
    "rule of law",
    "constitutional morality",
    "constitutional scheme",
    "constitutional mandate",
    "scheduled caste status",
    "scheduled tribes status",
    "caste certificate",
    "constitutional protection",
    "good samaritan",
    "constitutional rights",
    # Fundamental rights and liberties
    "right to privacy",
    "right to life",
    "right to equality",
    "freedom of speech",
    "freedom of religion",
    "equality before law",
    "equal protection of laws",
    "reservation",
    "untouchability",
    "minority rights",
    "religious freedom",
    # Articles of the Constitution
    "article 12",
    "article 13",
    "article 14",
    "article 15",
    "article 16",
    "article 17",
    "article 18",
    "article 19",
    "article 20",
    "article 21",
    "article 21a",
    "article 22",
    "article 23",
    "article 24",
    "article 25",
    "article 26",
    "article 27",
    "article 28",
    "article 29",
    "article 30",
    "article 31a",
    "article 31b",
    "article 31c",
    "article 32",
    "article 39a",
    "article 44",
    "article 48a",
    "article 72",
    "article 74",
    "article 123",
    "article 124",
    "article 136",
    "article 141",
    "article 142",
    "article 143",
    "article 148",
    "article 161",
    "article 163",
    "article 200",
    "article 213",
    "article 226",
    "article 227",
    "article 239",
    "article 243",
    "article 246",
    "article 254",
    "article 262",
    "article 280",
    "article 300a",
    "article 311",
    "article 324",
    "article 326",
    "article 329",
    "article 338",
    "article 342",
    "article 356",
    "article 361",
    "article 363",
    "article 368",
    # Constitutional institutions and governance
    "election commission",
    "governor's powers",
    "powers of the governor",
    "legislative competence",
    "ordinance making power",
    "parliamentary privileges",
    "anti-defection",
    "ninth schedule",
    "presidential reference",
]


def clean_html(value):
    soup = BeautifulSoup(value or "", "html.parser")

    for element in soup.select("script, style, select, .modal"):
        element.decompose()

    text = soup.get_text(" ", strip=True).lower()

    # Normalize common Constitution article formats.
    text = re.sub(
        r"\barts?\.?\s*(\d+[a-z]?)",
        r"article \1",
        text,
    )

    return text


def main():
    frames = []

    for year in YEARS:
        path = Path.home() / "AppData" / "Local" / "Temp" / f"metadata-{year}.parquet"
        if not path.exists():
            print(f"Missing metadata: {path}")
            continue

        df = pd.read_parquet(path)
        df["source_year"] = year
        frames.append(df)

    if not frames:
        raise SystemExit("No metadata files found.")

    df = pd.concat(frames, ignore_index=True)
    df["search_text"] = (
        df["title"].fillna("").astype(str) + " " + df["raw_html"].fillna("").map(clean_html)
    )

    results = []

    for row in df.itertuples():
        text = row.search_text
        matches = [
            term
            for term in TERMS
            if re.search(
                r"(?<![a-z0-9])" + re.escape(term) + r"(?![a-z0-9])",
                text,
            )
        ]

        if matches:
            results.append(
                {
                    "title": row.title,
                    "year": row.source_year,
                    "decision_date": row.decision_date,
                    "citation": row.citation,
                    "case_id": row.case_id,
                    "path": row.path,
                    "score": len(matches),
                    "matched_terms": "; ".join(matches),
                    "review_status": "needs_manual_review",
                }
            )

    output = pd.DataFrame(results)

    if not output.empty:
        before = len(output)
        output = output.drop_duplicates(subset=["path"], keep="first")
        print(f"Duplicate paths removed: {before - len(output)}")
        output = output.sort_values(["score", "year"], ascending=[False, True])
    destination = Path("data") / "constitutional_candidates_2015_2025.csv"
    destination.parent.mkdir(parents=True, exist_ok=True)
    output.to_csv(destination, index=False, encoding="utf-8-sig")

    print(f"Metadata records: {len(df)}")
    print(f"Candidate records: {len(output)}")
    print(f"Saved: {destination}")
    print("\nTop 15 candidates:")
    print(output[["year", "title", "score", "matched_terms"]].head(15).to_string(index=False))


if __name__ == "__main__":
    main()
