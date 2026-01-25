import os
from dataclasses import dataclass

from app.ai.plugins.ocr import OCRPlugin
from app.ai.plugins.translation import TranslationPlugin
from app.ai.plugins.doc_classifier import DocumentClassifierPlugin
from app.ai.plugins.field_extractor import FieldExtractorPlugin
from app.ai.plugins.discrepancy_reasoner import DiscrepancyReasonerPlugin

from app.ai.mock.mock_ocr import MockOCR
from app.ai.mock.mock_translation import MockTranslation
from app.ai.mock.mock_doc_classifier import MockDocClassifier

from app.ai.mock.mock_field_extractor import MockFieldExtractor
from app.ai.mock.mock_reasoner import MockDiscrepancyReasoner

from app.ai.gemini.client import GeminiClient
from app.ai.gemini.field_extractor import GeminiFlashFieldExtractor
from app.ai.gemini.discrepancy_reasoner import GeminiFlashDiscrepancyReasoner


@dataclass(frozen=True)
class AIRegistry:
    ocr: OCRPlugin
    translation: TranslationPlugin
    classifier: DocumentClassifierPlugin
    extractor: FieldExtractorPlugin
    reasoner: DiscrepancyReasonerPlugin


def get_registry() -> AIRegistry:
    use_gemini = os.getenv("USE_GEMINI_PLUGINS", "false").lower() == "true"

    ocr = MockOCR()
    translation = MockTranslation()
    classifier = MockDocClassifier()

    if not use_gemini:
        return AIRegistry(
            ocr=ocr,
            translation=translation,
            classifier=classifier,
            extractor=MockFieldExtractor(),
            reasoner=MockDiscrepancyReasoner(),
        )

    gemini_api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    client = GeminiClient(api_key=gemini_api_key, model=model)

    return AIRegistry(
        ocr=ocr,
        translation=translation,
        classifier=classifier,
        extractor=GeminiFlashFieldExtractor(client),
        reasoner=GeminiFlashDiscrepancyReasoner(client),
    )
