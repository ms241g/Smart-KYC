from pydantic import BaseModel
from typing import Dict, Optional, List


class EvidenceInput(BaseModel):
    evidence_id: str
    storage_key: str
    content_type: str
    file_name: str


class CustomerProfileInput(BaseModel):
    customer_id: str
    full_name: str
    dob: str
    citizenship: str
    address: Dict[str, str]


class CaseContextInput(BaseModel):
    case_id: str
    category_id: str
    policy_version: str
    customer_profile: CustomerProfileInput
    form_payload: Dict
    evidences: List[EvidenceInput]
    country: Optional[str] = "IN"
    risk_tier: Optional[str] = "medium"
