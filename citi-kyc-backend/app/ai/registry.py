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


load_dotenv()

@dataclass(frozen=True)
class AIRegistry:
    classifier: object
    extractor: object
    reasoner: object


def get_registry() -> AIRegistry:
    client = GeminiClient(api_key=os.getenv("GEMINI_API_KEY"))
    print("AI Registry - Using Gemini Plugins")

    return AIRegistry(
        classifier=GeminiDocClassifierPlugin(client),
        extractor=GeminiFlashFieldExtractor(client),
        reasoner=GeminiFlashDiscrepancyReasoner(client),
    )

"""
@dataclass(frozen=True)
class AIRegistry:
    ocr: DefaultOCRPlugin
    translation: GeminiTranslationPlugin
    classifier: GeminiDocClassifierPlugin
    extractor: GeminiFlashFieldExtractor
    reasoner: GeminiFlashDiscrepancyReasoner


def get_registry() -> AIRegistry:
    # Debug: Print all relevant env variables for plugin selection
    use_gemini_env = os.getenv("USE_GEMINI_PLUGINS")
    gemini_api_key_env = os.getenv("GEMINI_API_KEY")
    gemini_model_env = os.getenv("GEMINI_MODEL")
    print(f"[AIRegistry] USE_GEMINI_PLUGINS={use_gemini_env}, GEMINI_API_KEY={'set' if gemini_api_key_env else 'not set'}, GEMINI_MODEL={gemini_model_env}")
    use_gemini = (use_gemini_env or "false").lower() == "true"
    print(f"AI Registry - Using Gemini Plugins: {use_gemini}")
    use_gemini = True  # Force Gemini usage for all plugins


    if not use_gemini:
        return AIRegistry(
            ocr=MockOCR(),
            translation=MockTranslation(),
            classifier=MockDocClassifier(),
            extractor=MockFieldExtractor(),
            reasoner=MockDiscrepancyReasoner(),
        )

    gemini_api_key = os.getenv("GEMINI_API_KEY")
    model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    client = GeminiClient(api_key=gemini_api_key, model=model)

    ocr = DefaultOCRPlugin()
    translation = GeminiTranslationPlugin(client)
    classifier = GeminiDocClassifierPlugin(client)

    return AIRegistry(
        ocr=ocr,
        translation=translation,
        classifier=classifier,
        extractor=GeminiFlashFieldExtractor(client),
        reasoner=GeminiFlashDiscrepancyReasoner(client),
    )
    """
