#!/usr/bin/env python3
"""Setup script for test database tables."""

import asyncio

from app.infrastructure.database.connection import Base
from tests.conftest import test_engine


async def setup_test_database():
    """Create all tables in the test database."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Test database tables created successfully")


if __name__ == "__main__":
    asyncio.run(setup_test_database())
