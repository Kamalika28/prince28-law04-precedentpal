<!-- generated:start -->
# Capacity Planning Report

## Assumptions

| Parameter | Value |
|---|---:|
| Projection target | 20,000 PDFs |
| Embedding price | $0.20 per million tokens |
| Embedding dimensions | 1,024 |
| Chunk size | 500 tokens |
| USD to INR rate | INR 95.00 |

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
| Embedding cost | INR 19,232.91 |

## Calculation method

- Tokens are estimated as extracted characters divided by four.
- The projection scales the sample average by the target PDF count.
- Chunks are estimated using the configured chunk size.
- Vector storage assumes four bytes per dimension (float32).
- PDF storage uses the average size of the current sample.
- Chunk overlap is not included.

## Four engineering questions

1. **Is embedding cost a problem?**
   Estimated cost is INR 19,232.91 for 20,000 PDFs
   using the assumed price of $0.20 per million tokens. This is an estimate,
   not a confirmed provider quote.

2. **Do vectors and text fit in free Postgres?**
   Raw vectors alone require 7908.27 MB.
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


<!-- generated:end -->
