
# Engineering notes: PrecedentPal

## D03 · PostgreSQL

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

**Run 1 – Initial load**

```text
records=20 inserted=20 updated=0 unchanged=0
```

All 20 records were inserted into the database.

**Run 2 – Run again without changes**

```text
records=20 inserted=0 updated=0 unchanged=20
```

No duplicate records were created. All 20 records remained unchanged.

**Run 3 – After editing one record**

```text
records=20 inserted=0 updated=1 unchanged=19
```

One modified record was updated, while the remaining 19 records stayed unchanged.

**Additional verification – Run again**

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

## D04 · Docker, Compose and tests

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
paste the last line of: docker compose logs migrate   (first up, then after down + up)
```

### Breaking the database on purpose

```text
db stopped:  /health → paste
db stopped:  /ready  → paste
db started:  /ready  → paste
```

Why should a load balancer stop sending traffic here but not restart the app? (2 lines)

### Tests and coverage

```text
uv run poe test              → paste the last line
uv run poe test-integration  → paste the last line
coverage TOTAL, unit only    → paste
coverage TOTAL, with integration tests → paste
```

Two files or lines my coverage report says are never run, and whether they matter: (2 lines)
