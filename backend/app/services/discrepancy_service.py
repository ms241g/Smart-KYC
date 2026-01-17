import uuid
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.discrepancy import Discrepancy, DiscrepancySeverity, DiscrepancyStatus


class DiscrepancyService:
    async def list_open(self, case_id: str, db: AsyncSession) -> list[Discrepancy]:
        q = await db.execute(
            select(Discrepancy).where(
                Discrepancy.case_id == case_id,
                Discrepancy.status == DiscrepancyStatus.OPEN
            )
        )
        return list(q.scalars().all())

    async def clear_open(self, case_id: str, db: AsyncSession):
        await db.execute(
            delete(Discrepancy).where(
                Discrepancy.case_id == case_id,
                Discrepancy.status == DiscrepancyStatus.OPEN
            )
        )
        await db.commit()

    async def create(
        self,
        case_id: str,
        field: str,
        message: str,
        expected_value: str | None,
        received_value: str | None,
        severity: DiscrepancySeverity,
        resolution_required: dict | None,
        db: AsyncSession,
    ) -> Discrepancy:
        disc = Discrepancy(
            id=f"DISC-{uuid.uuid4().hex[:12].upper()}",
            case_id=case_id,
            field=field,
            message=message,
            expected_value=expected_value,
            received_value=received_value,
            severity=severity,
            resolution_required=resolution_required,
            status=DiscrepancyStatus.OPEN
        )
        db.add(disc)
        await db.commit()
        await db.refresh(disc)
        return disc
