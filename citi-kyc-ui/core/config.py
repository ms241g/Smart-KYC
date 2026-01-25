import os

BACKEND_BASE_URL = os.getenv("KYC_BACKEND_BASE_URL", "http://localhost:8000")
DEFAULT_COUNTRY = os.getenv("DEFAULT_COUNTRY", "IN")
DEFAULT_RISK_TIER = os.getenv("DEFAULT_RISK_TIER", "medium")
