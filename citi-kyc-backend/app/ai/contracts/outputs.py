from pydantic import BaseModel
from typing import List, Dict, Optional, Any


class ConfidenceScore(BaseModel):
    value: float  # 0-1
    reason: Optional[str] = None


class OCRTextBlock(BaseModel):
    page: int
    text: str


class OCRResult(BaseModel):
    language: str
    text_blocks: List[OCRTextBlock]
    raw_text: str
    confidence: ConfidenceScore


class TranslationResult(BaseModel):
    source_language: str
    target_language: str
    translated_text: str
    confidence: ConfidenceScore


class DocumentClassificationResult(BaseModel):
    document_type: str  # passport, drivers_license, utility_bill, etc
    confidence: ConfidenceScore


class FieldValue(BaseModel):
    value: Optional[str] = None
    confidence: ConfidenceScore


class ExtractedFields(BaseModel):
    fields: Dict[str, FieldValue]  # name, dob, address...
    meta: Optional[Dict[str, Any]] = None


class DiscrepancyItem(BaseModel):
    field: str
    expected: Optional[str]
    received: Optional[str]
    severity: str  # LOW/MEDIUM/HIGH/CRITICAL
    resolution_required: Optional[Dict[str, Any]] = None
    explanation: Optional[str] = None


class ReasoningResult(BaseModel):
    discrepancies: List[DiscrepancyItem]
    confidence: ConfidenceScore
