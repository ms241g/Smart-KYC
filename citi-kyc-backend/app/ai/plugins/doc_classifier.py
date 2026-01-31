from app.ai.contracts.inputs import EvidenceInput
from app.ai.contracts.outputs import DocumentClassificationResult
from app.services.doc_classifier import GeminiDocClassifierService
from app.ai.gemini.client import GeminiClient


class GeminiDocClassifierPlugin:
    def __init__(self, client: GeminiClient):
        self.service = GeminiDocClassifierService(client)

    async def classify(self, evidence: EvidenceInput) -> DocumentClassificationResult:
        # OCR must run before classification
        from app.ai.registry import get_registry
        ocr = await get_registry().ocr.run(evidence)
        return await self.service.classify(ocr.raw_text)
