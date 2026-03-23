"""Tests for Analytics API endpoints (/api/v1/analytics/*)."""

from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.dependencies import get_db_connection
from app.main import app

BASE = "/api/v1/analytics"


# =============================================================================
# Helpers to mock conn.cursor() as async context manager
# =============================================================================

def make_async_cursor(fetchone_returns=None, fetchall_returns=None):
    cursor = AsyncMock()
    cursor.execute = AsyncMock()
    if fetchone_returns is not None:
        cursor.fetchone = AsyncMock(side_effect=list(fetchone_returns))
    if fetchall_returns is not None:
        cursor.fetchall = AsyncMock(side_effect=list(fetchall_returns))
    return cursor


def make_conn_with_cursor(cursor):
    """Wrap a cursor in a mock conn supporting `async with conn.cursor(...) as c:`"""
    cm = AsyncMock()
    cm.__aenter__ = AsyncMock(return_value=cursor)
    cm.__aexit__ = AsyncMock(return_value=False)

    conn = MagicMock()
    conn.cursor = MagicMock(return_value=cm)
    return conn


def override_analytics_conn(conn):
    """Override get_db_connection with the given mock conn for analytics tests."""
    async def _override():
        yield conn

    app.dependency_overrides[get_db_connection] = _override


# =============================================================================
# GET /api/v1/analytics/dashboard
# =============================================================================

class TestDashboard:
    async def test_dashboard_success(self, client):
        fetchone_returns = [
            {"count": 120},    # total_users
            {"count": 15},     # total_activities
            {"count": 8},      # active_activities
            {"total": 450},    # total_signups
            {"total": 320},    # total_completions
            {"avg_rate": 71.1},
            {"total": Decimal("1580.00")},
        ]
        cursor = make_async_cursor(fetchone_returns=fetchone_returns)
        override_analytics_conn(make_conn_with_cursor(cursor))

        response = await client.get(f"{BASE}/dashboard")

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["total_users"] == 120
        assert body["data"]["total_activities"] == 15
        assert body["data"]["active_activities"] == 8
        assert body["data"]["total_signups"] == 450

    async def test_dashboard_zero_values(self, client):
        fetchone_returns = [
            {"count": 0}, {"count": 0}, {"count": 0},
            {"total": None}, {"total": None},
            {"avg_rate": None}, {"total": None},
        ]
        cursor = make_async_cursor(fetchone_returns=fetchone_returns)
        override_analytics_conn(make_conn_with_cursor(cursor))

        response = await client.get(f"{BASE}/dashboard")

        assert response.status_code == 200
        assert response.json()["data"]["total_users"] == 0
        assert response.json()["data"]["avg_completion_rate"] == 0.0

    async def test_dashboard_unauthorized(self, client_no_auth):
        response = await client_no_auth.get(f"{BASE}/dashboard")
        assert response.status_code in (401, 403)


# =============================================================================
# GET /api/v1/analytics/activity-stats
# =============================================================================

class TestActivityStats:
    MOCK_ROWS = [
        {
            "activity_id": "act123abc456def789ab123",
            "activity_name": "Test Activity",
            "sign_up_count": 30,
            "completed_count": 22,
            "completion_rate": 73.3,
            "total_points": Decimal("220.00"),
        }
    ]

    async def test_activity_stats_success(self, client):
        cursor = make_async_cursor(fetchall_returns=[self.MOCK_ROWS])
        override_analytics_conn(make_conn_with_cursor(cursor))

        response = await client.get(f"{BASE}/activity-stats")

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["activity_name"] == "Test Activity"

    async def test_activity_stats_empty(self, client):
        cursor = make_async_cursor(fetchall_returns=[[]])
        override_analytics_conn(make_conn_with_cursor(cursor))

        response = await client.get(f"{BASE}/activity-stats")

        assert response.status_code == 200
        assert response.json()["data"] == []

    async def test_activity_stats_limit_too_large(self, client):
        response = await client.get(f"{BASE}/activity-stats", params={"limit": 200})
        assert response.status_code == 422


