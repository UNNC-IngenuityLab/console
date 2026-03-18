"""UI config and settings API tests."""

import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.asyncio


class TestGetUIConfig:
    """Test get UI config endpoints."""

    async def test_get_all_ui_configs(self, authenticated_client: AsyncClient):
        """Test getting all UI configurations."""
        response = await authenticated_client.get("/api/v1/config/ui")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        # Data is grouped by category
        assert isinstance(data["data"], dict)

    async def test_get_ui_config_by_category(self, authenticated_client: AsyncClient):
        """Test getting UI configs by category."""
        response = await authenticated_client.get("/api/v1/config/ui/category/general")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0

    async def test_get_ui_config_by_key(self, authenticated_client: AsyncClient):
        """Test getting single UI config by key."""
        response = await authenticated_client.get("/api/v1/config/ui/key/app.primary_color")

        # May or may not exist depending on initial data
        assert response.status_code in [200, 404]

    async def test_get_ui_config_without_auth(self, client: AsyncClient):
        """Test getting UI config without authentication."""
        response = await client.get("/api/v1/config/ui")

        assert response.status_code == 401


class TestUpdateUIConfig:
    """Test update UI config endpoints."""

    async def test_update_ui_config_success(self, authenticated_client: AsyncClient):
        """Test successful UI config update."""
        # First, ensure a config exists
        from app.config import settings
        from aiomysql import connect

        conn = await connect(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database="ingenuity_lab_test",
        )

        async with conn.cursor() as cursor:
            await cursor.execute(
                """
                INSERT INTO ui_configs (`key`, value, type, category, label)
                VALUES ('test.config', '"old value"', 'string', 'general', 'Test Config')
                ON DUPLICATE KEY UPDATE value = value
                """
            )
        await conn.commit()
        await conn.close()

        # Now update it
        response = await authenticated_client.put(
            "/api/v1/config/ui/test.config",
            json={"value": '"new value"'},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0

    async def test_update_ui_config_not_found(self, authenticated_client: AsyncClient):
        """Test updating non-existent UI config."""
        response = await authenticated_client.put(
            "/api/v1/config/ui/nonexistent.key",
            json={"value": "test"},
        )

        assert response.status_code == 404

    async def test_batch_update_ui_configs(self, authenticated_client: AsyncClient):
        """Test batch updating UI configs."""
        # First ensure test configs exist
        from app.config import settings
        from aiomysql import connect

        conn = await connect(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database="ingenuity_lab_test",
        )

        async with conn.cursor() as cursor:
            await cursor.execute(
                """
                INSERT INTO ui_configs (`key`, value, type, category, label)
                VALUES ('batch.test1', '"value1"', 'string', 'general', 'Test 1')
                ON DUPLICATE KEY UPDATE value = value
                """
            )
        await conn.commit()
        await conn.close()

        response = await authenticated_client.put(
            "/api/v1/config/ui/batch",
            json={"configs": {"batch.test1": '"updated value"'}},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0


class TestSystemSettings:
    """Test system settings endpoints."""

    async def test_get_system_settings(self, authenticated_client: AsyncClient):
        """Test getting system settings."""
        response = await authenticated_client.get("/api/v1/settings/")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["id"] == "system"
        assert "qr_code_expiration_seconds" in data["data"]

    async def test_get_system_settings_without_auth(self, client: AsyncClient):
        """Test getting system settings without authentication."""
        response = await client.get("/api/v1/settings/")

        assert response.status_code == 401

    async def test_update_system_settings(self, authenticated_client: AsyncClient):
        """Test updating system settings."""
        response = await authenticated_client.put(
            "/api/v1/settings/",
            json={
                "qr_code_expiration_seconds": 600,
                "maintenance_mode": False,
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0

    async def test_update_system_settings_invalid_value(self, authenticated_client: AsyncClient):
        """Test updating with invalid values."""
        response = await authenticated_client.put(
            "/api/v1/settings/",
            json={"qr_code_expiration_seconds": -100},
        )

        assert response.status_code == 422  # Validation error
