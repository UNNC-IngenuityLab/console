"""Activity management API tests."""

import pytest
from httpx import AsyncClient
from decimal import Decimal


pytestmark = pytest.mark.asyncio


class TestListActivities:
    """Test list activities endpoint."""

    async def test_list_activities_success(self, authenticated_client: AsyncClient):
        """Test successful activity list retrieval."""
        response = await authenticated_client.get("/api/v1/activities/")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "items" in data["data"]

    async def test_list_activities_with_pagination(self, authenticated_client: AsyncClient):
        """Test activity list with pagination."""
        response = await authenticated_client.get(
            "/api/v1/activities/", params={"page": 1, "page_size": 10}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["page"] == 1

    async def test_list_activities_with_search(self, authenticated_client: AsyncClient, sample_activity: dict):
        """Test activity list with search."""
        response = await authenticated_client.get(
            "/api/v1/activities/", params={"search": "Test"}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0

    async def test_list_activities_with_active_filter(self, authenticated_client: AsyncClient):
        """Test activity list filtered by active status."""
        response = await authenticated_client.get(
            "/api/v1/activities/", params={"is_active": True}
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0

    async def test_list_activities_without_auth(self, client: AsyncClient):
        """Test listing activities without authentication."""
        response = await client.get("/api/v1/activities/")

        assert response.status_code == 401


class TestGetActivity:
    """Test get activity endpoint."""

    async def test_get_activity_success(
        self, authenticated_client: AsyncClient, sample_activity: dict
    ):
        """Test successful activity retrieval."""
        response = await authenticated_client.get(f"/api/v1/activities/{sample_activity['id']}")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert data["data"]["id"] == sample_activity["id"]
        assert "sub_activities" in data["data"]

    async def test_get_activity_not_found(self, authenticated_client: AsyncClient):
        """Test getting non-existent activity."""
        response = await authenticated_client.get("/api/v1/activities/nonexistentid")

        assert response.status_code == 404


class TestCreateActivity:
    """Test create activity endpoint."""

    async def test_create_activity_success(self, authenticated_client: AsyncClient):
        """Test successful activity creation."""
        response = await authenticated_client.post(
            "/api/v1/activities/",
            json={
                "name": "New Test Activity",
                "venue": "Test Venue",
                "date_range": "2025.05.01 10:00~16:00",
                "start_date": "2025-05-01",
                "end_date": "2025-05-01",
                "total_point": Decimal("25.0"),
                "sub_activities": [
                    {"name": "Check-in", "point": Decimal("5.0"), "sort_order": 1},
                    {"name": "Main Event", "point": Decimal("20.0"), "sort_order": 2},
                ],
            },
        )

        assert response.status_code == 201 or response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "activity_id" in data["data"]

    async def test_create_activity_minimal(self, authenticated_client: AsyncClient):
        """Test creating activity with minimal required fields."""
        response = await authenticated_client.post(
            "/api/v1/activities/",
            json={
                "name": "Minimal Activity",
                "venue": "Venue",
                "date_range": "2025.05.01 10:00~16:00",
            },
        )

        assert response.status_code == 201 or response.status_code == 200

    async def test_create_activity_missing_fields(self, authenticated_client: AsyncClient):
        """Test creating activity with missing required fields."""
        response = await authenticated_client.post(
            "/api/v1/activities/",
            json={"name": "Incomplete Activity"},
        )

        assert response.status_code == 422

    async def test_create_activity_without_auth(self, client: AsyncClient):
        """Test creating activity without authentication."""
        response = await client.post(
            "/api/v1/activities/",
            json={
                "name": "Test",
                "venue": "Venue",
                "date_range": "2025.05.01",
            },
        )

        assert response.status_code == 401


class TestUpdateActivity:
    """Test update activity endpoint."""

    async def test_update_activity_success(
        self, authenticated_client: AsyncClient, sample_activity: dict
    ):
        """Test successful activity update."""
        response = await authenticated_client.put(
            f"/api/v1/activities/{sample_activity['id']}",
            json={"name": "Updated Activity Name"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0

    async def test_update_activity_deactivate(
        self, authenticated_client: AsyncClient, sample_activity: dict
    ):
        """Test deactivating an activity."""
        response = await authenticated_client.put(
            f"/api/v1/activities/{sample_activity['id']}",
            json={"is_active": False},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0

    async def test_update_activity_not_found(self, authenticated_client: AsyncClient):
        """Test updating non-existent activity."""
        response = await authenticated_client.put(
            "/api/v1/activities/nonexistentid",
            json={"name": "Updated"},
        )

        assert response.status_code == 404


class TestDeleteActivity:
    """Test delete activity endpoint."""

    async def test_delete_activity_success(self, authenticated_client: AsyncClient):
        """Test successful activity deletion."""
        from app.core.security import generate_object_id
        from datetime import datetime
        from app.config import settings
        from aiomysql import connect

        # Create temporary activity
        conn = await connect(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            database="ingenuity_lab_test",
        )

        activity_id = generate_object_id()
        timestamp_id = int(datetime.now().timestamp() * 1000)

        async with conn.cursor() as cursor:
            await cursor.execute(
                f"""
                INSERT INTO activities (id, activity_id, creator_openid, name, venue, date_range, total_point, sign_up_count, completed_count, is_active)
                VALUES ('{activity_id}', {timestamp_id}, 'admin_openid', 'Temp Activity', 'Venue', '2025.05.01', 10, 0, 0, 1)
                """
            )
        await conn.commit()
        await conn.close()

        # Delete the activity
        response = await authenticated_client.delete(f"/api/v1/activities/{activity_id}")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0

    async def test_delete_activity_not_found(self, authenticated_client: AsyncClient):
        """Test deleting non-existent activity."""
        response = await authenticated_client.delete("/api/v1/activities/nonexistentid")

        assert response.status_code == 404


class TestGenerateQRCode:
    """Test generate QR code endpoint."""

    async def test_generate_qrcode_success(
        self, authenticated_client: AsyncClient, sample_activity: dict
    ):
        """Test successful QR code generation."""
        response = await authenticated_client.post(f"/api/v1/activities/{sample_activity['id']}/qrcode")

        assert response.status_code == 200
        data = response.json()
        assert data["code"] == 0
        assert "qr_code_url" in data["data"]
        assert data["data"]["qr_code_url"].startswith("data:image/png")

    async def test_generate_qrcode_activity_not_found(self, authenticated_client: AsyncClient):
        """Test generating QR code for non-existent activity."""
        response = await authenticated_client.post("/api/v1/activities/nonexistentid/qrcode")

        assert response.status_code == 404


class TestSubActivities:
    """Test sub-activity endpoints."""

    async def test_create_sub_activity_success(
        self, authenticated_client: AsyncClient, sample_activity: dict
    ):
        """Test successful sub-activity creation."""
        response = await authenticated_client.post(
            f"/api/v1/activities/{sample_activity['id']}/sub-activities",
            json={"name": "New Sub-Activity", "point": Decimal("10.0"), "sort_order": 3},
        )

        assert response.status_code == 201 or response.status_code == 200
        data = response.json()
        assert data["code"] == 0

    async def test_update_sub_activity(self, authenticated_client: AsyncClient, sample_activity: dict):
        """Test updating a sub-activity."""
        # Get activity to find sub-activity ID
        response = await authenticated_client.get(f"/api/v1/activities/{sample_activity['id']}")
        activity_data = response.json()["data"]

        if activity_data["sub_activities"]:
            sub_id = activity_data["sub_activities"][0]["id"]
            response = await authenticated_client.put(
                f"/api/v1/activities/sub-activities/{sub_id}",
                json={"name": "Updated Sub-Activity"},
            )

            assert response.status_code == 200

    async def test_delete_sub_activity(self, authenticated_client: AsyncClient, sample_activity: dict):
        """Test deleting a sub-activity."""
        # Create a sub-activity first
        create_response = await authenticated_client.post(
            f"/api/v1/activities/{sample_activity['id']}/sub-activities",
            json={"name": "To Be Deleted", "point": Decimal("5.0"), "sort_order": 99},
        )

        if create_response.status_code == 200:
            sub_id = create_response.json()["data"]["sub_activity_id"]
            response = await authenticated_client.delete(f"/api/v1/activities/sub-activities/{sub_id}")

            assert response.status_code == 200
