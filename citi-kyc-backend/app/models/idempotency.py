from sqlalchemy import String, DateTime, JSON, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class IdempotencyKey(Base):
    __tablename__ = "idempotency_keys"

    idempotency_key: Mapped[str] = mapped_column(String(120), primary_key=True)  # idempotency key
    endpoint: Mapped[str] = mapped_column(String(200), nullable=False)

    # stored successful response snapshot
    response_payload: Mapped[dict] = mapped_column(JSON, nullable=False)

    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
