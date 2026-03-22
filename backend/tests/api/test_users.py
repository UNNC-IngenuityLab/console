"""User management API tests."""

import pytest
from httpx import AsyncClient
from decimal import Decimal


pytestmark = pytest.mark.asyncio


class TestListUsers:
    """Test list users endpoint."""

    async def test_list_users_success(self, authenticated_client: AsyncClient):
        """Test successful user list retrieval."""
        response = await authenticated_client.get("/api/v1/users/")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "items" in data["data"]
        assert "total" in data["data"]
        assert "page" in data["data"]

    async def test_list_users_with_pagination(self, authenticated_client: AsyncClient):
        """Test user list with pagination."""
        response = await authenticated_client.get(
            "/api/v1/users/", params={"page": 1, "page_size": 10}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["page"] == 1
        assert data["data"]["page_size"] == 10

    async def test_list_users_with_search(self, authenticated_client: AsyncClient, sample_user: dict):
        """Test user list with search filter."""
        response = await authenticated_client.get(
            "/api/v1/users/", params={"search": "20240001"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0

    async def test_list_users_with_level_filter(self, authenticated_client: AsyncClient):
        """Test user list filtered by level."""
        response = await authenticated_client.get(
            "/api/v1/users/", params={"level": 3}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0

    async def test_list_users_with_sorting(self, authenticated_client: AsyncClient):
        """Test user list with sorting."""
        response = await authenticated_client.get(
            "/api/v1/users/", params={"sort_by": "total_points", "sort_order": "DESC"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0

    async def test_list_users_without_auth(self, client: AsyncClient):
        """Test listing users without authentication."""
        response = await client.get("/api/v1/users/")

        assert response.status_code == 401


class TestGetUser:
    """Test get user endpoint."""

    async def test_get_user_success(
        self, authenticated_client: AsyncClient, sample_user: dict
    ):
        """Test successful user retrieval."""
        response = await authenticated_client.get(f"/api/v1/users/{sample_user['id']}")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["id"] == sample_user["id"]

    async def test_get_user_not_found(self, authenticated_client: AsyncClient):
        """Test getting non-existent user."""
        response = await authenticated_client.get("/api/v1/users/nonexistentid")

        assert response.status_code == 404

    async def test_get_user_without_auth(self, client: AsyncClient, sample_user: dict):
        """Test getting user without authentication."""
        response = await client.get(f"/api/v1/users/{sample_user['id']}")

        assert response.status_code == 401


class TestUpdateUserPoints:
    """Test update user points endpoint."""

    async def test_update_points_success(
        self, authenticated_client: AsyncClient, sample_user: dict
    ):
        """Test successful points update."""
        response = await authenticated_client.put(
            f"/api/v1/users/{sample_user['id']}/points",
            json={"points": Decimal("75.5"), "reason": "Test points update"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "old_points" in data["data"]
        assert "new_points" in data["data"]
        assert data["data"]["new_points"] == "75.5"

    async def test_update_points_invalid_negative(self, authenticated_client: AsyncClient, sample_user: dict):
        """Test updating points with negative value."""
        response = await authenticated_client.put(
            f"/api/v1/users/{sample_user['id']}/points",
            json={"points": Decimal("-10"), "reason": "Test"},
        )

        assert response.status_code == 422  # Validation error

    async def test_update_points_missing_reason(self, authenticated_client: AsyncClient, sample_user: dict):
        """Test updating points without reason."""
        response = await authenticated_client.put(
            f"/api/v1/users/{sample_user['id']}/points",
            json={"points": Decimal("50")},
        )

        assert response.status_code == 422

    async def test_update_points_user_not_found(self, authenticated_client: AsyncClient):
        """Test updating points for non-existent user."""
        response = await authenticated_client.put(
            "/api/v1/users/nonexistentid/points",
            json={"points": Decimal("50"), "reason": "Test"},
        )

        assert response.status_code == 404


class TestUpdateUser:
    """Test update user endpoint."""

    async def test_update_user_success(
        self, authenticated_client: AsyncClient, sample_user: dict
    ):
        """Test successful user update."""
        response = await authenticated_client.put(
            f"/api/v1/users/{sample_user['id']}",
            json={"nickname": "Updated Name", "level": 4},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0

    async def test_update_user_deactivate(
        self, authenticated_client: AsyncClient, sample_user: dict
    ):
        """Test deactivating a user."""
        response = await authenticated_client.put(
            f"/api/v1/users/{sample_user['id']}",
            json={"is_active": False},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0

    async def test_update_user_not_found(self, authenticated_client: AsyncClient):
        """Test updating non-existent user."""
        response = await authenticated_client.put(
            "/api/v1/users/nonexistentid",
            json={"nickname": "Test"},
        )

        assert response.status_code == 404


class TestDeleteUser:
    """Test delete user endpoint."""

    async def test_delete_user_success(self, authenticated_client: AsyncClient):
        """Test successful user deletion."""
        from app.core.security import generate_object_id, get_password_hash
        from app.config import settings
        from aiomysql import connect

        # Create a temporary user
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
                INSERT INTO users (id, openid, student_id, password, security_question, security_answer, total_points, level, is_active)
                VALUES ('{user_id}', 'temp_openid', 'temp001', '{hashed_password}', 'test', 'test', 0, 1, 1)
                """
            )
        await conn.commit()
        await conn.close()

        # Delete the user
        response = await authenticated_client.delete(f"/api/v1/users/{user_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0

    async def test_delete_user_not_found(self, authenticated_client: AsyncClient):
        """Test deleting non-existent user."""
        response = await authenticated_client.delete("/api/v1/users/nonexistentid")

        assert response.status_code == 404
