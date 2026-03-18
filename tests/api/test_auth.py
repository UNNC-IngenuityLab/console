"""Authentication API tests."""

import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.asyncio


class TestLogin:
    """Test login endpoint."""

    async def test_login_success(self, client: AsyncClient, sample_user: dict):
        """Test successful login."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"student_id": "20240001", "password": "password123"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "access_token" in data["data"]
        assert data["data"]["token_type"] == "bearer"
        assert "user" in data["data"]
        assert data["data"]["user"]["student_id"] == "20240001"

    async def test_login_invalid_credentials(self, client: AsyncClient):
        """Test login with invalid credentials."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"student_id": "99999999", "password": "wrongpassword"},
        )

        assert response.status_code == 401

    async def test_login_missing_fields(self, client: AsyncClient):
        """Test login with missing required fields."""
        response = await client.post(
            "/api/v1/auth/login",
            json={"student_id": "20240001"},  # Missing password
        )

        assert response.status_code == 422  # Validation error

    async def test_login_disabled_user(self, client: AsyncClient):
        """Test login with disabled user account."""
        from app.core.security import get_password_hash, generate_object_id
        from app.config import settings
        from aiomysql import connect

        # Create disabled user
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
                VALUES ('{user_id}', 'disabled_openid', 'disabled001', '{hashed_password}', 'test', 'test', 0, 1, 0)
                """
            )
        await conn.commit()
        await conn.close()

        response = await client.post(
            "/api/v1/auth/login",
            json={"student_id": "disabled001", "password": "password123"},
        )

        assert response.status_code == 401


class TestLogout:
    """Test logout endpoint."""

    async def test_logout_success(self, authenticated_client: AsyncClient):
        """Test successful logout."""
        response = await authenticated_client.post("/api/v1/auth/logout")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["message"] == "Logged out successfully"

    async def test_logout_without_auth(self, client: AsyncClient):
        """Test logout without authentication."""
        response = await client.post("/api/v1/auth/logout")

        # Logout is stateless for JWT, so it should still work
        assert response.status_code == 200


class TestGetCurrentUser:
    """Test get current user endpoint."""

    async def test_get_current_user_success(
        self, authenticated_client: AsyncClient, sample_user: dict
    ):
        """Test getting current user info."""
        response = await authenticated_client.get("/api/v1/auth/me")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "user" in data["data"]

    async def test_get_current_user_without_auth(self, client: AsyncClient):
        """Test getting current user without authentication."""
        response = await client.get("/api/v1/auth/me")

        assert response.status_code == 401
