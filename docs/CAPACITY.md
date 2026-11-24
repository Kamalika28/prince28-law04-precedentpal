# Capacity Planning Report

## Assumptions

| Parameter | Value |
|---|---:|
| Projection target | 20,000 PDFs |
| Embedding price | $0.20 per million tokens |
| Embedding dimensions | 1,024 |
| Chunk size | 500 tokens |
| USD to INR rate | Ã¢â€šÂ¹95.00 |

These are planning assumptions, not confirmed provider prices.

## Current sample

| Metric | Result |
|---|---:|
| PDFs found | 55 |
| PDFs processed | 55 |
| Pages | 4,692 |
| Estimated tokens | 2,783,710 |
| Estimated chunks | 5,568 |
| PDF storage | 81.84 MB |

## Projected full corpus

| Metric | Projection |
|---|---:|
| PDFs | 20,000 |
| Estimated tokens | 1,012,258,182 |
| Estimated chunks | 2,024,517 |
| PDF storage | 29760.69 MB |
| Raw vector storage | 7908.27 MB |
| Embedding cost | Ã¢â€šÂ¹19,232.91 |

## Calculation method

- Tokens are estimated as extracted characters divided by four.
- The projection scales the sample average by the target PDF count.
- Chunks are estimated using the configured chunk size.
- Vector storage assumes four bytes per dimension (float32).
- PDF storage uses the average size of the current sample.
- Chunk overlap is not included.

## Four engineering conclusions

1. **Collection scale:** The current sample contains 55
   processed PDFs. It is not yet 1,000 verified constitutional judgments.

2. **Embedding budget:** The estimated cost is Ã¢â€šÂ¹19,232.91
   under the selected price and exchange-rate assumptions. Confirm actual
   provider pricing before running a full embedding job.

3. **Vector capacity:** Raw vectors require approximately
   7908.27 MB. Database indexes, metadata, and backups
   will increase actual storage requirements.

4. **Scaling strategy:** Complete legal relevance screening, remove
   duplicates, validate extraction quality, and test a smaller batch
   before embedding the full collection.

## Limitations

These are estimates, not measured production usage. They exclude
database indexes, metadata overhead, backups, network transfer,
and chunk overlap.
