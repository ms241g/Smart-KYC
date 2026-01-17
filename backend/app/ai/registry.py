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


@dataclass(frozen=True)
class AIRegistry:
    ocr: OCRPlugin
    translation: TranslationPlugin
    classifier: DocumentClassifierPlugin
    extractor: FieldExtractorPlugin
    reasoner: DiscrepancyReasonerPlugin


def get_registry() -> AIRegistry:
    """
    In production: use env-based configuration to choose plugins.
    """
    return AIRegistry(
        ocr=MockOCR(),
        translation=MockTranslation(),
        classifier=MockDocClassifier(),
        extractor=MockFieldExtractor(),
        reasoner=MockDiscrepancyReasoner()
    )
