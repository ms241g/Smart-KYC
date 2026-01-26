import enum
from sqlalchemy import String, Enum, DateTime, Integer, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base

class EvidenceStatus(str, enum.Enum):
    INITIATED = "INITIATED"
    UPLOADED = "UPLOADED"
    VERIFIED = "VERIFIED"
    REJECTED = "REJECTED"

class Evidence(Base):
    __tablename__ = "evidence"

    evidence_id: Mapped[str] = mapped_column(String(50), primary_key=True)
    internal_case_id: Mapped[str] = mapped_column(String(50), index=True, nullable=False)

    file_name: Mapped[str] = mapped_column(String(255), nullable=False)
    content_type: Mapped[str] = mapped_column(String(100), nullable=False)

    storage_key: Mapped[str] = mapped_column(String(512), unique=True, nullable=False)

    status: Mapped[EvidenceStatus] = mapped_column(
        Enum(EvidenceStatus), default=EvidenceStatus.INITIATED, nullable=False
    )

    sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)

    timestamp_created: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
