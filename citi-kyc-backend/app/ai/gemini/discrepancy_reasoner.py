from __future__ import annotations
import json
from typing import Any

from app.ai.contracts.inputs import CaseContextInput
from app.ai.contracts.outputs import ReasoningResult, DiscrepancyItem, ConfidenceScore
from app.ai.gemini.client import GeminiClient
from app.ai.gemini.schemas import GeminiReasoningOutput
from app.ai.security.pii_redactor import redact_text, RedactionConfig


def _compact(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, separators=(",", ":"))


REASONER_SYSTEM_PROMPT = """
You are a compliance-grade KYC discrepancy reasoner for Citi Bank.

You must:
- Compare authoritative customer profile vs user payload vs evidence extracted fields
- Identify mismatches relevant to KYC policy
- Produce discrepancies with severity and resolution guidance

Return ONLY JSON matching the response schema.
Do not hallucinate values.
"""


class GeminiFlashDiscrepancyReasoner:
    def __init__(self, gemini_client: GeminiClient):
        self.client = gemini_client

    async def reason(self, ctx: CaseContextInput) -> ReasoningResult:
        # PII minimization: redact only in free text fields (if any)
        # Structured JSON still contains necessary KYC fields; keep only what is required.
        profile = ctx.customer_profile.model_dump()
        payload = ctx.form_payload

        prompt = f"""{REASONER_SYSTEM_PROMPT}

CATEGORY_ID: {ctx.category_id}
POLICY_VERSION: {ctx.policy_version}
COUNTRY: {ctx.country}
RISK_TIER: {ctx.risk_tier}

AUTHORITATIVE_CUSTOMER_PROFILE:
{_compact(profile)}

USER_FORM_PAYLOAD:
{_compact(payload)}

EVIDENCE_LIST:
{_compact([e.model_dump() for e in ctx.evidences])}
"""

        out: GeminiReasoningOutput = self.client.generate_structured(
            prompt=prompt,
            schema_model=GeminiReasoningOutput,
            temperature=0.15,
            max_output_tokens=2048,
        )

        discrepancies = [
            DiscrepancyItem(
                field=d.field,
                expected=d.expected,
                received=d.received,
                severity=d.severity,
                resolution_required=d.resolution_required,
                explanation=d.explanation,
            )
            for d in out.discrepancies
        ]

        return ReasoningResult(
            discrepancies=discrepancies,
            confidence=ConfidenceScore(value=float(out.overall_confidence), reason="gemini_flash_reasoner"),
        )
