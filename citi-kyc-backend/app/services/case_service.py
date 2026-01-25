import uuid
from datetime import datetime, timezone
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.schemas.case import (
    CaseInitiateRequest,
    CaseInitiateResponse,
    CaseSubmitRequest,
    CaseResolveRequest,
    CaseStatusResponse,
)
from app.schemas.discrepancy import DiscrepancyOut
from app.models.case import KYCCase, CaseStatus
from app.services.discrepancy_service import DiscrepancyService
from app.workflows.tasks import validate_case_async


class CaseService:
    async def initiate_case(self, payload: CaseInitiateRequest, db: AsyncSession) -> CaseInitiateResponse:
        case_id = f"INT-{uuid.uuid4().hex[:12].upper()}"
        created_at = datetime.now(timezone.utc)
        print("Initiating case with ID:", case_id, "with payload:", payload)

        case = KYCCase(
            internal_case_id=case_id,
            customer_id=payload.customer_id,
            category_id=payload.category_id,
            policy_version="v1.0",
            status=CaseStatus.DRAFT,
            evidence_ids=[],
            user_payload=None,
            timestamp_created=created_at,
            updated_at=created_at,
        )
        db.add(case)
        await db.commit()

        return CaseInitiateResponse(case_id=case_id, status=case.status.value)

    async def submit_case(self, case_id: str, payload: CaseSubmitRequest, db: AsyncSession):
        if not payload.consent:
            raise ValueError("Consent required")

        q = await db.execute(select(KYCCase).where(KYCCase.id == case_id))
        case = q.scalar_one_or_none()
        if not case:
            raise ValueError("Case not found")

        case.user_payload = payload.customer_details
        case.evidence_ids = payload.evidence_ids
        case.status = CaseStatus.VALIDATING
        await db.commit()

        validate_case_async.delay(case_id)

        return {"case_id": case_id, "status": case.status.value}

    async def resolve_case(self, case_id: str, payload: CaseResolveRequest, db: AsyncSession):
        q = await db.execute(select(KYCCase).where(KYCCase.id == case_id))
        case = q.scalar_one_or_none()
        if not case:
            raise ValueError("Case not found")

        # merge updates
        if payload.updated_customer_details:
            case.user_payload = payload.updated_customer_details

        if payload.additional_evidence_ids:
            existing = set(case.evidence_ids or [])
            case.evidence_ids = list(existing.union(set(payload.additional_evidence_ids)))

        # re-run validations
        case.status = CaseStatus.VALIDATING
        await db.commit()

        validate_case_async.delay(case_id)

        return {"case_id": case_id, "status": case.status.value}

    async def get_case_status(self, case_id: str, db: AsyncSession) -> CaseStatusResponse:
        q = await db.execute(select(KYCCase).where(KYCCase.id == case_id))
        case = q.scalar_one_or_none()
        if not case:
            raise ValueError("Case not found")

        discrepancies = await DiscrepancyService().list_open(case_id, db)
        disc_out = [
            DiscrepancyOut(
                id=d.id,
                field=d.field,
                message=d.message,
                expected_value=d.expected_value,
                received_value=d.received_value,
                severity=d.severity.value,
                status=d.status.value,
                resolution_required=d.resolution_required
            )
            for d in discrepancies
        ]

        next_steps = []
        if case.status == CaseStatus.ACTION_REQUIRED:
            next_steps.append("Resolve discrepancies and upload additional evidence")
        elif case.status == CaseStatus.VALIDATED:
            next_steps.append("Submit case for human review")
        else:
            next_steps.append("Await validation completion")

        return CaseStatusResponse(
            case_id=case.id,
            status=case.status.value,
            discrepancies=disc_out,
            next_steps=next_steps
        )
