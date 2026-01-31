from app.ai.contracts.inputs import EvidenceInput
from app.ai.contracts.outputs import OCRResult
from app.services.ocr_service import OCRService, TesseractOCRProvider


class DefaultOCRPlugin:
    def __init__(self):
        self.service = OCRService(provider=TesseractOCRProvider())

    async def run(self, evidence: EvidenceInput) -> OCRResult:
        return await self.service.run(evidence)
