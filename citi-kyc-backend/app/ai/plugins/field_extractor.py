from typing import Protocol
from app.ai.contracts.outputs import OCRResult, TranslationResult, ExtractedFields


class FieldExtractorPlugin(Protocol):
    async def extract(self, text: str) -> ExtractedFields:
        """Extract KYC fields from text."""
        ...
