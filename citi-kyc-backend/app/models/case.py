import enum
from sqlalchemy import String, DateTime, Enum, JSON, func
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class CaseStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    SUBMITTED = "SUBMITTED"
    VALIDATING = "VALIDATING"
    ACTION_REQUIRED = "ACTION_REQUIRED"
    VALIDATED = "VALIDATED"
    READY_FOR_REVIEW = "READY_FOR_REVIEW"
    IN_REVIEW = "IN_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    CLOSED = "CLOSED"


class KYCCase(Base):
    __tablename__ = "cases"

    internal_case_id: Mapped[str] = mapped_column(String(50), primary_key=True)   # internal id
    customer_id: Mapped[str] = mapped_column(String(50), index=True, nullable=False)
    category_id: Mapped[str] = mapped_column(String(50), nullable=False)

    status: Mapped[CaseStatus] = mapped_column(Enum(CaseStatus), default=CaseStatus.DRAFT, create_constraint=True, native_enum=True)

    policy_version: Mapped[str] = mapped_column(String(50), default="v1.0")
    user_payload: Mapped[dict] = mapped_column(JSON, nullable=True)  # form data
    evidence_ids: Mapped[list] = mapped_column(JSON, nullable=True)

    final_case_id: Mapped[str | None] = mapped_column(String(50), nullable=True)  # customer visible id

    timestamp_created: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
