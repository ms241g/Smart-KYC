from __future__ import annotations
from typing import Dict, List

from app.schemas.policy import CategoryListResponse, KYCCategory, PolicyRequirementsResponse


CATEGORY_RULES: Dict[str, dict] = {
    "cip": {
        "allowed_doc_types": ["passport", "drivers_license", "national_id"],
        "extraction_fields": [
            "full_name", "dob", "citizenship",
            "address.line1", "address.line2", "address.city", "address.state", "address.postal_code", "address.country",
            "document_number", "issuing_country", "issue_date", "expiry_date"
        ],
    },
    "address_verification": {
        "allowed_doc_types": ["utility_bill", "bank_statement", "rent_agreement"],
        "extraction_fields": [
            "full_name",
            "address.line1", "address.line2", "address.city", "address.state", "address.postal_code", "address.country",
            "issue_date"
        ],
    },
    "kyb": {
        "allowed_doc_types": ["certificate_incorporation", "dba", "tax_registration"],
        "extraction_fields": [
            "business_name", "registration_id", "incorporation_date",
            "address.line1", "address.line2", "address.city", "address.state", "address.postal_code", "address.country"
        ],
    },
    "periodic_refresh": {
        "allowed_doc_types": ["passport", "drivers_license", "national_id", "utility_bill", "bank_statement"],
        "extraction_fields": [
            "full_name", "dob",
            "address.line1", "address.line2", "address.city", "address.state", "address.postal_code", "address.country"
        ],
    },
    "edd": {
        "allowed_doc_types": ["passport", "drivers_license", "national_id", "utility_bill", "bank_statement", "sof_declaration"],
        "extraction_fields": [
            "full_name", "dob", "citizenship",
            "address.line1", "address.line2", "address.city", "address.state", "address.postal_code", "address.country",
            "source_of_funds", "source_of_wealth"
        ],
    },
}


class PolicyService:
    async def list_categories(self) -> CategoryListResponse:
        categories = [
            KYCCategory(id="cip", title="CIP", description="Customer Identification Program (Individual identity verification)"),
            KYCCategory(id="address_verification", title="Address Verification", description="Proof of address verification"),
            KYCCategory(id="kyb", title="KYB", description="Business verification"),
            KYCCategory(id="periodic_refresh", title="Periodic KYC Refresh", description="Periodic verification update"),
            KYCCategory(id="edd", title="EDD", description="Enhanced Due Diligence"),
        ]
        print(f"Available categories: {[c.id for c in categories]}")
        return CategoryListResponse(categories=categories)

    async def get_requirements(self, category_id: str, country: str, risk_tier: str) -> PolicyRequirementsResponse:
        rules = CATEGORY_RULES.get(category_id)
        if not rules:
            # safe default
            rules = {"allowed_doc_types": [], "extraction_fields": []}

        return PolicyRequirementsResponse(
            category_id=category_id,
            policy_version="v1.0",
            required_fields=self._required_fields_for_category(category_id),
            required_documents=rules.get("allowed_doc_types", []),
            rules={
                "allowed_doc_types": rules.get("allowed_doc_types", []),
                "extraction_fields": rules.get("extraction_fields", []),
                # Common controls
                "dob_mismatch": "hard_fail",
                "address_mismatch": "secondary_doc_allowed",
            },
        )

    async def get_category_rules(self, category_id: str) -> dict:
        return CATEGORY_RULES.get(category_id, {"allowed_doc_types": [], "extraction_fields": []})

    def _required_fields_for_category(self, category_id: str) -> List[str]:
        if category_id == "kyb":
            return ["business_name", "registration_id", "country_of_registration", "address"]
        if category_id == "edd":
            return ["full_name", "dob", "citizenship", "address", "source_of_funds"]
        return ["full_name", "dob", "citizenship", "address"]
