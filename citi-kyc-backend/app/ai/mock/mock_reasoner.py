from app.ai.contracts.inputs import CaseContextInput
from app.ai.contracts.outputs import ReasoningResult, DiscrepancyItem, ConfidenceScore


class MockDiscrepancyReasoner:
    async def reason(self, ctx: CaseContextInput) -> ReasoningResult:
        # This can become your LLM-based discrepancy reasoning layer
        return ReasoningResult(
            discrepancies=[],
            confidence=ConfidenceScore(value=0.8, reason="mock_reasoner"),
        )
