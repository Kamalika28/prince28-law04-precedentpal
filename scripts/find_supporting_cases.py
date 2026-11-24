import io

import pandas as pd
import requests

cases = {
    1950: ["ROMESH THAPPAR", "BRIJ BHUSHAN"],
    1952: ["V.G. ROW", "STATE OF MADRAS"],
}

base = "https://indian-supreme-court-judgments.s3.ap-south-1.amazonaws.com/metadata/parquet/year={}/metadata.parquet"

for year, terms in cases.items():
    response = requests.get(base.format(year))
    response.raise_for_status()
    df = pd.read_parquet(io.BytesIO(response.content))

    print(f"\n===== {year} =====")
    for term in terms:
        matches = df[df["title"].str.contains(term, case=False, na=False)]
        print(f"\nSearch: {term}")
        print(matches[["title", "citation", "decision_date", "path"]].to_string(index=False))
