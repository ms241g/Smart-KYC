from pydantic import BaseModel
from typing import Optional, Dict


class DiscrepancyOut(BaseModel):
    id: str
    field: str
    message: str
    expected_value: Optional[str] = None
    received_value: Optional[str] = None
    severity: str
    status: str
    resolution_required: Optional[bool] = None
