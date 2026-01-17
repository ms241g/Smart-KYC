from typing import Protocol
from app.ai.contracts.inputs import EvidenceInput
from app.ai.contracts.outputs import OCRResult


class OCRPlugin(Protocol):
    async def run(self, evidence: EvidenceInput) -> OCRResult:
        """Extract text from evidence file."""
        ...
