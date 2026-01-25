from typing import Protocol

class HumanReviewAdapter(Protocol):
    async def create_review_task(self, case_id: str, payload: dict) -> str:
        ...
