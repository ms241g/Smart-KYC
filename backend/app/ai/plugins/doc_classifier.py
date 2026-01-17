from typing import Protocol
from app.ai.contracts.inputs import EvidenceInput
from app.ai.contracts.outputs import DocumentClassificationResult


class DocumentClassifierPlugin(Protocol):
    async def classify(self, evidence: EvidenceInput) -> DocumentClassificationResult:
        ...
