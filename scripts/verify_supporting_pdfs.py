import requests

base = "https://indian-supreme-court-judgments.s3.ap-south-1.amazonaws.com/data/pdf/year={}/english/{}_EN.pdf"

cases = [
    (1950, "1950_1_594_605", "Romesh Thappar"),
    (1950, "1950_1_605_620", "Brij Bhushan"),
    (1952, "1952_1_597_611", "State of Madras v V.G. Row"),
]

for year, path, name in cases:
    url = base.format(year, path)
    response = requests.head(url, timeout=30)
    print(f"{response.status_code} | {name} | {url}")
