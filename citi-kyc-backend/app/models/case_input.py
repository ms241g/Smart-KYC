from sqlalchemy import String, DateTime, JSON, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class CaseInput(Base):
    __tablename__ = "case_inputs"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    case_id: Mapped[str] = mapped_column(String(50), index=True, nullable=False)

    payload: Mapped[dict] = mapped_column(JSON, nullable=False)
    consent: Mapped[bool] = mapped_column(default=False)
    consent_version: Mapped[str] = mapped_column(String(50), default="v1")
    consent_text_hash: Mapped[str] = mapped_column(String(128), default="")

    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
