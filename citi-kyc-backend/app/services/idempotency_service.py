from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.idempotency import IdempotencyKey


class IdempotencyService:
    async def get(self, key: str, endpoint: str, db: AsyncSession) -> dict | None:
        q = await db.execute(select(IdempotencyKey).where(IdempotencyKey.id == key))
        item = q.scalar_one_or_none()
        if not item:
            return None
        # endpoint match is defensive
        if item.endpoint != endpoint:
            return None
        return item.response_payload

    async def store(self, key: str, endpoint: str, response_payload: dict, db: AsyncSession):
        item = IdempotencyKey(id=key, endpoint=endpoint, response_payload=response_payload)
        db.add(item)
        await db.commit()
