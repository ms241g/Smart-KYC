from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Dict, Optional, List, Literal


# -------------------------
# Field extraction response
# -------------------------
class GeminiFieldValue(BaseModel):
    value: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)


class GeminiExtractedFields(BaseModel):
    fields: Dict[str, GeminiFieldValue] = Field(default_factory=dict)
    language: Optional[str] = None
    notes: Optional[str] = None


# -------------------------
# Reasoner response
# -------------------------
Severity = Literal["LOW", "MEDIUM", "HIGH", "CRITICAL"]

class GeminiDiscrepancyItem(BaseModel):
    field: str
    expected: Optional[str] = None
    received: Optional[str] = None
    severity: Severity
    explanation: Optional[str] = None
    resolution_required: Optional[dict] = None


class GeminiReasoningOutput(BaseModel):
    discrepancies: List[GeminiDiscrepancyItem] = Field(default_factory=list)
    overall_confidence: float = Field(ge=0.0, le=1.0)
    summary: Optional[str] = None
