"""Test database connection configuration."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings
from app.infrastructure.database.connection import Base

# Create test async engine
test_engine = create_async_engine(
    str(settings.DATABASE_URL).replace("postgresql://", "postgresql+asyncpg://"),
    echo=False,  # Disable echo in tests for cleaner output
    future=True,
)

# Create test async session factory
TestAsyncSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_test_db_session() -> AsyncSession:
    """Get test database session.

    Yields:
        AsyncSession: Test database session
    """
    async with TestAsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def create_test_tables() -> None:
    """Create all test database tables."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def drop_test_tables() -> None:
    """Drop all test database tables."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def reset_test_database() -> None:
    """Reset test database by dropping and recreating all tables."""
    await drop_test_tables()
    await create_test_tables()
