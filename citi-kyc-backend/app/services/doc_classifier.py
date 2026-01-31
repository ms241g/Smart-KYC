from app.ai.contracts.inputs import EvidenceInput
from app.ai.contracts.outputs import DocumentClassificationResult, ConfidenceScore
from app.ai.gemini.client import GeminiClient


DOC_CLASS_PROMPT = """
You are a KYC document classification model for a bank.

Identify the document type from this OCR text.

Possible types:
passport, drivers_license, national_id, utility_bill, bank_statement,
certificate_incorporation, tax_registration, sof_declaration, unknown

Return JSON:
{
  "document_type": "...",
  "confidence": 0.0-1.0
}
"""


class GeminiDocClassifierService:
    def __init__(self, client: GeminiClient):
        self.client = client

    async def classify(self, text: str) -> DocumentClassificationResult:
        schema = {
            "type": "object",
            "properties": {
                "document_type": {"type": "string"},
                "confidence": {"type": "number"}
            },
            "required": ["document_type", "confidence"]
        }

        result = self.client.generate_structured(
            prompt=f"{DOC_CLASS_PROMPT}\n\nTEXT:\n{text}",
            schema_model=schema
        )

        return DocumentClassificationResult(
            document_type=result["document_type"],
            confidence=ConfidenceScore(value=result["confidence"], reason="gemini_doc_classifier"),
        )
