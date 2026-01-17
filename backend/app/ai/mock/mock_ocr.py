from app.ai.contracts.inputs import EvidenceInput
from app.ai.contracts.outputs import OCRResult, OCRTextBlock, ConfidenceScore


class MockOCR:
    async def run(self, evidence: EvidenceInput) -> OCRResult:
        fake_text = f"Mock OCR text for {evidence.file_name}"
        return OCRResult(
            language="en",
            text_blocks=[OCRTextBlock(page=1, text=fake_text)],
            raw_text=fake_text,
            confidence=ConfidenceScore(value=0.85, reason="mock_ocr"),
        )
