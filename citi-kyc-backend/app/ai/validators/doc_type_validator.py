from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional

from app.models.discrepancy import DiscrepancySeverity


@dataclass(frozen=True)
class DocTypeValidationResult:
    is_valid: bool
    discrepancy_field: Optional[str] = None
    message: Optional[str] = None
    expected_value: Optional[str] = None
    received_value: Optional[str] = None
    severity: Optional[DiscrepancySeverity] = None
    resolution_required: Optional[dict] = None


def validate_doc_type(
    category_id: str,
    evidence_id: str,
    classified_doc_type: str,
    allowed_doc_types: List[str],
) -> DocTypeValidationResult:
    if not allowed_doc_types:
        # policy absent -> allow (fail open) OR fail closed depending on compliance posture
        return DocTypeValidationResult(is_valid=True)

    if classified_doc_type in allowed_doc_types:
        return DocTypeValidationResult(is_valid=True)

    return DocTypeValidationResult(
        is_valid=False,
        discrepancy_field=f"evidence.{evidence_id}.document_type",
        message=f"Document type '{classified_doc_type}' is not acceptable for category '{category_id}'.",
        expected_value=f"Allowed: {allowed_doc_types}",
        received_value=classified_doc_type,
        severity=DiscrepancySeverity.HIGH,
        resolution_required={
            "action": "upload_additional_doc",
            "allowed_doc_types": allowed_doc_types,
        }
    )
