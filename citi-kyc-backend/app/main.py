from fastapi import FastAPI
from app.api.v1.router import api_router
from app.core.config import settings
#from app.core.logging import setup_logging

#setup_logging()

app = FastAPI(
    title="Citi KYC Backend",
    version="0.1.0",
    description="Backend for Citi KYC Initiation Portal (sync + async validation)",
)

app.include_router(api_router, prefix="/v1")


@app.get("/health")
def health():
    return {"status": "ok", "service": settings.app_name}
