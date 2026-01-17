from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from app.schemas.discrepancy import DiscrepancyOut


class CaseInitiateRequest(BaseModel):
    customer_id: str
    category_id: str


class CaseInitiateResponse(BaseModel):
    case_id: str
    status: str


class CaseSubmitRequest(BaseModel):
    customer_details: Dict[str, Any]
    evidence_ids: List[str]
    consent: bool


class CaseResolveRequest(BaseModel):
    updated_customer_details: Optional[Dict[str, Any]] = None
    additional_evidence_ids: Optional[List[str]] = None


class CaseSubmitForReviewResponse(BaseModel):
    case_id: str
    final_case_id: str
    status: str


class CaseStatusResponse(BaseModel):
    case_id: str
    status: str
    discrepancies: List[DiscrepancyOut]
    next_steps: List[str]
