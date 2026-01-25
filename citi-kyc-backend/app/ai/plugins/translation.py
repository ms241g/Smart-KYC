from typing import Protocol
from app.ai.contracts.outputs import OCRResult, TranslationResult


class TranslationPlugin(Protocol):
    async def translate(self, ocr: OCRResult, target_language: str = "en") -> TranslationResult:
        ...
