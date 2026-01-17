from fastapi import APIRouter, Depends
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
    return await EvidenceService().generate_upload_url(payload, db)


@router.post("/confirm-upload", response_model=EvidenceConfirmUploadResponse)
async def confirm_upload(
    payload: EvidenceConfirmUploadRequest,
    db: AsyncSession = Depends(get_db),
):
    return await EvidenceService().confirm_upload(payload, db)
