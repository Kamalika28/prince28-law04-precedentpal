import asyncio
from pathlib import Path

from arq import Retry
from arq.connections import RedisSettings
from sqlalchemy import select

from precedentpal.config import get_settings
from precedentpal.db.models import Document, IngestItem
from precedentpal.db.session import make_engine, make_sessionmaker
from precedentpal.ingest.parse import ParseError, parse_file
from precedentpal.store import document_id, save_document, save_failure


async def startup(ctx: dict) -> None:
    settings = get_settings()
    engine = make_engine(settings)
    ctx["engine"] = engine
    ctx["sessions"] = make_sessionmaker(engine)

    async with ctx["sessions"]() as session:
        items = (
            await session.scalars(
                select(IngestItem).where(IngestItem.status.in_(["queued", "running"]))
            )
        ).all()
        for item in items:
            item.status = "queued"
        await session.commit()

        for item in items:
            await ctx["redis"].enqueue_job(
                "process_ingest_item", item.id, _job_id=f"ingest:{item.id}"
            )


async def shutdown(ctx: dict) -> None:
    await ctx["engine"].dispose()


async def process_ingest_item(ctx: dict, item_id: int) -> None:
    settings = get_settings()

    async with ctx["sessions"]() as session:
        item = await session.get(IngestItem, item_id)
        if item is None or item.status in {"done", "failed"}:
            return

        record = item.record
        item.status = "running"
        item.attempts += 1
        await session.commit()

        try:
            existing = await session.scalar(
                select(Document).where(Document.external_id == document_id(record["sha256"]))
            )
            if existing is None:
                parsed = await asyncio.to_thread(parse_file, Path(record["path"]))
                pages = len(parsed.pages)
                await save_document(session, record, parsed)
            else:
                pages = int(existing.metadata_.get("pages", 0))

            item.status = "done"
            item.pages = pages
            item.error = ""
            await session.commit()

        except ParseError as error:
            await session.rollback()
            await save_failure(session, record, error)
            item = await session.get(IngestItem, item_id)
            item.status = "failed"
            item.error = f"{error.reason}: {error.detail}"
            await session.commit()

        except Exception as error:
            await session.rollback()
            item = await session.get(IngestItem, item_id)
            item.error = str(error)[:2000]
            item.status = "failed" if item.attempts >= settings.ingest_max_tries else "queued"
            await session.commit()
            if item.status == "queued":
                raise Retry(defer=5) from error


class WorkerSettings:
    functions = [process_ingest_item]
    redis_settings = RedisSettings.from_dsn(get_settings().redis_url)
    on_startup = startup
    on_shutdown = shutdown
    max_jobs = get_settings().ingest_concurrency
    job_timeout = get_settings().ingest_job_timeout
    max_tries = get_settings().ingest_max_tries
