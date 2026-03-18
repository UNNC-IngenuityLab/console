"""Analytics API tests."""

import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.asyncio


class TestDashboardStats:
    """Test dashboard statistics endpoint."""

    async def test_get_dashboard_stats(self, authenticated_client: AsyncClient):
        """Test getting dashboard statistics."""
        response = await authenticated_client.get("/api/v1/analytics/dashboard")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "total_users" in data["data"]
        assert "total_activities" in data["data"]
        assert "active_activities" in data["data"]
        assert "total_signups" in data["data"]
        assert "total_completions" in data["data"]
        assert "avg_completion_rate" in data["data"]

    async def test_get_dashboard_stats_without_auth(self, client: AsyncClient):
        """Test getting dashboard stats without authentication."""
        response = await client.get("/api/v1/analytics/dashboard")

        assert response.status_code == 401


class TestActivityStats:
    """Test activity statistics endpoint."""

    async def test_get_activity_stats(self, authenticated_client: AsyncClient):
        """Test getting activity completion statistics."""
        response = await authenticated_client.get("/api/v1/analytics/activity-stats")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert isinstance(data["data"], list)

    async def test_get_activity_stats_with_limit(self, authenticated_client: AsyncClient):
        """Test getting activity stats with limit."""
        response = await authenticated_client.get(
            "/api/v1/analytics/activity-stats", params={"limit": 5}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0


class TestTrendData:
    """Test trend data endpoint."""

    async def test_get_trend_data(self, authenticated_client: AsyncClient):
        """Test getting user activity trend."""
        response = await authenticated_client.get("/api/v1/analytics/trend")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert isinstance(data["data"], list)

    async def test_get_trend_data_custom_days(self, authenticated_client: AsyncClient):
        """Test getting trend data with custom days."""
        response = await authenticated_client.get(
            "/api/v1/analytics/trend", params={"days": 7}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        # Should return 7 days of data
        assert len(data["data"]) <= 7


class TestLeaderboard:
    """Test leaderboard endpoint."""

    async def test_get_leaderboard(self, authenticated_client: AsyncClient):
        """Test getting leaderboard data."""
        response = await authenticated_client.get("/api/v1/analytics/leaderboard")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert isinstance(data["data"], list)

        # Check first entry structure
        if len(data["data"]) > 0:
            first_entry = data["data"][0]
            assert "rank" in first_entry
            assert "user_id" in first_entry
            assert "student_id" in first_entry
            assert "total_points" in first_entry
            assert "level" in first_entry

    async def test_get_leaderboard_with_limit(self, authenticated_client: AsyncClient):
        """Test getting leaderboard with custom limit."""
        response = await authenticated_client.get(
            "/api/v1/analytics/leaderboard", params={"limit": 10}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert len(data["data"]) <= 10


class TestLevelDistribution:
    """Test level distribution endpoint."""

    async def test_get_level_distribution(self, authenticated_client: AsyncClient):
        """Test getting level distribution."""
        response = await authenticated_client.get("/api/v1/analytics/level-distribution")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert isinstance(data["data"], list)

        # Check entry structure
        if len(data["data"]) > 0:
            first_entry = data["data"][0]
            assert "level" in first_entry
            assert "level_name" in first_entry
            assert "user_count" in first_entry
            assert "percentage" in first_entry
