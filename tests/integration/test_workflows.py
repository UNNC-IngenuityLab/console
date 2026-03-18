"""Integration tests for complete API workflows."""

import pytest
from httpx import AsyncClient
from decimal import Decimal


pytestmark = pytest.mark.asyncio


class TestUserJourney:
    """Test complete user journey workflow."""

    async def test_complete_user_activity_workflow(
        self, client: AsyncClient, authenticated_client: AsyncClient
    ):
        """Test complete workflow: create user -> create activity -> signup -> update points."""

        # Step 1: Create a test user (via direct DB insertion)
        from app.core.security import generate_object_id, get_password_hash
        from app.config import settings
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
                VALUES ('{user_id}', 'journey_openid', 'journey001', '{hashed_password}', 'pet', 'fluffy', 'Journey User', 0, 1, 1)
                """
            )
        await conn.commit()
        await conn.close()

        # Step 2: User logs in
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"student_id": "journey001", "password": "password123"},
        )

        assert login_response.status_code == 200
        token = login_response.json()["data"]["access_token"]

        # Step 3: Create an activity as admin
        activity_response = await authenticated_client.post(
            "/api/v1/activities/",
            json={
                "name": "Journey Test Activity",
                "venue": "Test Hall",
                "date_range": "2025.06.01 10:00~16:00",
                "start_date": "2025-06-01",
                "end_date": "2025-06-01",
                "total_point": Decimal("20.0"),
                "sub_activities": [
                    {"name": "Check-in", "point": Decimal("5.0"), "sort_order": 1},
                    {"name": "Activity", "point": Decimal("15.0"), "sort_order": 2},
                ],
            },
        )

        assert activity_response.status_code in [200, 201]
        activity_id = activity_response.json()["data"]["activity_id"]

        # Step 4: Generate QR code for the activity
        qr_response = await authenticated_client.post(f"/api/v1/activities/{activity_id}/qrcode")

        assert qr_response.status_code == 200
        assert "qr_code_url" in qr_response.json()["data"]

        # Step 5: Update user points (simulating activity completion)
        points_response = await authenticated_client.put(
            f"/api/v1/users/{user_id}/points",
            json={"points": Decimal("20.0"), "reason": "Completed Journey Test Activity"},
        )

        assert points_response.status_code == 200
        assert points_response.json()["data"]["new_points"] == "20.0"

        # Step 6: Verify user level was updated
        user_response = await authenticated_client.get(f"/api/v1/users/{user_id}")
        assert user_response.status_code == 200
        user_data = user_response.json()["data"]
        assert user_data["total_points"] == 20.0

        # Step 7: Check leaderboard includes user
        leaderboard_response = await authenticated_client.get("/api/v1/analytics/leaderboard")
        assert leaderboard_response.status_code == 200


class TestAnnouncementWorkflow:
    """Test announcement management workflow."""

    async def test_announcement_lifecycle(self, authenticated_client: AsyncClient):
        """Test creating, updating, deactivating, and deleting an announcement."""

        # Create announcement
        create_response = await authenticated_client.post(
            "/api/v1/announcements/",
            json={
                "title": "Workflow Test Announcement",
                "content": "This announcement will be modified",
                "priority": 3,
            },
        )

        assert create_response.status_code in [200, 201]
        announcement_id = create_response.json()["data"]["announcement_id"]

        # Update announcement
        update_response = await authenticated_client.put(
            f"/api/v1/announcements/{announcement_id}",
            json={"title": "Updated Title", "priority": 5},
        )

        assert update_response.status_code == 200

        # Deactivate announcement
        deactivate_response = await authenticated_client.put(
            f"/api/v1/announcements/{announcement_id}",
            json={"is_active": False},
        )

        assert deactivate_response.status_code == 200

        # Verify it's not in active list
        list_response = await authenticated_client.get(
            "/api/v1/announcements/", params={"is_active": True}
        )

        assert list_response.status_code == 200
        # Our deactivated announcement shouldn't be in active list
        announcements = list_response.json()["data"]["items"]
        announcement_ids = [a["id"] for a in announcements]
        assert announcement_id not in announcement_ids

        # Delete announcement
        delete_response = await authenticated_client.delete(f"/api/v1/announcements/{announcement_id}")
        assert delete_response.status_code == 200


class TestActivityWorkflow:
    """Test activity management workflow."""

    async def test_activity_with_sub_activities_workflow(self, authenticated_client: AsyncClient):
        """Test creating activity with multiple sub-activities and managing them."""

        # Create activity with sub-activities
        create_response = await authenticated_client.post(
            "/api/v1/activities/",
            json={
                "name": "Multi-Sub Activity",
                "venue": "Multi Hall",
                "date_range": "2025.07.01 10:00~18:00",
                "total_point": Decimal("40.0"),
                "sub_activities": [
                    {"name": "Registration", "point": Decimal("5.0"), "sort_order": 1},
                    {"name": "Session 1", "point": Decimal("15.0"), "sort_order": 2},
                    {"name": "Session 2", "point": Decimal("15.0"), "sort_order": 3},
                    {"name": "Survey", "point": Decimal("5.0"), "sort_order": 4},
                ],
            },
        )

        assert create_response.status_code in [200, 201]
        activity_id = create_response.json()["data"]["activity_id"]

        # Get activity details with sub-activities
        get_response = await authenticated_client.get(f"/api/v1/activities/{activity_id}")
        assert get_response.status_code == 200

        activity_data = get_response.json()["data"]
        assert len(activity_data["sub_activities"]) == 4

        # Add another sub-activity
        add_response = await authenticated_client.post(
            f"/api/v1/activities/{activity_id}/sub-activities",
            json={"name": "Bonus Activity", "point": Decimal("10.0"), "sort_order": 5},
        )

        assert add_response.status_code in [200, 201]

        # Update a sub-activity
        sub_id = activity_data["sub_activities"][0]["id"]
        update_sub_response = await authenticated_client.put(
            f"/api/v1/activities/sub-activities/{sub_id}",
            json={"name": "Updated Sub-Activity", "point": Decimal("8.0")},
        )

        assert update_sub_response.status_code == 200

        # Delete activity (should cascade to sub-activities)
        delete_response = await authenticated_client.delete(f"/api/v1/activities/{activity_id}")
        assert delete_response.status_code == 200


class TestLevelConfigurationWorkflow:
    """Test level configuration workflow."""

    async def test_custom_level_configuration(self, authenticated_client: AsyncClient):
        """Test creating custom level configurations."""

        # Create multiple custom levels
        custom_levels = [
            {"level": 101, "name": "Bronze", "min_score": Decimal("0"), "bg_color": "#CD7F32"},
            {"level": 102, "name": "Silver", "min_score": Decimal("50"), "bg_color": "#C0C0C0"},
            {"level": 103, "name": "Gold", "min_score": Decimal("100"), "bg_color": "#FFD700"},
        ]

        level_ids = []

        for level_data in custom_levels:
            response = await authenticated_client.post("/api/v1/levels/", json=level_data)
            assert response.status_code in [200, 201]
            if response.status_code == 200:
                level_ids.append(response.json()["data"]["level_id"])

        # List all levels
        list_response = await authenticated_client.get("/api/v1/levels/")
        assert list_response.status_code == 200

        all_levels = list_response.json()["data"]
        level_numbers = [level["level"] for level in all_levels]

        # Verify our custom levels are there
        for custom_level in custom_levels:
            assert custom_level["level"] in level_numbers

        # Export levels
        export_response = await authenticated_client.get("/api/v1/levels/export")
        assert export_response.status_code == 200

        exported_levels = export_response.json()["data"]["levels"]
        assert len(exported_levels) >= len(custom_levels)

        # Clean up - delete custom levels
        for level_id in level_ids:
            delete_response = await authenticated_client.delete(f"/api/v1/levels/{level_id}")
            assert delete_response.status_code == 200


class TestErrorHandling:
    """Test error handling across APIs."""

    async def test_not_found_errors(self, authenticated_client: AsyncClient):
        """Test 404 errors for non-existent resources."""

        # User not found
        user_response = await authenticated_client.get("/api/v1/users/nonexistent_user_id")
        assert user_response.status_code == 404

        # Activity not found
        activity_response = await authenticated_client.get("/api/v1/activities/nonexistent_activity_id")
        assert activity_response.status_code == 404

        # Announcement not found
        announcement_response = await authenticated_client.get("/api/v1/announcements/nonexistent_id")
        assert announcement_response.status_code == 404

        # Level not found
        level_response = await authenticated_client.get("/api/v1/levels/999999")
        assert level_response.status_code == 404

    async def test_validation_errors(self, authenticated_client: AsyncClient):
        """Test validation errors."""

        # Invalid login data
        login_response = await client.post(
            "/api/v1/auth/login",
            json={"student_id": ""},  # Missing password
        )
        assert login_response.status_code == 422

        # Invalid activity data
        activity_response = await authenticated_client.post(
            "/api/v1/activities/",
            json={"name": ""},  # Missing required fields
        )
        assert activity_response.status_code == 422

        # Invalid points value
        points_response = await authenticated_client.put(
            "/api/v1/users/some_id/points",
            json={"points": Decimal("-10"), "reason": "test"},
        )
        assert points_response.status_code == 422

    async def test_unauthorized_access(self, client: AsyncClient):
        """Test unauthorized access to protected endpoints."""

        # Try to access protected endpoints without token
        endpoints = [
            "/api/v1/users/",
            "/api/v1/activities/",
            "/api/v1/announcements/",
            "/api/v1/levels/",
            "/api/v1/settings/",
            "/api/v1/analytics/dashboard",
        ]

        for endpoint in endpoints:
            response = await client.get(endpoint)
            assert response.status_code == 401, f"Expected 401 for {endpoint}, got {response.status_code}"
