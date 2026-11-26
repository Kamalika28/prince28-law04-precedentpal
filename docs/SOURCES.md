# Sources

## 1. AWS Open Data Registry – Indian Supreme Court Judgments

- **URL:** https://registry.opendata.aws/indian-supreme-court-judgments/
- **Provider:** Dattam Labs / AWS Open Data Registry
- **Data coverage:** 1950–2025 (project focus: 2000–2025)
- **Formats:** HTML dataset information page, JSON metadata, Parquet structured metadata, PDF judgments, and TAR archives for bulk downloads.
- **Storage:** Public Amazon S3 bucket in ap-south-1.
- **Access:** Public access; AWS credentials are not required.
- **License:** Creative Commons Attribution 4.0 International (CC BY 4.0).
- **Terms of use:** Reuse, redistribution and adaptation are permitted with appropriate attribution.
- **Project usage:** Primary source for collecting judgment documents and structured case metadata.

## 2. Supreme Court of India – Official Website

- **URL:** https://www.sci.gov.in/
- **Provider:** Supreme Court of India.
- **Formats:** HTML web pages and PDF documents.
- **Content:** Official court information, judgments, orders and legal resources.
- **Access:** Public website.
- **Terms of use:** Refer to the official website's Terms and Conditions and Copyright Policy. Acknowledge the source prominently when reproducing content. Third-party copyrighted material may require separate permission.
- **Project usage:** Secondary official source for verifying judgment details and legal information.

## Data Schema

The project aims to maintain the following fields for each judgment:

`id, case_name, citation, date, bench_size, judges, opinion_type, subject, cited_cases`

**Collection focus:** Indian Supreme Court judgments from 2000 to 2025.

**Attribution:** Indian Supreme Court Judgments dataset, Dattam Labs, AWS Open Data Registry, CC BY 4.0. Accessed November 23, 2026.

**Note:** Actual metadata availability will be checked during data collection. Fields not available directly may require extraction from judgment documents.
