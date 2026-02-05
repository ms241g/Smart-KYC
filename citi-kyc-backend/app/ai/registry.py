import os
from dataclasses import dataclass
from dotenv import load_dotenv

#from app.ai.plugins.doc_classifier import GeminiDocClassifierPlugin
#from app.ai.plugins.field_extractor import FieldExtractorPlugin
#from app.ai.plugins.discrepancy_reasoner import DiscrepancyReasonerPlugin

from app.ai.plugins.ocr import DefaultOCRPlugin
from app.ai.plugins.translation import GeminiTranslationPlugin
#from app.ai.plugins.doc_classifier import GeminiDocClassifierPlugin
from app.ai.gemini.document_classifier import GeminiDocClassifierPlugin
from app.ai.gemini.client import GeminiClient

from app.ai.gemini.gemini_field_extractor import GeminiFlashFieldExtractor
from app.ai.gemini.discrepancy_reasoner import GeminiFlashDiscrepancyReasoner
from app.ai.openai.client import OpenAIClient
from app.ai.openai.openai_field_extractor import OpenAIFieldExtractor
from app.ai.openai.openai_document_classifier import OpenAIDocClassifier
from app.ai.openai.openai_discrepancy_reasoner import OpenAIDiscrepancyReasoner


load_dotenv()

@dataclass(frozen=True)
class AIRegistry:
    classifier: object
    extractor: object
    reasoner: object


def get_registry() -> AIRegistry:
    provider = os.getenv("AI_PROVIDER", "gemini")

    if provider == "openai":
        client = OpenAIClient(api_key=os.getenv("OPENAI_API_KEY"))
        return AIRegistry(
            classifier=OpenAIDocClassifier(client),
            extractor=OpenAIFieldExtractor(client),
            reasoner=OpenAIDiscrepancyReasoner(client),
        )
    else:
        # Default Gemini
        client = GeminiClient(api_key=os.getenv("GEMINI_API_KEY"))
        return AIRegistry(
            classifier=GeminiDocClassifierPlugin(client),
            extractor=GeminiFlashFieldExtractor(client),
            reasoner=GeminiFlashDiscrepancyReasoner(client),
        )
