"""
Pytest configuration and shared fixtures.

Environment variables must be set before any app module is imported,
because app.config.settings is evaluated at module load time.

Tests use httpx.AsyncClient with ASGITransport (requires pytest-asyncio).
All test functions are async; asyncio_mode = "auto" is configured in pyproject.toml.
"""

import os

# Set test environment variables BEFORE importing any app modules
os.environ.setdefault("DB_HOST", "localhost")
os.environ.setdefault("DB_PORT", "3306")
os.environ.setdefault("DB_NAME", "ingenuity_lab_test")
os.environ.setdefault("DB_USER", "root")
os.environ.setdefault("DB_PASSWORD", "test_password")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-testing-only-minimum-32-chars")
os.environ.setdefault("ENVIRONMENT", "test")

from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import httpx
import pytest

from app.config import get_settings
from app.dependencies import get_admin_log_repo, get_admin_user, get_db_connection
from app.main import app

# Clear lru_cache so settings reload from our test env vars
get_settings.cache_clear()


# =============================================================================
# Mock data constants
# =============================================================================

MOCK_ADMIN_USER = {
    "id": "user123abc456def7890ab12",
    "student_id": "N20230001",
    "openid": "openid_test_admin_123",
    "nickname": "Test Admin",
    "avatar_url": None,
    "total_points": Decimal("15.00"),
    "level": 3,
    "is_active": True,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00",
}

MOCK_USER = {
    "id": "usr456abc789def0123ab45",
    "student_id": "N20230002",
    "openid": "openid_test_user_456",
    "nickname": "Test Student",
    "avatar_url": "https://example.com/avatar.png",
    "total_points": Decimal("25.00"),
    "level": 4,
    "is_active": True,
    "created_at": "2024-01-02T00:00:00",
    "updated_at": "2024-01-02T00:00:00",
}

MOCK_ACTIVITY = {
    "id": "act123abc456def789ab123",
    "activity_id": 1704067200000,
    "creator_openid": "openid_test_admin_123",
    "name": "Test Activity",
    "venue": "Main Hall",
    "start_date": "2024-01-15T09:00:00",
    "end_date": "2024-01-15T17:00:00",
    "total_point": Decimal("10.00"),
    "sign_up_count": 5,
    "completed_count": 3,
    "is_active": True,
    "sub_activity_count": 2,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00",
}

MOCK_USER_ACTIVITY = {
    "id": "ra123abc456def789ab12",
    "activity_id": "act123abc456def789ab123",
    "activity_name": "Test Activity",
    "venue": "Main Hall",
    "is_completed": True,
    "points_earned": Decimal("10.00"),
    "registered_at": "2024-01-15T08:30:00",
    "completed_at": "2024-01-15T17:00:00",
}

MOCK_SUB_ACTIVITY = {
    "id": 1,
    "activity_id": "act123abc456def789ab123",
    "name": "Sub Activity 1",
    "point": Decimal("5.00"),
    "is_stopped": False,
    "sort_order": 0,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00",
}

MOCK_ANNOUNCEMENT = {
    "id": "ann123abc456def789ab123",
    "creator_openid": "openid_test_admin_123",
    "title": "Test Announcement",
    "content": "This is test announcement content.",
    "is_active": True,
    "priority": 1,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00",
}

MOCK_LEVEL_CONFIG = {
    "id": 1,
    "level": 1,
    "name": "车库小店",
    "name_en": "Garage Shop",
    "name_zh_tw": None,
    "min_score": Decimal("0.00"),
    "max_score": Decimal("10.00"),
    "icon_url": "/assets/level-1.png",
    "icon_dark_url": None,
    "bg_color": "#FF5722",
    "bg_gradient_start": None,
    "bg_gradient_end": None,
    "description": "Starting level",
    "description_en": None,
    "animation_type": "none",
    "sound_url": None,
    "is_active": True,
    "sort_order": 0,
    "created_at": "2024-01-01T00:00:00",
    "updated_at": "2024-01-01T00:00:00",
}

MOCK_SETTINGS = {
    "id": "settings_main_001",
    "qr_code_expiration_seconds": 300,
    "max_points_per_activity": Decimal("100.00"),
    "max_points_per_sub_activity": Decimal("50.00"),
    "registration_open": True,
    "new_user_initial_points": Decimal("0.00"),
    "leaderboard_top_n": 50,
    "leaderboard_refresh_interval_seconds": 60,
    "activities_per_page": 20,
    "scan_rate_limit_per_minute": 10,
    "maintenance_mode": False,
    "maintenance_message": None,
    "updated_at": "2024-01-01T00:00:00",
}

PAGINATED_RESULT_TEMPLATE = {
    "items": [],
    "total": 0,
    "page": 1,
    "page_size": 20,
    "total_pages": 0,
}


# =============================================================================
# Fixtures
# =============================================================================

@pytest.fixture
def mock_log_repo():
    """Mock AdminLogRepository that does nothing."""
    repo = AsyncMock()
    repo.create = AsyncMock(return_value=1)
    return repo


@pytest.fixture
async def client(mock_log_repo):
    """
    Async test client with mocked auth and DB dependencies.
    Uses httpx.AsyncClient with ASGITransport — no real DB needed.
    The lifespan does NOT run (intentional: all deps are overridden).
    """
    async def override_get_admin_user():
        return MOCK_ADMIN_USER

    async def override_get_db_connection():
        yield MagicMock()

    async def override_get_admin_log_repo():
        return mock_log_repo

    app.dependency_overrides[get_admin_user] = override_get_admin_user
    app.dependency_overrides[get_db_connection] = override_get_db_connection
    app.dependency_overrides[get_admin_log_repo] = override_get_admin_log_repo

    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as c:
        yield c

    app.dependency_overrides = {}


@pytest.fixture
async def client_no_auth():
    """
    Async test client WITHOUT auth override — used to test unauthorized access.
    No dependency overrides, so JWT validation runs normally.
    """
    async with httpx.AsyncClient(
        transport=httpx.ASGITransport(app=app),
        base_url="http://testserver",
    ) as c:
        yield c
