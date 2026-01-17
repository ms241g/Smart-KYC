import enum
from sqlalchemy import String, Enum, DateTime, func, JSON, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class DiscrepancyStatus(str, enum.Enum):
    OPEN = "OPEN"
    RESOLVED = "RESOLVED"


class DiscrepancySeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class Discrepancy(Base):
    __tablename__ = "discrepancies"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    case_id: Mapped[str] = mapped_column(String(50), ForeignKey("cases.id"), index=True)

    field: Mapped[str] = mapped_column(String(100))
    message: Mapped[str] = mapped_column(String(500))
    expected_value: Mapped[str | None] = mapped_column(String(255), nullable=True)
    received_value: Mapped[str | None] = mapped_column(String(255), nullable=True)

    severity: Mapped[DiscrepancySeverity] = mapped_column(Enum(DiscrepancySeverity), default=DiscrepancySeverity.MEDIUM)
    status: Mapped[DiscrepancyStatus] = mapped_column(Enum(DiscrepancyStatus), default=DiscrepancyStatus.OPEN)

    resolution_required: Mapped[dict] = mapped_column(JSON, nullable=True)  # e.g. required_doc="utility_bill"

    created_at: Mapped[str] = mapped_column(DateTime(timezone=True), server_default=func.now())
