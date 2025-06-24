#!/usr/bin/env python3
"""
Script to setup test database for PyTasks API.

This script creates the test database if it doesn't exist and sets up
the necessary tables for running tests.
"""

import asyncio
import sys

import asyncpg

from app.config import get_settings
from app.infrastructure.database.test_connection import (
    create_test_tables,
    drop_test_tables,
    test_engine,
)


async def database_exists(database_name: str, connection_params: dict) -> bool:
    """Check if database exists."""
    try:
        # Connect to postgres database to check if target database exists
        conn_params = connection_params.copy()
        conn_params["database"] = "postgres"

        conn = await asyncpg.connect(**conn_params)
        try:
            result = await conn.fetchval(
                "SELECT 1 FROM pg_database WHERE datname = $1", database_name
            )
            return result is not None
        finally:
            await conn.close()
    except Exception as e:
        print(f"Error checking database existence: {e}")
        return False


async def create_database(database_name: str, connection_params: dict) -> bool:
    """Create database if it doesn't exist."""
    try:
        # Connect to postgres database to create target database
        conn_params = connection_params.copy()
        conn_params["database"] = "postgres"

        conn = await asyncpg.connect(**conn_params)
        try:
            await conn.execute(f'CREATE DATABASE "{database_name}"')
            print(f"✅ Database '{database_name}' created successfully")
            return True
        finally:
            await conn.close()
    except asyncpg.DuplicateDatabaseError:
        print(f"ℹ️  Database '{database_name}' already exists")
        return True
    except Exception as e:
        print(f"❌ Error creating database '{database_name}': {e}")
        return False


async def drop_database(database_name: str, connection_params: dict) -> bool:
    """Drop database if it exists."""
    try:
        # Connect to postgres database to drop target database
        conn_params = connection_params.copy()
        conn_params["database"] = "postgres"

        conn = await asyncpg.connect(**conn_params)
        try:
            # Terminate existing connections to the database
            await conn.execute(
                """
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = $1 AND pid <> pg_backend_pid()
                """,
                database_name,
            )

            await conn.execute(f'DROP DATABASE IF EXISTS "{database_name}"')
            print(f"✅ Database '{database_name}' dropped successfully")
            return True
        finally:
            await conn.close()
    except Exception as e:
        print(f"❌ Error dropping database '{database_name}': {e}")
        return False


def parse_database_url(url: str) -> tuple[str, dict]:
    """Parse database URL to extract database name and connection parameters."""
    # Example: postgresql://user:password@host:port/database
    if not url.startswith("postgresql://"):
        raise ValueError("Invalid PostgreSQL URL")

    # Remove protocol
    url = url[13:]  # Remove 'postgresql://'

    # Split user:password@host:port/database
    if "@" in url:
        auth_part, host_part = url.split("@", 1)
        if ":" in auth_part:
            user, password = auth_part.split(":", 1)
        else:
            user, password = auth_part, None
    else:
        user, password = None, None
        host_part = url

    # Split host:port/database
    if "/" in host_part:
        host_port, database = host_part.split("/", 1)
    else:
        raise ValueError("Database name not found in URL")

    # Split host:port
    if ":" in host_port:
        host, port = host_port.split(":", 1)
        port = int(port)
    else:
        host, port = host_port, 5432

    connection_params = {
        "host": host,
        "port": port,
    }

    if user:
        connection_params["user"] = user
    if password:
        connection_params["password"] = password

    return database, connection_params


async def setup_test_database() -> bool:
    """Set up test database and tables."""
    settings = get_settings()
    test_db_url = settings.DATABASE_URL

    if not test_db_url:
        print("❌ DATABASE_URL not configured")
        return False

    try:
        database_name, connection_params = parse_database_url(str(test_db_url))
        print(f"🔧 Setting up test database: {database_name}")

        # Check if database exists, create if not
        if not await database_exists(database_name, connection_params):
            if not await create_database(database_name, connection_params):
                return False
        else:
            print(f"ℹ️  Database '{database_name}' already exists")

        # Create tables
        print("🔧 Creating test tables...")
        await create_test_tables()
        print("✅ Test tables created successfully")

        return True

    except Exception as e:
        print(f"❌ Error setting up test database: {e}")
        return False
    finally:
        # Close the test engine
        await test_engine.dispose()


async def teardown_test_database() -> bool:
    """Teardown test database."""
    settings = get_settings()
    test_db_url = settings.DATABASE_URL

    if not test_db_url:
        print("❌ DATABASE_URL not configured")
        return False

    try:
        database_name, connection_params = parse_database_url(str(test_db_url))
        print(f"🧹 Tearing down test database: {database_name}")

        # Drop tables first
        print("🧹 Dropping test tables...")
        await drop_test_tables()
        print("✅ Test tables dropped successfully")

        return True

    except Exception as e:
        print(f"❌ Error tearing down test database: {e}")
        return False
    finally:
        # Close the test engine
        await test_engine.dispose()


async def reset_test_database() -> bool:
    """Reset test database (drop and recreate)."""
    settings = get_settings()
    test_db_url = settings.DATABASE_URL

    if not test_db_url:
        print("❌ DATABASE_URL not configured")
        return False

    try:
        database_name, connection_params = parse_database_url(str(test_db_url))
        print(f"🔄 Resetting test database: {database_name}")

        # Drop database
        await drop_database(database_name, connection_params)

        # Create database
        if not await create_database(database_name, connection_params):
            return False

        # Create tables
        print("🔧 Creating test tables...")
        await create_test_tables()
        print("✅ Test database reset successfully")

        return True

    except Exception as e:
        print(f"❌ Error resetting test database: {e}")
        return False
    finally:
        # Close the test engine
        await test_engine.dispose()


def main():
    """Handle command line arguments."""
    if len(sys.argv) < 2:
        print("Usage: python setup_test_db.py [setup|teardown|reset]")
        sys.exit(1)

    command = sys.argv[1].lower()

    if command == "setup":
        success = asyncio.run(setup_test_database())
    elif command == "teardown":
        success = asyncio.run(teardown_test_database())
    elif command == "reset":
        success = asyncio.run(reset_test_database())
    else:
        print(f"Unknown command: {command}")
        print("Available commands: setup, teardown, reset")
        sys.exit(1)

    if not success:
        sys.exit(1)

    print("🎉 Operation completed successfully!")


if __name__ == "__main__":
    main()
