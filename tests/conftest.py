"""Test configuration and fixtures."""

import asyncio
import os
from typing import AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

# Set test environment before importing app
os.environ["ENVIRONMENT"] = "test"
os.environ["DB_NAME"] = "ingenuity_lab_test"

from app.main import app
from app.config import settings
from tests.fixtures.mock_data import (
    generate_mock_user,
    generate_mock_activity,
    generate_mock_announcement,
    generate_mock_level_config,
)


# =============================================================================
# Test Database Setup
# =============================================================================

async def setup_test_database():
    """Set up test database schema."""
    from aiomysql import connect

    conn = await connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
    )
    async with conn.cursor() as cursor:
        # Create test database
        await cursor.execute(f"CREATE DATABASE IF NOT EXISTS ingenuity_lab_test")
        await cursor.execute("USE ingenuity_lab_test")

        # Read and execute schema
        schema_path = os.path.join(
            os.path.dirname(__file__), "../../db_migration/schema.sql"
        )
        with open(schema_path, "r") as f:
            schema_sql = f.read()

        # Split and execute statements
        for statement in schema_sql.split(";"):
            statement = statement.strip()
            if statement and not statement.startswith("--"):
                try:
                    # Skip VIEW and PROCEDURE creation for simpler testing
                    if any(keyword in statement.upper() for keyword in ["VIEW", "PROCEDURE", "TRIGGER"]):
                        continue
                    if "CREATE TABLE" in statement.upper() or "INSERT INTO" in statement.upper():
                        await cursor.execute(statement)
                except Exception as e:
                    # Ignore errors for optional schema elements
                    pass

    await conn.commit()
    await conn.close()


async def teardown_test_database():
    """Clean up test database."""
    from aiomysql import connect

    conn = await connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
    )
    async with conn.cursor() as cursor:
        await cursor.execute("DROP DATABASE IF EXISTS ingenuity_lab_test")
    await conn.commit()
    await conn.close()


# =============================================================================
# Pytest Fixtures
# =============================================================================

@pytest.fixture(scope="session")
def event_loop() -> Generator:
    """Create event loop for async tests."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="session")
async def database_setup():
    """Set up test database once per session."""
    await setup_test_database()
    yield
    await teardown_test_database()


@pytest_asyncio.fixture
async def client(database_setup) -> AsyncGenerator[AsyncClient, None]:
    """Create test HTTP client."""
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac


@pytest_asyncio.fixture
async def admin_token(client: AsyncClient) -> str:
    """Create admin user and return access token."""
    from app.core.security import get_password_hash, generate_object_id

    # Create admin user directly in database
    from aiomysql import connect

    conn = await connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database="ingenuity_lab_test",
    )

    user_id = generate_object_id()
    hashed_password = get_password_hash("admin123")

    async with conn.cursor() as cursor:
        await cursor.execute(
            f"""
            INSERT INTO users (id, openid, student_id, password, security_question, security_answer, total_points, level, is_active)
            VALUES ('{user_id}', 'admin_test_openid', 'admin001', '{hashed_password}', 'test question', 'test answer', 100, 5, 1)
            """
        )
    await conn.commit()
    await conn.close()

    # Login and get token
    response = await client.post(
        "/api/v1/auth/login", json={"student_id": "admin001", "password": "admin123"}
    )

    assert response.status_code == 200
    return response.json()["data"]["access_token"]


@pytest_asyncio.fixture
async def authenticated_client(client: AsyncClient, admin_token: str) -> AsyncClient:
    """Return client with auth headers set."""
    client.headers.update({"Authorization": f"Bearer {admin_token}"})
    return client


@pytest_asyncio.fixture
async def sample_user(client: AsyncClient) -> dict:
    """Create a sample user for testing."""
    from app.core.security import get_password_hash, generate_object_id
    from aiomysql import connect

    conn = await connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database="ingenuity_lab_test",
    )

    user_id = generate_object_id()
    hashed_password = get_password_hash("password123")

    async with conn.cursor() as cursor:
        await cursor.execute(
            f"""
            INSERT INTO users (id, openid, student_id, password, security_question, security_answer, nickname, total_points, level, is_active)
            VALUES ('{user_id}', 'test_openid_123', '20240001', '{hashed_password}', 'pet', 'fluffy', 'Test User', 50.5, 3, 1)
            """
        )
    await conn.commit()
    await conn.close()

    return {"id": user_id, "student_id": "20240001", "nickname": "Test User"}


@pytest_asyncio.fixture
async def sample_activity(client: AsyncClient) -> dict:
    """Create a sample activity for testing."""
    from app.core.security import generate_object_id
    from datetime import datetime
    from aiomysql import connect

    conn = await connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database="ingenuity_lab_test",
    )

    activity_id = generate_object_id()
    activity_timestamp_id = int(datetime.now().timestamp() * 1000)

    async with conn.cursor() as cursor:
        await cursor.execute(
            f"""
            INSERT INTO activities (id, activity_id, creator_openid, name, venue, date_range, start_date, end_date, total_point, sign_up_count, completed_count, is_active)
            VALUES ('{activity_id}', {activity_timestamp_id}, 'admin_test_openid', 'Test Activity', 'Test Venue', '2025.04.01 10:00~16:00', '2025-04-01', '2025-04-01', 20.0, 5, 3, 1)
            """
        )

        # Add sub-activities
        await cursor.execute(
            f"""
            INSERT INTO sub_activities (id, activity_id, name, point, is_stopped, sort_order)
            VALUES ({activity_timestamp_id + 1}, '{activity_id}', 'Check-in', 5.0, 0, 1)
            """
        )
        await cursor.execute(
            f"""
            INSERT INTO sub_activities (id, activity_id, name, point, is_stopped, sort_order)
            VALUES ({activity_timestamp_id + 2}, '{activity_id}', 'Main Event', 15.0, 0, 2)
            """
        )

    await conn.commit()
    await conn.close()

    return {"id": activity_id, "name": "Test Activity", "activity_id": activity_timestamp_id}


@pytest_asyncio.fixture
async def sample_announcement(client: AsyncClient) -> dict:
    """Create a sample announcement for testing."""
    from app.core.security import generate_object_id
    from aiomysql import connect

    conn = await connect(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_password,
        database="ingenuity_lab_test",
    )

    announcement_id = generate_object_id()

    async with conn.cursor() as cursor:
        await cursor.execute(
            f"""
            INSERT INTO announcements (id, creator_openid, title, content, is_active, priority)
            VALUES ('{announcement_id}', 'admin_test_openid', 'Test Announcement', 'This is a test announcement content.', 1, 5)
            """
        )

    await conn.commit()
    await conn.close()

    return {"id": announcement_id, "title": "Test Announcement"}
