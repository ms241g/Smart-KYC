import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.review_task import ReviewTask, ReviewStatus


class DBHumanReviewAdapter:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_review_task(self, case_id: str, payload: dict) -> str:
        task_id = f"REV-{uuid.uuid4().hex[:12].upper()}"
        task = ReviewTask(id=task_id, case_id=case_id, payload=payload, status=ReviewStatus.OPEN)
        self.db.add(task)
        await self.db.commit()
        return task_id
