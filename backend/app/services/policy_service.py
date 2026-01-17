from app.schemas.policy import CategoryListResponse, KYCCategory, PolicyRequirementsResponse


class PolicyService:
    """
    In production: backed by policy DB + versioned rules.
    """

    async def list_categories(self) -> CategoryListResponse:
        categories = [
            KYCCategory(id="cip", title="CIP", description="Customer Identification Program"),
            KYCCategory(id="address_verification", title="Address Verification", description="Proof of address verification"),
            KYCCategory(id="kyb", title="KYB", description="Business verification"),
            KYCCategory(id="periodic_refresh", title="Periodic KYC Refresh", description="Periodic verification update"),
            KYCCategory(id="edd", title="EDD", description="Enhanced Due Diligence"),
        ]
        return CategoryListResponse(categories=categories)

    async def get_requirements(self, category_id: str, country: str, risk_tier: str) -> PolicyRequirementsResponse:
        # Stub – later read from DB
        return PolicyRequirementsResponse(
            category_id=category_id,
            policy_version="v1.0",
            required_fields=["full_name", "dob", "citizenship", "address"],
            required_documents=["passport", "drivers_license"],
            rules={"dob_mismatch": "hard_fail", "address_mismatch": "secondary_doc_allowed"},
        )
