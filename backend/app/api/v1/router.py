from fastapi import APIRouter
from app.api.v1.endpoints import policies, cases, evidence

api_router = APIRouter()

api_router.include_router(policies.router, prefix="/policies", tags=["policies"])
api_router.include_router(cases.router, prefix="/cases", tags=["cases"])
api_router.include_router(evidence.router, prefix="/evidence", tags=["evidence"])
