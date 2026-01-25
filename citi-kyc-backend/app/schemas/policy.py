from pydantic import BaseModel
from typing import List, Dict, Any


class KYCCategory(BaseModel):
    id: str
    title: str
    description: str


class CategoryListResponse(BaseModel):
    categories: List[KYCCategory]


class PolicyRequirementsResponse(BaseModel):
    category_id: str
    policy_version: str
    required_fields: List[str]
    required_documents: List[str]
    rules: Dict[str, Any]
