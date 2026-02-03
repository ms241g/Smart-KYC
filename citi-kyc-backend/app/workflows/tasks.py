import asyncio
from sqlalchemy import select

from app.workflows.celery_app import celery_app
from app.db.session import AsyncSessionLocal
from app.models.case import KYCCase, CaseStatus
from app.models.evidence import Evidence

from app.services.customer_profile_service import CustomerProfileService
from app.services.discrepancy_service import DiscrepancyService
from app.services.policy_service import PolicyService

from app.models.discrepancy import DiscrepancySeverity
from app.ai.registry import get_registry
from app.ai.contracts.inputs import CaseContextInput, EvidenceInput, CustomerProfileInput
from app.ai.validators.doc_type_validator import validate_doc_type


def _run(coro):
    return asyncio.get_event_loop().run_until_complete(coro)


@celery_app.task(name="validate_case_async")
def validate_case_async(case_id: str):
    _run(_validate_case(case_id))


async def _validate_case(case_id: str):
    registry = get_registry()

    async with AsyncSessionLocal() as db:
        case_q = await db.execute(select(KYCCase).where(KYCCase.internal_case_id == case_id))
        case = case_q.scalar_one_or_none()
        if not case:
            return

        # Clear previous discrepancies
        await DiscrepancyService().clear_open(case_id, db)

        # Fetch policy rules
        policy = PolicyService()
        category_rules = await policy.get_category_rules(case.category_id)
        allowed_doc_types = category_rules.get("allowed_doc_types", [])
        extraction_fields = category_rules.get("extraction_fields", ["full_name", "dob"])
        print(f"Policy rules for category {case.category_id}: allowed_doc_types={allowed_doc_types}, extraction_fields={extraction_fields}")
        # Fetch customer profile
        profile = await CustomerProfileService().fetch_customer_profile(case.customer_id)
        print(f"Customer profile for customer {case.customer_id}: {profile}")

        # Fetch evidences
        evidence_objs = []
        if case.evidence_ids:
            ev_q = await db.execute(select(Evidence).where(Evidence.evidence_id.in_(case.evidence_ids)))
            evidence_objs = list(ev_q.scalars().all())

        evidences = [
            EvidenceInput(
                evidence_id=e.evidence_id,
                storage_key=e.storage_key,
                content_type=e.content_type,
                file_name=e.file_name
            )
            for e in evidence_objs
        ]

        # Construct context
        ctx = CaseContextInput(
            case_id=case.internal_case_id,
            category_id=case.category_id,
            policy_version=case.policy_version,
            customer_profile=CustomerProfileInput(
                customer_id=profile.customer_id,
                full_name=profile.full_name,
                dob=profile.dob,
                citizenship=profile.citizenship,
                address=profile.address
            ),
            form_payload=case.user_payload or {},
            evidences=evidences
        )


# ----------------------------
# Per evidence AI pipeline (Multimodal Gemini)
# ----------------------------
        extracted_bundle = {}

        for ev in evidences:
            try:
                # 1️⃣ Classify document type directly from file
                doc_type = await registry.classifier.classify(ev)
                print(f"Document classification for evidence {ev.evidence_id}: {doc_type}")

                # 2️⃣ Validate document type against policy
                result = validate_doc_type(case.category_id, ev.evidence_id, doc_type.document_type, allowed_doc_types)
                print(f"Document type validation for evidence {ev.evidence_id}: is_valid={result.is_valid}, message={result.message}")
                if not result.is_valid:
                    await DiscrepancyService().create(
                        case_id=case.internal_case_id,
                        field=result.discrepancy_field,
                        message=result.message,
                        expected_value=result.expected_value,
                        received_value=result.received_value,
                        severity=result.severity,
                        resolution_required=result.resolution_required,
                        db=db
                    )
                    case.status = CaseStatus.ACTION_REQUIRED
                    await db.commit()
                    return

                # 3️⃣ Extract structured fields directly from document
                fields = await registry.extractor.extract_from_evidence(
                    storage_key=ev.storage_key,
                    fields_to_extract=extraction_fields
                )

                extracted_bundle[ev.evidence_id] = {
                    "doc_type": doc_type.model_dump(),
                    "fields": fields.model_dump(),
                    "llm_confidence": 0.85  # placeholder; extractor may later return aggregate confidence
                }

            except Exception as e:
                print(f"Discrepancy in AI processing error for evidence {ev.evidence_id}: {e}")
                await DiscrepancyService().create(
                    case_id=case.internal_case_id,
                    field="evidence_processing",
                    message=f"Failed to process evidence {ev.evidence_id}: {e}",
                    severity=DiscrepancySeverity.HIGH,
                    resolution_required=True,
                    expected_value=None,
                    received_value=None,
                    db=db
                )
                case.status = CaseStatus.ACTION_REQUIRED
                await db.commit()
                return


        # Attach extracted summary into context
        ctx.form_payload = {**ctx.form_payload, "_evidence_extracted": extracted_bundle}
        print(f"Extracted data bundle for case {case.internal_case_id}: {extracted_bundle}")

        # ----------------------------
        # ✅ Discrepancy reasoning (Gemini)
        # ----------------------------
        reasoning = await registry.reasoner.reason(ctx)
        print(f"Discrepancy reasoning result for case {case.internal_case_id}: confidence={reasoning.confidence.value}, discrepancies_count={len(reasoning.discrepancies)}")

        if reasoning.discrepancies:
            for d in reasoning.discrepancies:
                await DiscrepancyService().create(
                    case_id=case.internal_case_id,
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
            case.status = CaseStatus.VALIDATED

        await db.commit()
