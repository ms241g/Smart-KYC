from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db

from app.schemas.case import (
    CaseInitiateRequest,
    CaseInitiateResponse,
    CaseSubmitRequest,
    CaseResolveRequest,
    CaseStatusResponse,
    CaseSubmitForReviewResponse,
)
from app.services.case_service import CaseService
from app.services.human_review_service import HumanReviewService

router = APIRouter()


@router.post("/initiate", response_model=CaseInitiateResponse)
async def initiate_case(payload: CaseInitiateRequest, db: AsyncSession = Depends(get_db)):
    return await CaseService().initiate_case(payload, db)


@router.post("/{case_id}/submit")
async def submit_case(case_id: str, payload: CaseSubmitRequest, db: AsyncSession = Depends(get_db)):
    return await CaseService().submit_case(case_id, payload, db)


@router.post("/{case_id}/resolve")
async def resolve_case(case_id: str, payload: CaseResolveRequest, db: AsyncSession = Depends(get_db)):
    return await CaseService().resolve_case(case_id, payload, db)


@router.get("/{case_id}/status", response_model=CaseStatusResponse)
async def get_status(case_id: str, db: AsyncSession = Depends(get_db)):
    return await CaseService().get_case_status(case_id, db)


@router.post("/{case_id}/submit-for-review", response_model=CaseSubmitForReviewResponse)
async def submit_for_review(case_id: str, db: AsyncSession = Depends(get_db)):
    case = await HumanReviewService().submit_for_review(case_id, db)
    return CaseSubmitForReviewResponse(
        case_id=case.id,
        final_case_id=case.final_case_id,
        status=case.status.value
    )
