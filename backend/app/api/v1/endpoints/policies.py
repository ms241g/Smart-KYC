from fastapi import APIRouter, Query
from app.services.policy_service import PolicyService
from app.schemas.policy import CategoryListResponse, PolicyRequirementsResponse

router = APIRouter()


@router.get("/categories", response_model=CategoryListResponse)
async def list_categories():
    return await PolicyService().list_categories()


@router.get("/{category_id}/requirements", response_model=PolicyRequirementsResponse)
async def get_requirements(
    category_id: str,
    country: str = Query(default="IN"),
    risk_tier: str = Query(default="medium"),
):
    return await PolicyService().get_requirements(category_id, country, risk_tier)
