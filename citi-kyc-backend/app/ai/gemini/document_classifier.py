from .client import GeminiClient
from .schemas import DocClassifierSchema
from app.ai.contracts.outputs import DocumentClassificationResult, ConfidenceScore

import boto3
from app.core.config import settings
from app.ai.contracts.inputs import EvidenceInput


class GeminiDocClassifierPlugin:
    def __init__(self, client: GeminiClient):
        self.client = client
        self.s3 = boto3.client("s3", region_name=settings.s3_region)

    def _download(self, key: str) -> bytes:
        print(f"In Downloading file for AI classifier from S3: {key}")
        return self.s3.get_object(Bucket=settings.s3_bucket, Key=key)["Body"].read()

    async def classify(self, evidence: EvidenceInput) -> DocumentClassificationResult:
        file_bytes = self._download(evidence.storage_key)

        prompt = """
You are a banking KYC document classifier.

Identify the document type from the uploaded file.

Possible types:
passport, drivers_license, national_id, utility_bill,
bank_statement, certificate_incorporation, tax_registration,
sof_declaration, unknown

Return ONLY JSON:
{
  "document_type": "<type>",
  "confidence": 0.0-1.0
}
"""

        result: DocClassifierSchema = self.client.generate_structured(
            prompt=prompt,
            schema_model=DocClassifierSchema,
            file_bytes=file_bytes
        )

        return DocumentClassificationResult(
            document_type=result.document_type,
            confidence=ConfidenceScore(
                value=float(result.confidence),
                reason="gemini_multimodal_classifier"
            ),
        )
