"""Announcement management API tests."""

import pytest
from httpx import AsyncClient


pytestmark = pytest.mark.asyncio


class TestListAnnouncements:
    """Test list announcements endpoint."""

    async def test_list_announcements_success(self, authenticated_client: AsyncClient):
        """Test successful announcement list retrieval."""
        response = await authenticated_client.get("/api/v1/announcements/")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "items" in data["data"]

    async def test_list_announcements_with_pagination(self, authenticated_client: AsyncClient):
        """Test announcement list with pagination."""
        response = await authenticated_client.get(
            "/api/v1/announcements/", params={"page": 1, "page_size": 10}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["page"] == 1

    async def test_list_announcements_with_active_filter(self, authenticated_client: AsyncClient):
        """Test announcement list filtered by active status."""
        response = await authenticated_client.get(
            "/api/v1/announcements/", params={"is_active": True}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0

    async def test_list_announcements_without_auth(self, client: AsyncClient):
        """Test listing announcements without authentication."""
        response = await client.get("/api/v1/announcements/")

        assert response.status_code == 401


class TestGetAnnouncement:
    """Test get announcement endpoint."""

    async def test_get_announcement_success(
        self, authenticated_client: AsyncClient, sample_announcement: dict
    ):
        """Test successful announcement retrieval."""
        response = await authenticated_client.get(f"/api/v1/announcements/{sample_announcement['id']}")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["id"] == sample_announcement["id"]

    async def test_get_announcement_not_found(self, authenticated_client: AsyncClient):
        """Test getting non-existent announcement."""
        response = await authenticated_client.get("/api/v1/announcements/nonexistentid")

        assert response.status_code == 404


class TestCreateAnnouncement:
    """Test create announcement endpoint."""

    async def test_create_announcement_success(self, authenticated_client: AsyncClient):
        """Test successful announcement creation."""
        response = await authenticated_client.post(
            "/api/v1/announcements/",
            json={
                "title": "Test Announcement",
                "content": "This is a test announcement content.",
                "priority": 5,
            },
        )

        assert response.status_code == 201 or response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "announcement_id" in data["data"]

    async def test_create_announcement_minimal(self, authenticated_client: AsyncClient):
        """Test creating announcement with minimal fields."""
        response = await authenticated_client.post(
            "/api/v1/announcements/",
            json={
                "title": "Minimal Announcement",
                "content": "Content here",
            },
        )

        assert response.status_code == 201 or response.status_code == 200

    async def test_create_announcement_missing_fields(self, authenticated_client: AsyncClient):
        """Test creating announcement with missing required fields."""
        response = await authenticated_client.post(
            "/api/v1/announcements/",
            json={"title": "Incomplete"},
        )

        assert response.status_code == 422

    async def test_create_announcement_without_auth(self, client: AsyncClient):
        """Test creating announcement without authentication."""
        response = await client.post(
            "/api/v1/announcements/",
            json={"title": "Test", "content": "Content"},
        )

        assert response.status_code == 401


class TestUpdateAnnouncement:
    """Test update announcement endpoint."""

    async def test_update_announcement_success(
        self, authenticated_client: AsyncClient, sample_announcement: dict
    ):
        """Test successful announcement update."""
        response = await authenticated_client.put(
            f"/api/v1/announcements/{sample_announcement['id']}",
            json={"title": "Updated Announcement Title"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0

    async def test_update_announcement_deactivate(
        self, authenticated_client: AsyncClient, sample_announcement: dict
    ):
        """Test deactivating an announcement."""
        response = await authenticated_client.put(
            f"/api/v1/announcements/{sample_announcement['id']}",
            json={"is_active": False},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0

    async def test_update_announcement_priority(
        self, authenticated_client: AsyncClient, sample_announcement: dict
    ):
        """Test updating announcement priority."""
        response = await authenticated_client.put(
            f"/api/v1/announcements/{sample_announcement['id']}",
            json={"priority": 10},
        )

        assert response.status_code == 200

    async def test_update_announcement_not_found(self, authenticated_client: AsyncClient):
        """Test updating non-existent announcement."""
        response = await authenticated_client.put(
            "/api/v1/announcements/nonexistentid",
            json={"title": "Updated"},
        )

        assert response.status_code == 404


class TestDeleteAnnouncement:
    """Test delete announcement endpoint."""

    async def test_delete_announcement_success(self, authenticated_client: AsyncClient):
        """Test successful announcement deletion."""
        from app.core.security import generate_object_id
        from app.config import settings
        from aiomysql import connect

        # Create temporary announcement
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
                VALUES ('{announcement_id}', 'admin_openid', 'Temp Announcement', 'Content', 1, 0)
                """
            )
        await conn.commit()
        await conn.close()

        # Delete the announcement
        response = await authenticated_client.delete(f"/api/v1/announcements/{announcement_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0

    async def test_delete_announcement_not_found(self, authenticated_client: AsyncClient):
        """Test deleting non-existent announcement."""
        response = await authenticated_client.delete("/api/v1/announcements/nonexistentid")

        assert response.status_code == 404
