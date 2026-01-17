import asyncio
from sqlalchemy import select
from app.workflows.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from app.models.case import KYCCase, CaseStatus
from app.models.evidence import Evidence
from app.services.customer_profile_service import CustomerProfileService
from app.services.discrepancy_service import DiscrepancyService
from app.models.discrepancy import DiscrepancySeverity
from app.ai.registry import get_registry
from app.ai.contracts.inputs import CaseContextInput, EvidenceInput, CustomerProfileInput


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


@celery_app.task(name="validate_case_async")
def validate_case_async(case_id: str):
    _run(_validate_case(case_id))


async def _validate_case(case_id: str):
    registry = get_registry()

    async with AsyncSessionLocal() as db:
        case_q = await db.execute(select(KYCCase).where(KYCCase.id == case_id))
        case = case_q.scalar_one_or_none()
        if not case:
            return

        await DiscrepancyService().clear_open(case_id, db)

        # Profile
        profile = await CustomerProfileService().fetch_customer_profile(case.customer_id)

        # Evidence objects
        evidence_objs = []
        if case.evidence_ids:
            ev_q = await db.execute(select(Evidence).where(Evidence.id.in_(case.evidence_ids)))
            evidence_objs = list(ev_q.scalars().all())

        evidences = [
            EvidenceInput(
                evidence_id=e.id,
                storage_key=e.storage_key,
                content_type=e.content_type,
                file_name=e.file_name,
            )
            for e in evidence_objs
        ]

        ctx = CaseContextInput(
            case_id=case.id,
            category_id=case.category_id,
            policy_version=case.policy_version,
            customer_profile=CustomerProfileInput(
                customer_id=profile.customer_id,
                full_name=profile.full_name,
                dob=profile.dob,
                citizenship=profile.citizenship,
                address=profile.address,
            ),
            form_payload=case.user_payload or {},
            evidences=evidences,
        )

        # ------------------------------
        # AI Pipeline per evidence
        # ------------------------------
        extracted_bundle = {}
        for ev in evidences:
            ocr = await registry.ocr.run(ev)

            text = ocr.raw_text
            if ocr.language != "en":
                tr = await registry.translation.translate(ocr, "en")
                text = tr.translated_text

            doc_type = await registry.classifier.classify(ev)
            fields = await registry.extractor.extract(text)

            extracted_bundle[ev.evidence_id] = {
                "doc_type": doc_type,
                "fields": fields,
                "ocr": ocr,
            }

        # ------------------------------
        # Discrepancy reasoning (AI)
        # ------------------------------
        reasoning = await registry.reasoner.reason(ctx)

        # If reasoner returns discrepancies, persist them
        if reasoning.discrepancies:
            for d in reasoning.discrepancies:
                await DiscrepancyService().create(
                    case_id=case_id,
                    field=d.field,
                    message=d.explanation or "Discrepancy detected",
                    expected_value=d.expected,
                    received_value=d.received,
                    severity=DiscrepancySeverity[d.severity],
                    resolution_required=d.resolution_required,
                    db=db
                )
            case.status = CaseStatus.ACTION_REQUIRED
        else:
            # fallback deterministic check (profile vs form)
            user = case.user_payload or {}
            if user.get("dob") and user["dob"] != profile.dob:
                await DiscrepancyService().create(
                    case_id=case_id,
                    field="dob",
                    message="DOB mismatch with customer profile",
                    expected_value=profile.dob,
                    received_value=user["dob"],
                    severity=DiscrepancySeverity.CRITICAL,
                    resolution_required={"action": "update_form"},
                    db=db,
                )
                case.status = CaseStatus.ACTION_REQUIRED
            else:
                case.status = CaseStatus.VALIDATED

        await db.commit()
