from __future__ import annotations
from pydantic import BaseModel, Field
from typing import Dict, Optional, List, Literal


# -------------------------
# Field extraction response
# -------------------------
class GeminiFieldValue(BaseModel):
    value: Optional[str] = None
    confidence: float = Field(ge=0.0, le=1.0)


class GeminiFieldItem(BaseModel):
    field_name: str = Field(description="Name of the extracted field")
    value: Optional[str] = Field(description="Extracted value or null")
    confidence: float = Field(ge=0.0, le=1.0, description="Confidence score")


class GeminiExtractedFields(BaseModel):
    fields: List[GeminiFieldItem]


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


class GeminiDiscrepancyItem(BaseModel):
    field: str = Field(description="Field where discrepancy was found")
    expected: Optional[str] = Field(description="Expected value from authoritative source")
    received: Optional[str] = Field(description="Value found in user input or evidence")
    severity: str = Field(description="LOW, MEDIUM, HIGH, CRITICAL")
    resolution_required: bool = Field(description="Whether user action is required")
    explanation: Optional[str] = Field(description="Human-readable explanation")


class GeminiReasoningOutput(BaseModel):
    discrepancies: List[GeminiDiscrepancyItem]
    overall_confidence: float = Field(ge=0.0, le=1.0)


class DocClassifierSchema(BaseModel):
    """
    Structured response expected from Gemini for document classification
    """
    document_type: str = Field(description="Predicted document type")
    confidence: float = Field(ge=0.0, le=1.0, description="Model confidence between 0 and 1")

