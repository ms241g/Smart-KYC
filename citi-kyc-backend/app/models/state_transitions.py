from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class CaseStateTransition(Base):
    __tablename__ = "case_state_transitions"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    case_id: Mapped[str] = mapped_column(String(50), index=True, nullable=False)

    from_status: Mapped[str] = mapped_column(String(50), nullable=False)
    to_status: Mapped[str] = mapped_column(String(50), nullable=False)

    actor_type: Mapped[str] = mapped_column(String(20), default="SYSTEM")  # USER/SYSTEM/HUMAN/AI
    actor_id: Mapped[str | None] = mapped_column(String(80), nullable=True)

    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
