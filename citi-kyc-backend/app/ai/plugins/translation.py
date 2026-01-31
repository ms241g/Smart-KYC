from app.ai.contracts.outputs import OCRResult, TranslationResult
from app.services.translation_service import GeminiTranslationService
from app.ai.gemini.client import GeminiClient


class GeminiTranslationPlugin:
    def __init__(self, client: GeminiClient):
        self.service = GeminiTranslationService(client)

    async def translate(self, ocr: OCRResult, target_language: str = "en") -> TranslationResult:
        return await self.service.translate(ocr)
