import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.audit import AuditEvent, AuditEventType


class AuditLogger:
    async def log(
        self,
        event_type: AuditEventType,
        payload: dict,
        db: AsyncSession,
        case_id: str | None = None,
        actor_type: str = "SYSTEM",
        actor_id: str | None = None,
    ):
        ev = AuditEvent(
            id=f"AUD-{uuid.uuid4().hex[:12].upper()}",
            case_id=case_id,
            event_type=event_type,
            actor_type=actor_type,
            actor_id=actor_id,
            payload=payload,
        )
        db.add(ev)
        await db.commit()
