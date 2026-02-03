from __future__ import annotations
import base64
from typing import List
import boto3

from app.ai.contracts.outputs import ExtractedFields, FieldValue, ConfidenceScore
from app.ai.gemini.client import GeminiClient
from app.ai.gemini.schemas import GeminiExtractedFields
from app.core.config import settings


class GeminiFlashFieldExtractor:
    """
    Multimodal extractor: LLM performs OCR + field extraction
    """

    def __init__(self, gemini_client: GeminiClient):
        self.client = gemini_client
        self.s3 = boto3.client("s3", region_name=settings.s3_region)

    def _download_file_bytes(self, key: str) -> bytes:
        obj = self.s3.get_object(Bucket=settings.s3_bucket, Key=key)
        return obj["Body"].read()

    def _build_prompt(self, fields_to_extract: List[str]) -> str:
        fields = "\n".join([f"- {f}" for f in fields_to_extract])
        return f"""
        You are a KYC document understanding AI for a regulated bank.

        The user has uploaded a document (passport, license, utility bill, etc.).
        Extract structured information directly from the document.

        Return ONLY JSON matching schema.

        Fields to extract:
        {fields}

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
        """


    async def extract_from_evidence(self, storage_key: str, fields_to_extract: List[str]) -> ExtractedFields:
        file_bytes = self._download_file_bytes(storage_key)
        print(f"Downloaded {len(file_bytes)} bytes from S3 in extraction for key {storage_key}")

        prompt = self._build_prompt(fields_to_extract)
        #print("Gemini Flash Field Extractor Prompt:", prompt)

        out: GeminiExtractedFields = self.client.generate_structured(
            prompt=prompt,
            schema_model=GeminiExtractedFields,
            file_bytes=file_bytes  # NEW: multimodal input
        )
        print("Gemini Flash Field Extractor Output:", out)
        fields = {
            item.field_name: FieldValue(
                value=item.value,
                confidence=ConfidenceScore(
                    value=float(item.confidence),
                    reason="gemini_multimodal_extractor"
                )
            )
            for item in out.fields
        }


        return ExtractedFields(fields=fields, meta={"extractor": "gemini-2.0-flash-multimodal"})
