"""Level configuration API tests."""

import pytest
from httpx import AsyncClient
from decimal import Decimal


pytestmark = pytest.mark.asyncio


class TestListLevels:
    """Test list levels endpoint."""

    async def test_list_levels_success(self, authenticated_client: AsyncClient):
        """Test successful level list retrieval."""
        response = await authenticated_client.get("/api/v1/levels/")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert isinstance(data["data"], list)

    async def test_list_levels_active_only(self, authenticated_client: AsyncClient):
        """Test listing only active levels."""
        response = await authenticated_client.get("/api/v1/levels/", params={"is_active": True})

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0

    async def test_list_levels_without_auth(self, client: AsyncClient):
        """Test listing levels without authentication."""
        response = await client.get("/api/v1/levels/")

        assert response.status_code == 401


class TestExportLevels:
    """Test export levels endpoint."""

    async def test_export_levels_success(self, authenticated_client: AsyncClient):
        """Test successful level export."""
        response = await authenticated_client.get("/api/v1/levels/export")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "levels" in data["data"]


class TestCreateLevel:
    """Test create level endpoint."""

    async def test_create_level_success(self, authenticated_client: AsyncClient):
        """Test successful level creation."""
        response = await authenticated_client.post(
            "/api/v1/levels/",
            json={
                "level": 11,
                "name": "Custom Level",
                "min_score": Decimal("100"),
                "bg_color": "#FF5722",
            },
        )

        assert response.status_code == 201 or response.status_code == 200
        data = response.json()
        assert data["code"] == 0

    async def test_create_level_duplicate(self, authenticated_client: AsyncClient):
        """Test creating level with duplicate level number."""
        # First creation should succeed
        await authenticated_client.post(
            "/api/v1/levels/",
            json={
                "level": 99,
                "name": "Test Level",
                "min_score": Decimal("200"),
            },
        )

        # Duplicate should fail
        response = await authenticated_client.post(
            "/api/v1/levels/",
            json={
                "level": 99,
                "name": "Duplicate Level",
                "min_score": Decimal("200"),
            },
        )

        assert response.status_code == 409

    async def test_create_level_missing_fields(self, authenticated_client: AsyncClient):
        """Test creating level with missing required fields."""
        response = await authenticated_client.post(
            "/api/v1/levels/",
            json={"name": "Incomplete Level"},
        )

        assert response.status_code == 422


class TestUpdateLevel:
    """Test update level endpoint."""

    async def test_update_level_success(self, authenticated_client: AsyncClient):
        """Test successful level update."""
        # First create a level
        create_response = await authenticated_client.post(
            "/api/v1/levels/",
            json={
                "level": 88,
                "name": "Update Test Level",
                "min_score": Decimal("150"),
            },
        )

        if create_response.status_code == 200:
            level_id = create_response.json()["data"]["level_id"]

            response = await authenticated_client.put(
                f"/api/v1/levels/{level_id}",
                json={"name": "Updated Level Name"},
            )

            assert response.status_code == 200

    async def test_update_level_not_found(self, authenticated_client: AsyncClient):
        """Test updating non-existent level."""
        response = await authenticated_client.put(
            "/api/v1/levels/99999",
            json={"name": "Updated"},
        )

        assert response.status_code == 404


class TestDeleteLevel:
    """Test delete level endpoint."""

    async def test_delete_level_success(self, authenticated_client: AsyncClient):
        """Test successful level deletion."""
        # First create a level
        create_response = await authenticated_client.post(
            "/api/v1/levels/",
            json={
                "level": 77,
                "name": "Delete Test Level",
                "min_score": Decimal("120"),
            },
        )

        if create_response.status_code == 200:
            level_id = create_response.json()["data"]["level_id"]

            response = await authenticated_client.delete(f"/api/v1/levels/{level_id}")

            assert response.status_code == 200

    async def test_delete_level_not_found(self, authenticated_client: AsyncClient):
        """Test deleting non-existent level."""
        response = await authenticated_client.delete("/api/v1/levels/99999")

        assert response.status_code == 404


class TestReorderLevels:
    """Test reorder levels endpoint."""

    async def test_reorder_levels_success(self, authenticated_client: AsyncClient):
        """Test successful level reordering."""
        response = await authenticated_client.put(
            "/api/v1/levels/reorder",
            json={"level_orders": {"1": 10, "2": 20, "3": 30}},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0

    async def test_reorder_levels_empty(self, authenticated_client: AsyncClient):
        """Test reordering with empty orders."""
        response = await authenticated_client.put(
            "/api/v1/levels/reorder",
            json={"level_orders": {}},
        )

        assert response.status_code == 200
