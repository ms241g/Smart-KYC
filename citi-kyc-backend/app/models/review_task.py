import enum
from sqlalchemy import String, Enum, DateTime, JSON, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class ReviewStatus(str, enum.Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    CLOSED = "CLOSED"


class ReviewTask(Base):
    __tablename__ = "review_tasks"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    case_id: Mapped[str] = mapped_column(String(50), index=True, nullable=False)

    queue: Mapped[str] = mapped_column(String(80), default="CITI_COMPLIANCE_QUEUE")
    status: Mapped[ReviewStatus] = mapped_column(Enum(ReviewStatus), default=ReviewStatus.OPEN)

    assigned_to: Mapped[str | None] = mapped_column(String(80), nullable=True)

    sla_due_at: Mapped[str | None] = mapped_column(String(50), nullable=True)

    payload: Mapped[dict] = mapped_column(JSON, nullable=True)

    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
