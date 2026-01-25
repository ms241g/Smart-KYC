from typing import Protocol
from app.ai.contracts.inputs import CaseContextInput
from app.ai.contracts.outputs import ReasoningResult


class DiscrepancyReasonerPlugin(Protocol):
    async def reason(self, ctx: CaseContextInput) -> ReasoningResult:
        ...
