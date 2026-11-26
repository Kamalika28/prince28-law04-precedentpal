import requests

base = "https://indian-supreme-court-judgments.s3.ap-south-1.amazonaws.com/data/pdf/year={}/english/{}_EN.pdf"

cases = [
    (1973, "S_1973_1_1_1002", "Kesavananda Bharati"),
    (1977, "1978_1_535_536", "State of Rajasthan v Balchand"),
    (2015, "2015_5_963_1074", "Shreya Singhal"),
    (2017, "2017_10_569_999", "Puttaswamy (Privacy)"),
    (2018, "2018_8_1_1076", "Puttaswamy (Aadhaar)"),
    (2020, "2020_1_812_908", "Anuradha Bhasin"),
    (2022, "2022_10_351_447", "Satender Kumar Antil"),
]

for year, path, name in cases:
    url = base.format(year, path)
    try:
        response = requests.head(url, timeout=30)
        print(f"{response.status_code} | {name} | {url}")
    except requests.RequestException as error:
        print(f"ERROR | {name} | {error}")
