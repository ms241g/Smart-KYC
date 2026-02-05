from dataclasses import dataclass
from typing import Any, Dict, Optional
import httpx
from dateutil import parser as date_parser
from app.core.config import settings

@dataclass
class NormalizedCustomerProfile:
    customer_id: str
    full_name: str
    dob: str  # ISO
    citizenship: str
    address: Dict[str, str]  # normalized

class CustomerProfileService:
    """
    Adapter for customer profile DB/service.
    In production: this will connect to Citi internal systems.
    """

    def __init__(self):
        self.base_url = settings.customer_profile_base_url

    async def fetch_customer_profile(self, customer_id: str) -> NormalizedCustomerProfile:
        """
        Fetch customer profile. If API unavailable, can fallback to mock (local env).
        """
        if settings.environment == "local":
            return self._mock_profile(customer_id)

        async with httpx.AsyncClient(timeout=8.0) as client:
            resp = await client.get(f"{self.base_url}/v1/customers/{customer_id}")
            resp.raise_for_status()
            data = resp.json()
            return self._normalize(data)

    def _normalize(self, data: Dict[str, Any]) -> NormalizedCustomerProfile:
        # Normalize DOB
        dob_iso = date_parser.parse(data["dob"]).date().isoformat()

        # Normalize address keys
        address = data.get("address", {})
        normalized_address = {
            "line1": address.get("line1", "").strip(),
            "line2": address.get("line2", "").strip(),
            "city": address.get("city", "").strip().lower(),
            "state": address.get("state", "").strip().lower(),
            "postal_code": address.get("postal_code", "").strip(),
            "country": address.get("country", "").strip().lower(),
        }

        return NormalizedCustomerProfile(
            customer_id=data["customer_id"],
            full_name=data["full_name"].strip(),
            dob=dob_iso,
            citizenship=data.get("citizenship", "").strip(),
            address=normalized_address,
        )

    def _mock_profile(self, customer_id: str) -> NormalizedCustomerProfile:
        """
        Local stub to allow backend to function end-to-end.
        """
        data = {
            "customer_id": customer_id,
            "full_name": "MANOJ KUMAR SHARMA",
            "dob": "1983-02-06",
            "citizenship": "INDIAN",
            "address": {
                "line1": "T A 180 STREET NO 3",
                "line2": "TUGHALAKABAD EXTN",
                "city": "DELHI",
                "state": "DELHI",
                "postal_code": "110019",
                "country": "INDIA",
            },
        }
        return self._normalize(data)
