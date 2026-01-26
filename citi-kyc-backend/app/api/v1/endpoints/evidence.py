from fastapi import APIRouter, Depends
import traceback
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.evidence import (
    EvidenceUploadUrlRequest,
    EvidenceUploadUrlResponse,
    EvidenceConfirmUploadRequest,
    EvidenceConfirmUploadResponse,
)
from app.services.evidence_service import EvidenceService
from app.db.session import get_db

router = APIRouter()


@router.post("/upload-url", response_model=EvidenceUploadUrlResponse)
async def generate_upload_url(
    payload: EvidenceUploadUrlRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        print(f"Generating upload URL for case_id={payload}")
        return await EvidenceService().generate_upload_url(payload, db)
    except Exception as e:
        print("Error in generate_upload_url:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/confirm-upload", response_model=EvidenceConfirmUploadResponse)
async def confirm_upload(
    payload: EvidenceConfirmUploadRequest,
    db: AsyncSession = Depends(get_db),
):
    try:
        print(f"Confirming upload for evidence_id={payload.evidence_id}")
        return await EvidenceService().confirm_upload(payload, db)
    except Exception as e:
        print("Error in confirm_upload:", e)
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(e))
