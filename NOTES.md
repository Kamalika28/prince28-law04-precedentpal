
# Engineering notes: PrecedentPal

## D03 - PostgreSQL

### Migrations (upgrade, downgrade, upgrade)

**1. Downgrade by one migration**

```powershell
uv run alembic downgrade -1
```

Output:
```text
INFO  [alembic.runtime.migration] Running downgrade <new_revision> -> <previous_revision>
```

**2. Check current migration**

```powershell
uv run alembic current
```

Output:
```text
<previous_revision>
```

**3. Upgrade to the latest migration**

```powershell
uv run alembic upgrade head
```

Output:
```text
INFO  [alembic.runtime.migration] Running upgrade <previous_revision> -> <new_revision>
```

**4. View migration history**

```powershell
uv run alembic history
```

Output:
```text
<previous_revision> -> <new_revision> (head), <migration_description>
<base> -> <previous_revision>, <initial_migration_description>
```

### The loader is idempotent

**Run 1 - Initial load**

```text
records=20 inserted=20 updated=0 unchanged=0
```

All 20 records were inserted into the database.

**Run 2 - Run again without changes**

```text
records=20 inserted=0 updated=0 unchanged=20
```

No duplicate records were created. All 20 records remained unchanged.

**Run 3 - After editing one record**

```text
records=20 inserted=0 updated=1 unchanged=19
```

One modified record was updated, while the remaining 19 records stayed unchanged.

**Additional verification - Run again**

```text
records=20 inserted=0 updated=0 unchanged=20
```

The database was already up to date.

**Conclusion:** The loader is idempotent because running it repeatedly does not create duplicates, and it updates only modified records.

### EXPLAIN for ?case_name=VALUE

Command:

```powershell
uv run python scripts/explain.py case_name "Justice K.S. Puttaswamy (Retd.) v. Union of India"
```

**1. What the planner chooses on its own:**

```text
Seq Scan on documents  (cost=0.00..11.00 rows=1 width=36) (actual time=1.100..4.859 rows=1.00 loops=1)
  Filter: (metadata @> '{"case_name": "Justice K.S. Puttaswamy (Retd.) v. Union of India"}'::jsonb)
  Rows Removed by Filter: 19
  Buffers: shared hit=22 read=7 dirtied=4
Planning:
  Buffers: shared hit=143 read=8 dirtied=1
Planning Time: 9.816 ms
Execution Time: 4.890 ms
```

**2. Seq scan switched off, to prove the index can be used:**

```text
Bitmap Heap Scan on documents  (cost=12.81..16.82 rows=1 width=36) (actual time=1.557..1.558 rows=1.00 loops=1)
  Recheck Cond: (metadata @> '{"case_name": "Justice K.S. Puttaswamy (Retd.) v. Union of India"}'::jsonb)
  Heap Blocks: exact=1
  Buffers: shared hit=2 read=2
  ->  Bitmap Index Scan on ix_documents_metadata_gin  (cost=0.00..12.81 rows=1 width=0) (actual time=1.518..1.519 rows=1.00 loops=1)
        Index Cond: (metadata @> '{"case_name": "Justice K.S. Puttaswamy (Retd.) v. Union of India"}'::jsonb)
        Index Searches: 1
        Buffers: shared hit=1 read=2
Planning:
  Buffers: shared hit=1
Planning Time: 0.082 ms
Execution Time: 1.602 ms
```

**Why did the planner choose a Seq Scan on my table? (2 lines, your own words)**

My table contains only 20 records, so PostgreSQL estimates that scanning the entire table is cheaper than using the index. A sequential scan has less overhead for a small table.

**When would it switch to the GIN index? (1 line)**

It may choose the GIN index when the table becomes larger and the query is selective enough to make index access more efficient.

## D04 - Docker, Compose and tests

### The image

```text
paste the output of: docker images precedentpal:dev
paste the output of: docker run --rm precedentpal:dev id
```

- Size: ___ MB (target: under 400 MB)
- First build: ___ s. After changing one line of code: ___ s.
- Which step said CACHED, and why? (1 line, your own words)

### The stack

```text
paste the output of: docker compose ps -a
paste the last line of: docker compose logs migrate (first up, then after down + up)
```

### Breaking the database on purpose

```text
db stopped: /health -> paste
db stopped: /ready -> paste
db started: /ready -> paste
```

Why should a load balancer stop sending traffic here but not restart the app? (2 lines)

### Tests and coverage

```text
uv run poe test              -> paste the last line
uv run poe test-integration  -> paste the last line
coverage TOTAL, unit only    -> paste
coverage TOTAL, with integration tests -> paste
```

Two files or lines my coverage report says are never run, and whether they matter: (2 lines)

## D05 - CI/CD and going live

