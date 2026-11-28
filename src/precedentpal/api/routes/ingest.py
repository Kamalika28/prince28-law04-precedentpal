import secrets

from arq import create_pool
from arq.connections import RedisSettings
from fastapi import APIRouter, HTTPException, Request, status
from sqlalchemy import select

from precedentpal.api.deps import SettingsDep
from precedentpal.db.models import IngestItem, IngestJob

router = APIRouter(prefix="/ingest", tags=["ingest"])


def require_admin(request: Request, settings: SettingsDep) -> None:
    token = request.headers.get("X-Admin-Token", "")
    if not settings.admin_token or not secrets.compare_digest(token, settings.admin_token):
        raise HTTPException(status_code=403, detail="Invalid admin token")


@router.post("", status_code=status.HTTP_202_ACCEPTED)
async def create_ingest_job(request: Request, settings: SettingsDep) -> dict:
    require_admin(request, settings)
    from precedentpal.api.routes.ingest_records import load_manifest

    records = load_manifest(settings.manifest_file)
    if not records:
        raise HTTPException(status_code=400, detail="No downloaded records")

    async with request.app.state.sessionmaker() as session:
        job = IngestJob(requested=len(records))
        job.items = [IngestItem(record=record) for record in records]
        session.add(job)
        await session.commit()
        job_id = job.id
        item_ids = [item.id for item in job.items]

    redis = await create_pool(RedisSettings.from_dsn(settings.redis_url))
    try:
        for item_id in item_ids:
            await redis.enqueue_job("process_ingest_item", item_id, _job_id=f"ingest:{item_id}")
    finally:
        await redis.aclose()

    return {"job_id": job_id, "requested": len(item_ids)}


@router.get("/{job_id}")
async def ingest_status(job_id: int, request: Request, settings: SettingsDep) -> dict:
    require_admin(request, settings)
    async with request.app.state.sessionmaker() as session:
        job = await session.get(IngestJob, job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Job not found")
        items = (await session.scalars(select(IngestItem).where(IngestItem.job_id == job_id))).all()
        return {
            "job_id": job_id,
            "requested": job.requested,
            "items": [
                {
                    "id": item.id,
                    "status": item.status,
                    "attempts": item.attempts,
                    "pages": item.pages,
                    "error": item.error,
                }
                for item in items
            ],
        }