# =============================================================================
# GET /api/v1/analytics/trend
# =============================================================================

class TestTrend:
    async def test_trend_success(self, client):
        cursor = make_async_cursor(
            fetchall_returns=[
                [{"date": "2024-01-01", "new_users": 5}],
                [{"date": "2024-01-01", "new_signups": 10}],
                [{"date": "2024-01-01", "new_completions": 7, "points_awarded": Decimal("70.00")}],
            ]
        )
        override_analytics_conn(make_conn_with_cursor(cursor))

        response = await client.get(f"{BASE}/trend", params={"days": 7})

        assert response.status_code == 200
        data = response.json()["data"]
        assert isinstance(data, list)
        assert len(data) == 7

    async def test_trend_empty_db(self, client):
        cursor = make_async_cursor(fetchall_returns=[[], [], []])
        override_analytics_conn(make_conn_with_cursor(cursor))

        response = await client.get(f"{BASE}/trend", params={"days": 7})

        assert response.status_code == 200
        for item in response.json()["data"]:
            assert item["new_users"] == 0

    async def test_trend_days_too_short(self, client):
        response = await client.get(f"{BASE}/trend", params={"days": 3})
        assert response.status_code == 422

    async def test_trend_days_too_long(self, client):
        response = await client.get(f"{BASE}/trend", params={"days": 500})
        assert response.status_code == 422


# =============================================================================
# GET /api/v1/analytics/leaderboard
# =============================================================================

class TestLeaderboard:
    MOCK_ROWS = [
        {
            "rank": 1,
            "user_id": "usr456abc789def0123ab45",
            "student_id": "N20230002",
            "nickname": "Top Student",
            "avatar_url": None,
            "total_points": Decimal("95.00"),
            "level": 7,
        }
    ]

    async def test_leaderboard_success(self, client):
        cursor = make_async_cursor(fetchall_returns=[self.MOCK_ROWS])
        override_analytics_conn(make_conn_with_cursor(cursor))

        response = await client.get(f"{BASE}/leaderboard")

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 1
        assert data[0]["rank"] == 1
        assert data[0]["student_id"] == "N20230002"

    async def test_leaderboard_empty(self, client):
        cursor = make_async_cursor(fetchall_returns=[[]])
        override_analytics_conn(make_conn_with_cursor(cursor))

        response = await client.get(f"{BASE}/leaderboard")

        assert response.status_code == 200
        assert response.json()["data"] == []

    async def test_leaderboard_limit_out_of_range(self, client):
        response = await client.get(f"{BASE}/leaderboard", params={"limit": 200})
        assert response.status_code == 422


# =============================================================================
# GET /api/v1/analytics/level-distribution
# =============================================================================

class TestLevelDistribution:
    async def test_level_distribution_success(self, client):
        cursor = make_async_cursor(
            fetchone_returns=[{"total": 120}],
            fetchall_returns=[
                [
                    {"level": 1, "level_name": "车库小店", "user_count": 40},
                    {"level": 2, "level_name": "城市小店", "user_count": 80},
                ]
            ],
        )
        override_analytics_conn(make_conn_with_cursor(cursor))

        response = await client.get(f"{BASE}/level-distribution")

        assert response.status_code == 200
        data = response.json()["data"]
        assert len(data) == 2
        assert data[0]["level"] == 1
        assert data[0]["percentage"] == round(40 / 120 * 100, 2)

    async def test_level_distribution_no_users(self, client):
        cursor = make_async_cursor(
            fetchone_returns=[{"total": 0}],
            fetchall_returns=[[]],
        )
        override_analytics_conn(make_conn_with_cursor(cursor))

        response = await client.get(f"{BASE}/level-distribution")

        assert response.status_code == 200
        assert response.json()["data"] == []
