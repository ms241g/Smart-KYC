from api.client import get
import logging

logger = logging.getLogger(__name__)


def list_categories():
    print("Fetching KYC categories")
    return get("/v1/policies/categories")

def get_requirements(category_id: str, country: str, risk_tier: str):
    return get(
        f"/v1/policies/{category_id}/requirements",
        params={"country": country, "risk_tier": risk_tier}
    )
