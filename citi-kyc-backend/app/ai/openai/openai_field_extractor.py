import boto3
from app.ai.contracts.outputs import ExtractedFields, FieldValue, ConfidenceScore
from app.ai.gemini.schemas import GeminiExtractedFields
from app.core.config import settings


class OpenAIFieldExtractor:
    def __init__(self, client):
        self.client = client
        self.s3 = boto3.client("s3", region_name=settings.s3_region)

    def _download(self, key):
        return self.s3.get_object(Bucket=settings.s3_bucket, Key=key)["Body"].read()

    async def extract_from_evidence(self, storage_key: str, fields_to_extract: list[str]) -> ExtractedFields:
        file_bytes = self._download(storage_key)

        prompt = f"""
You are a KYC document understanding AI for a regulated bank.

        The user has uploaded a document (passport, license, utility bill, etc.).
        Extract structured information directly from the document.
        In case name is splitted into multiple fields (e.g., first name/given name, last/surname name), concatenate them into a single full_name field.

        Return ONLY JSON matching schema.

        Fields to extract:
        {fields_to_extract}

        Output format:
        {{
        "fields": [
            {{
            "field_name": "<field name>",
            "value": "<value or null>",
            "confidence": 0.0-1.0
            }}
        ]
        }}

        Rules:
        - Read the document visually.
        - If not English, translate internally before extraction.
        - Convert fields into uppercase strings.
        - Remove any punctuation from values.
        - Remove any Mr./Ms. or any other prefixes from names.
        - Dates must be ISO format YYYY-MM-DD.
        - If a field is missing, return value=null with low confidence.

Return JSON only.
"""

        out: GeminiExtractedFields = self.client.generate_structured(
            prompt=prompt,
            schema_model=GeminiExtractedFields,
            file_bytes=file_bytes,
        )

        fields = {
            item.field_name: FieldValue(
                value=item.value,
                confidence=ConfidenceScore(value=item.confidence, reason="openai_multimodal")
            )
            for item in out.fields
        }

        return ExtractedFields(fields=fields, meta={"extractor": "openai"})
