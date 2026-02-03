from __future__ import annotations
from app.ai.contracts.outputs import OCRResult, OCRTextBlock, ConfidenceScore
from app.ai.contracts.inputs import EvidenceInput

import pytesseract
from PIL import Image
import io
import boto3
from botocore.exceptions import ClientError

from app.core.config import settings


class OCRProviderBase:
    async def extract_text(self, evidence: EvidenceInput) -> OCRResult:
        raise NotImplementedError


class TesseractOCRProvider(OCRProviderBase):
    def __init__(self):
        self.s3 = boto3.client("s3", region_name=settings.s3_region)

    def _download_from_s3(self, key: str) -> bytes:
        try:
            response = self.s3.get_object(Bucket=settings.s3_bucket, Key=key)
            return response["Body"].read()
        except ClientError as e:
            raise RuntimeError(f"Failed to download evidence from S3 key={key}: {e}")

    async def extract_text(self, evidence: EvidenceInput) -> OCRResult:
        # Download file bytes from S3 using storage key
        try:
            file_bytes = self._download_from_s3(evidence.storage_key)
        except RuntimeError as e:
            raise RuntimeError(f"Failed to download file from s3 for evidence_id={evidence.evidence_id}: {e}")
        print(f"Downloaded {len(file_bytes)} bytes from S3 for evidence_id={evidence.evidence_id}")
        # Load into PIL
        try:
            image = Image.open(io.BytesIO(file_bytes))
        except Exception as e:
            raise RuntimeError(f"Failed to load image into object from S3 downloaded evidence_id={evidence.evidence_id}: {e}")
        print(f"Image format: {image.format}, size: {image.size}, mode: {image.mode}")

        # Run OCR
        try:
            text = pytesseract.image_to_string(image)
        except Exception as e:
            raise RuntimeError(f"Failed to run OCR for evidence_id={evidence.evidence_id}: {e}")
        print(f"OCR extracted text (first 100 chars): {text[:100]}...")

        return OCRResult(
            language="unknown",
            text_blocks=[OCRTextBlock(page=1, text=text)],
            raw_text=text,
            confidence=ConfidenceScore(value=0.6, reason="tesseract_local_s3"),
        )


class OCRService:
    def __init__(self, provider: OCRProviderBase):
        self.provider = provider

    async def run(self, evidence: EvidenceInput) -> OCRResult:
        return await self.provider.extract_text(evidence)
