from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "citi-kyc-backend"

    # DB
    #postgres_dsn: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/kyc"
    postgresql_dsn: str = "postgresql+asyncpg://postgres:Test123@localhost:5432/kyc_case_db"

    # Redis / Celery
    redis_broker_url: str = "sqla+sqlite:///celery_broker.sqlite"
    redis_backend_url: str = "db+sqlite:///celery_results.sqlite"

    # Evidence storage (S3 compatible)
    s3_region: str = "us-east-1"
    s3_bucket: str = "citi-kyc-evidence"
    s3_endpoint_url: str | None = None  # for MinIO/local
    s3_access_key_id: str | None = ""
    s3_secret_access_key: str | None = ""
    s3_url_expiry_seconds: int = 900  # 15 min

    # Customer profile service (adapter)
    customer_profile_base_url: str = "http://customer-profile-service:8080"

    # Environment
    environment: str = "local"

    class Config:
        env_file = ".env"

settings = Settings()
