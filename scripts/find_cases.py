import io

import pandas as pd
import requests

cases = {
    1973: "KESAVANANDA",
    1977: "BALCHAND",
    2015: "SHREYA SINGHAL",
    2018: "PUTTASWAMY",
    2020: "ANURADHA BHASIN",
    2022: "SATENDER KUMAR ANTIL",
}

base_url = "https://indian-supreme-court-judgments.s3.ap-south-1.amazonaws.com/metadata/parquet/year={}/metadata.parquet"

for year, search_term in cases.items():
    print(f"\n===== YEAR {year}: {search_term} =====")

    response = requests.get(base_url.format(year))
    response.raise_for_status()

    df = pd.read_parquet(io.BytesIO(response.content))

    matches = df[df["title"].str.contains(search_term, case=False, na=False)]

    if matches.empty:
        print("No matching cases found.")
    else:
        print(
            matches[["title", "citation", "decision_date", "case_id", "path"]].to_string(
                index=False
            )
        )
