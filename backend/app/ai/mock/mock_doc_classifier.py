from app.ai.contracts.inputs import EvidenceInput
from app.ai.contracts.outputs import DocumentClassificationResult, ConfidenceScore


class MockDocClassifier:
    async def classify(self, evidence: EvidenceInput) -> DocumentClassificationResult:
        # naïve mapping just for skeleton
        name = evidence.file_name.lower()
        doc_type = "unknown"
        if "passport" in name:
            doc_type = "passport"
        elif "license" in name:
            doc_type = "drivers_license"
        elif "utility" in name:
            doc_type = "utility_bill"

        return DocumentClassificationResult(
            document_type=doc_type,
            confidence=ConfidenceScore(value=0.75, reason="mock_classifier"),
        )
