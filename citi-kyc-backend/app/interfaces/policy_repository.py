from typing import Protocol

class PolicyRepository(Protocol):
    async def get_category_rules(self, category_id: str) -> dict:
        ...
    async def get_policy_version(self, category_id: str, country: str, risk_tier: str) -> str:
        ...
