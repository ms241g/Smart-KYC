from app.ai.contracts.outputs import OCRResult, TranslationResult, ConfidenceScore


class MockTranslation:
    async def translate(self, ocr: OCRResult, target_language: str = "en") -> TranslationResult:
        return TranslationResult(
            source_language=ocr.language,
            target_language=target_language,
            translated_text=ocr.raw_text,
            confidence=ConfidenceScore(value=0.9, reason="mock_translation"),
        )
