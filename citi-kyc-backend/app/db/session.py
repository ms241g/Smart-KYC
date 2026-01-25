from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings
from typing import AsyncGenerator

db_dsn = settings.postgresql_dsn
print("Database DSN:", db_dsn)
engine = create_async_engine(settings.postgresql_dsn, echo=False, pool_pre_ping=True)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    print("Creating new database session")
    async with AsyncSessionLocal() as session:
        yield session
