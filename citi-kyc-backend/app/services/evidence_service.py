import hashlib
import uuid
from datetime import datetime, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import boto3

from app.core.config import settings
from app.services.audit_logger import AuditLogger, AuditEventType
from app.models.evidence import Evidence, EvidenceStatus
from app.models.audit import AuditEventType
from app.schemas.evidence import (
    EvidenceUploadUrlRequest,
    EvidenceUploadUrlResponse,
    EvidenceConfirmUploadRequest,
    EvidenceConfirmUploadResponse,
)

ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "image/jpeg",
    "image/jpg",
    "image/png",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}

class EvidenceService:
    """
    Handles:
    - evidence metadata persistence
    - secure upload url generation
    - confirmation & checksum metadata capture
    """

    def _s3_client(self):
        session = boto3.session.Session()
        return session.client(
            "s3",
            region_name=settings.s3_region,
            endpoint_url=settings.s3_endpoint_url,
            aws_access_key_id=settings.s3_access_key_id,
            aws_secret_access_key=settings.s3_secret_access_key,
        )

    def _generate_storage_key(self, case_id: str, evidence_id: str, file_name: str) -> str:
        safe_name = file_name.replace(" ", "_")
        return f"cases/{case_id}/evidence/{evidence_id}/{safe_name}"

    async def generate_upload_url(
        self,
        payload: EvidenceUploadUrlRequest,
        db: AsyncSession,
    ) -> EvidenceUploadUrlResponse:
        print(f"Generating upload URL for case_id={payload.case_id}")
        if payload.content_type not in ALLOWED_CONTENT_TYPES:
            raise ValueError(f"Unsupported content_type: {payload.content_type}")

        now = datetime.now(timezone.utc)
        evidence_id = f"EVD-{uuid.uuid4().hex[:16].upper()}"
        storage_key = self._generate_storage_key(payload.case_id, evidence_id, payload.file_name)

        # Persist metadata
        ev = Evidence(
            evidence_id=evidence_id,
            internal_case_id=payload.case_id,
            file_name=payload.file_name,
            content_type=payload.content_type,
            storage_key=storage_key,
            status=EvidenceStatus.INITIATED,
            timestamp_created=now,
            updated_at=now,
        )
        db.add(ev)
        await db.commit()

        # Create presigned URL
        s3 = self._s3_client()
        presigned_url = s3.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": settings.s3_bucket,
                "Key": storage_key,
                "ContentType": payload.content_type,
            },
            ExpiresIn=settings.s3_url_expiry_seconds,
        )

        return EvidenceUploadUrlResponse(
            evidence_id=evidence_id,
            upload_url=presigned_url,
            storage_key=storage_key,
            expires_in_seconds=settings.s3_url_expiry_seconds,
        )

    async def confirm_upload(
        self,
        payload: EvidenceConfirmUploadRequest,
        db: AsyncSession,
    ) -> EvidenceConfirmUploadResponse:
        q = await db.execute(select(Evidence).where(Evidence.evidence_id == payload.evidence_id))
        ev: Evidence | None = q.scalar_one_or_none()
        if not ev:
            raise ValueError("Evidence not found")

        # Idempotency: allow repeat confirm with same values
        if ev.status == EvidenceStatus.VERIFIED:
            return EvidenceConfirmUploadResponse(evidence_id=ev.evidence_id, status=ev.status.value)

        ev.sha256 = payload.sha256
        ev.file_size = payload.file_size
        ev.status = EvidenceStatus.VERIFIED

        await db.commit()

        await AuditLogger().log(
            event_type=AuditEventType.EVIDENCE_EVENT,
            payload={"event": "CONFIRM_UPLOAD", "evidence_id": ev.evidence_id, "storage_key": ev.storage_key},
            db=db,
            case_id=ev.internal_case_id
        )        

        return EvidenceConfirmUploadResponse(evidence_id=ev.evidence_id, status=ev.status.value)

    async def get_evidence_by_case(self, case_id: str, db: AsyncSession) -> list[Evidence]:
        q = await db.execute(select(Evidence).where(Evidence.internal_case_id == case_id))
        return list(q.scalars().all())
