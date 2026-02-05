from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.case import KYCCase, CaseStatus
from app.utils.ids import new_case_id
from app.utils.state_machine import can_transition


class HumanReviewService:
    async def submit_for_review(self, case_id: str, db: AsyncSession) -> KYCCase:
        q = await db.execute(select(KYCCase).where(KYCCase.internal_case_id == case_id))
        case = q.scalar_one_or_none()
        if not case:
            raise ValueError("Case not found")

        if case.status != CaseStatus.VALIDATED:
            raise ValueError("Case must be VALIDATED before submitting for review")

        # Transition: VALIDATED -> READY_FOR_REVIEW -> IN_REVIEW
        case.status = CaseStatus.IN_REVIEW

        if not case.final_case_id:
            case.final_case_id = new_case_id()

        await db.commit()
        await db.refresh(case)
        return case
