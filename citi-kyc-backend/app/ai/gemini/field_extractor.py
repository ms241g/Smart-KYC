from __future__ import annotations
from typing import List, Optional

from app.ai.contracts.outputs import ExtractedFields, FieldValue, ConfidenceScore
from app.ai.gemini.client import GeminiClient
from app.ai.gemini.schemas import GeminiExtractedFields
from app.ai.security.pii_redactor import redact_text, RedactionConfig


def _build_prompt(fields_to_extract: List[str]) -> str:
    field_lines = "\n".join([f"- {f}" for f in fields_to_extract])
    return f"""
You are a KYC extraction engine for Citi Bank.

Extract ONLY these fields from document text:
{field_lines}

Rules:
- Return ONLY JSON matching schema.
- Use ISO date format yyyy-mm-dd.
- If field missing: value=null and low confidence.
"""


class GeminiFlashFieldExtractor:
    def __init__(self, gemini_client: GeminiClient):
        self.client = gemini_client

    async def extract(self, text: str, fields_to_extract: Optional[List[str]] = None) -> ExtractedFields:
        fields_to_extract = fields_to_extract or ["full_name", "dob", "address.city"]

        safe_text = redact_text(text, RedactionConfig())

        prompt = f"""{_build_prompt(fields_to_extract)}

DOCUMENT_TEXT:
{safe_text}
"""
        out: GeminiExtractedFields = self.client.generate_structured(
            prompt=prompt,
            schema_model=GeminiExtractedFields,
            temperature=0.1,
            max_output_tokens=2048,
        )

        fields = {
            k: FieldValue(
                value=v.value,
                confidence=ConfidenceScore(value=float(v.confidence), reason="gemini_flash_extractor")
            )
            for k, v in out.fields.items()
        }

        return ExtractedFields(fields=fields, meta={"extractor": "gemini-2.0-flash", "redacted": True})
