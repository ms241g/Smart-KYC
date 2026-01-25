import enum
from sqlalchemy import String, DateTime, Enum, JSON, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class AuditEventType(str, enum.Enum):
    API_REQUEST = "API_REQUEST"
    API_RESPONSE = "API_RESPONSE"
    AI_INVOCATION = "AI_INVOCATION"
    STATE_TRANSITION = "STATE_TRANSITION"
    EVIDENCE_EVENT = "EVIDENCE_EVENT"
    REVIEW_EVENT = "REVIEW_EVENT"


class AuditEvent(Base):
    __tablename__ = "audit_events"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    case_id: Mapped[str | None] = mapped_column(String(50), index=True, nullable=True)

    event_type: Mapped[AuditEventType] = mapped_column(Enum(AuditEventType), nullable=False)

    # who/what triggered it
    actor_type: Mapped[str] = mapped_column(String(30), default="SYSTEM")  # USER/SYSTEM/HUMAN/AI
    actor_id: Mapped[str | None] = mapped_column(String(80), nullable=True)

    # payload for traceability
    payload: Mapped[dict] = mapped_column(JSON, nullable=False)

    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
