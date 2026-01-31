from app.ai.contracts.outputs import OCRResult, TranslationResult, ConfidenceScore
from app.ai.gemini.client import GeminiClient


TRANSLATE_PROMPT = """
Translate the following text to English. Return JSON:
{
  "source_language": "...",
  "translated_text": "...",
  "confidence": 0.0-1.0
}
"""


class GeminiTranslationService:
    def __init__(self, client: GeminiClient):
        self.client = client

    async def translate(self, ocr: OCRResult) -> TranslationResult:
        schema = {
            "type": "object",
            "properties": {
                "source_language": {"type": "string"},
                "translated_text": {"type": "string"},
                "confidence": {"type": "number"}
            },
            "required": ["source_language", "translated_text", "confidence"]
        }

        result = self.client.generate_structured(
            prompt=f"{TRANSLATE_PROMPT}\n\nTEXT:\n{ocr.raw_text}",
            schema_model=schema
        )

        return TranslationResult(
            source_language=result["source_language"],
            target_language="en",
            translated_text=result["translated_text"],
            confidence=ConfidenceScore(value=result["confidence"], reason="gemini_translation"),
        )
