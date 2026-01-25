from pydantic import BaseModel, Field

class EvidenceUploadUrlRequest(BaseModel):
    case_id: str = Field(..., min_length=6)
    file_name: str
    content_type: str

class EvidenceUploadUrlResponse(BaseModel):
    evidence_id: str
    upload_url: str
    storage_key: str
    expires_in_seconds: int

class EvidenceConfirmUploadRequest(BaseModel):
    evidence_id: str
    sha256: str = Field(..., min_length=64, max_length=64)
    file_size: int = Field(..., ge=1)

class EvidenceConfirmUploadResponse(BaseModel):
    evidence_id: str
    status: str