- Live URL: https://precedentpal.onrender.com
- CI run for pull request 1: https://github.com/Kamalika28/prince28-law04-precedentpal/actions/runs/44703306312
- First deploy that ran by itself: https://github.com/Kamalika28/prince28-law04-precedentpal/actions/runs/44768490762
- Merge clicked at 9:26 PM -> "Smoke test passed" at 9:38 PM -> lead time: 12 min

### Smoke test output from that CD run

```text
ok   /health -> 200, version a545be3d9d91115e956a4908492532f69afee2f3
ok   /ready -> 200 {'status': 'ready', 'checks': {'database': True}}
ok   /v1/documents?limit=1 -> 200
```

### Rollback drill

- Rolled back to sha 59138c68c137192ff9af218cfa09aa12c83f6512: started __:__, smoke passed __:__ (___ min)
- Rolled forward to sha a545be3d9d91115e956a4908492532f69afee2f3: ___ min
- During the rollback, the database stayed on the newer schema. Why is that safe here? (2 lines)

### Where my secrets live

- Neon string: GitHub Secret DATABASE_URL + Render environment. Not in Git, not in the image.
- Render deploy hook: GitHub Secret RENDER_DEPLOY_HOOK only.

### Monitoring

- UptimeRobot checks /health every 5 minutes; alerts go to my email.
- One thing that would make my live app faster on its first request: (1 line)

## D06 · Collecting the corpus

### Downloader commands

The downloader supports four collection methods:

- `urls` - downloads URLs listed in `data/sources.csv`.
- `repo` - collects files from a Git repository.
- `sitemap` - discovers URLs from a sitemap and adds them to the source list.
- `manual` - registers files already downloaded into the local dataset.

Main downloader command:

```powershell
uv run python scripts/fetch.py urls
```

Default URL-download settings:

- Maximum concurrency: 4
- Minimum per-host delay: 0.5 seconds
- User-Agent: `examate-student-bot`
- Source metadata includes the source name and licence.

### Reliability and safety

- Normal URL downloads check `robots.txt` before fetching source files.
- If robots rules cannot be safely retrieved, the downloader blocks that origin.
- Retryable HTTP responses include 408, 425, 429, 500, 502, 503 and 504.
- Retries use backoff and respect `Retry-After` where available.
- Completed files are skipped when the same command is run again.
- Downloads use temporary `.part` files and rename completed files into place.
- Interrupted or failed partial files are removed. A retry starts that URL again rather than resuming its byte range.
- Download outcomes are recorded in `data/manifest.jsonl`.

**Known limitation:** Sitemap retrieval currently does not use the same robots.txt check as the normal URL downloader. This should be addressed before relying on sitemap discovery as a fully robots-compliant collection path.

### Tests

Downloader tests:

```powershell
uv run pytest tests/test_fetch.py -v
```

Result: 20 passed.

Full test suite:

```powershell
uv run poe test
```

Result: 22 passed, 7 skipped.

The three-run test verifies that:

1. A failed URL can be retried while a completed file is skipped.
2. A subsequent run skips both completed files.
3. No additional downloads occur once both files are complete.

**Test limitation:** This is a simulated retry-and-skip test. It is not proof of recovery after killing a live download process.
### Sources and licence checks

| Source | Licence recorded in sources.csv | Verification |
|---|---|---|
| AWS Open Data Registry – Indian Supreme Court Judgments | CC BY 4.0 | Licence metadata recorded; verify applicable dataset terms before redistribution |
| Supreme Court of India | Not established for this collection | Official website identified as a reference source; no licence assumed |

Source references:
- https://registry.opendata.aws/indian-supreme-court-judgments/
- https://www.sci.gov.in/

Original judgment URLs are retained in `data/sources.csv`.
### Dataset status
#### Collection outcome

- Successfully processed: 55 PDFs.
- Total pages: 4,692.
- Extraction failures: 0.
- Low-text PDFs flagged: 0.
- Start target: 1,000 constitutional judgments (2015–2025) — not yet met.
- Full target: 20,000+ judgments (2000–2025) — not yet met.
- The current collection includes older judgments and has not been fully screened for constitutional relevance or duplicates.
- A live process-kill and resume test has not been completed; the automated tests simulate retry and skip behaviour.

At the time of this report:

- PDFs found: 55
- PDFs processed successfully: 55
- Pages processed: 4,692
- Extracted characters: 11,134,842
- Estimated tokens: 2,783,710
- PDF storage: 81.84 MB

The 1,000-judgment target has not yet been reached. Downloaded PDFs still require legal relevance screening and duplicate checks.

### Capacity estimate

The capacity report uses a projection of:

- 20,000 PDFs
- 500-token chunks
- 1,024 vector dimensions
- Embedding price assumption: USD 0.20 per million tokens
- Exchange-rate assumption: INR 95 per USD

These are estimates based on the current sample, not measured full-dataset costs. Actual storage and processing requirements may differ.
