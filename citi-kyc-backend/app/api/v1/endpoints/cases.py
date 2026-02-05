from fastapi import APIRouter, Depends
from fastapi import Header
from fastapi import HTTPException
import traceback
from app.services.idempotency_service import IdempotencyService
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
    try:
        print("Initiating case with payload:", payload, "database session:", db)
        return await CaseService().initiate_case(payload, db)
    except Exception as e:
        from fastapi import HTTPException
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{case_id}/submit")
async def submit_case(
    case_id: str,
    payload: CaseSubmitRequest,
    idempotency_key: str | None = Header(default=None, alias="Idempotency-Key"),
    db: AsyncSession = Depends(get_db),
):
    try:
        if idempotency_key:
            cached = await IdempotencyService().get(idempotency_key, f"/cases/{case_id}/submit", db)
            if cached:
                return cached

        resp = await CaseService().submit_case(case_id, payload, db)

        if idempotency_key:
            await IdempotencyService().store(idempotency_key, f"/cases/{case_id}/submit", resp, db)

        return resp
    except Exception as e:
        from fastapi import HTTPException
        import traceback
        traceback.print_exc()
        if idempotency_key:
            await IdempotencyService().store_error(idempotency_key, f"/cases/{case_id}/submit", str(e), db)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{case_id}/resolve")
async def resolve_case(case_id: str, payload: CaseResolveRequest, db: AsyncSession = Depends(get_db)):
    try:
        return await CaseService().resolve_case(case_id, payload, db)
    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{case_id}/status", response_model=CaseStatusResponse)
async def get_status(case_id: str, db: AsyncSession = Depends(get_db)):
    try:
        return await CaseService().get_case_status(case_id, db)
    except Exception as e:
        from fastapi import HTTPException
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{case_id}/submit-for-review", response_model=CaseSubmitForReviewResponse)
async def submit_for_review(case_id: str, db: AsyncSession = Depends(get_db)):
    try:
        case = await HumanReviewService().submit_for_review(case_id, db)
        return CaseSubmitForReviewResponse(
            case_id=case.internal_case_id,
            final_case_id=case.final_case_id,
            status=case.status.value
        )
    except Exception as e:
        from fastapi import HTTPException
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
