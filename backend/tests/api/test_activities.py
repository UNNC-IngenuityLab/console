"""Tests for Activity Management API endpoints (/api/v1/activities/*)."""

from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pytest

from tests.conftest import MOCK_ACTIVITY, MOCK_SUB_ACTIVITY, PAGINATED_RESULT_TEMPLATE

BASE = "/api/v1/activities"


def _paginated(items):
    return {**PAGINATED_RESULT_TEMPLATE, "items": items, "total": len(items), "total_pages": 1 if items else 0}


def _mock_activity_repo(**overrides):
    repo = AsyncMock()
    repo.list_activities = AsyncMock(return_value=_paginated([MOCK_ACTIVITY]))
    repo.find_by_id = AsyncMock(return_value=MOCK_ACTIVITY)
    repo.create_activity = AsyncMock(return_value=MOCK_ACTIVITY["id"])
    repo.update_activity = AsyncMock(return_value=True)
    repo.delete_activity = AsyncMock(return_value=True)
    repo.update_signup_counts = AsyncMock(return_value=True)
    for k, v in overrides.items():
        setattr(repo, k, v)
    return repo


def _mock_sub_repo(**overrides):
    repo = AsyncMock()
    repo.list_by_activity = AsyncMock(return_value=[MOCK_SUB_ACTIVITY])
    repo.create_sub_activity = AsyncMock(return_value=MOCK_SUB_ACTIVITY["id"])
    repo.find_by_id = AsyncMock(return_value=MOCK_SUB_ACTIVITY)
    repo.update_sub_activity = AsyncMock(return_value=True)
    repo.delete_sub_activity = AsyncMock(return_value=True)
    for k, v in overrides.items():
        setattr(repo, k, v)
    return repo


# =============================================================================
# GET /api/v1/activities/
# =============================================================================

class TestListActivities:
    async def test_list_success(self, client):
        with patch("app.api.v1.activities.ActivityRepository") as MockRepo:
            MockRepo.return_value = _mock_activity_repo()
            response = await client.get(f"{BASE}/")

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["total"] == 1
        assert body["data"]["items"][0]["name"] == MOCK_ACTIVITY["name"]

    async def test_list_empty(self, client):
        with patch("app.api.v1.activities.ActivityRepository") as MockRepo:
            MockRepo.return_value = _mock_activity_repo(
                list_activities=AsyncMock(return_value=_paginated([]))
            )
            response = await client.get(f"{BASE}/")

        assert response.status_code == 200
        assert response.json()["data"]["total"] == 0

    async def test_list_with_search_filter(self, client):
        with patch("app.api.v1.activities.ActivityRepository") as MockRepo:
            mock_repo = _mock_activity_repo()
            MockRepo.return_value = mock_repo
            response = await client.get(f"{BASE}/", params={"search": "Test", "is_active": True})

        assert response.status_code == 200
        mock_repo.list_activities.assert_called_once_with(
            search="Test", is_active=True, start_date_from=None, start_date_to=None, page=1, page_size=20
        )

    async def test_list_invalid_page_size(self, client):
        response = await client.get(f"{BASE}/", params={"page_size": 500})
        assert response.status_code == 422

    async def test_list_unauthorized(self, client_no_auth):
        response = await client_no_auth.get(f"{BASE}/")
        assert response.status_code in (401, 403)


# =============================================================================
# GET /api/v1/activities/{id}
# =============================================================================

class TestGetActivity:
    async def test_get_success(self, client):
        with (
            patch("app.api.v1.activities.ActivityRepository") as MockActivityRepo,
            patch("app.api.v1.activities.SubActivityRepository") as MockSubRepo,
        ):
            MockActivityRepo.return_value = _mock_activity_repo()
            MockSubRepo.return_value = _mock_sub_repo()
            response = await client.get(f"{BASE}/{MOCK_ACTIVITY['id']}")

        assert response.status_code == 200
        body = response.json()
        assert body["data"]["id"] == MOCK_ACTIVITY["id"]
        assert "sub_activities" in body["data"]

    async def test_get_not_found(self, client):
        with (
            patch("app.api.v1.activities.ActivityRepository") as MockRepo,
            patch("app.api.v1.activities.SubActivityRepository"),
        ):
            MockRepo.return_value = _mock_activity_repo(find_by_id=AsyncMock(return_value=None))
            response = await client.get(f"{BASE}/nonexistent_id")

        assert response.status_code == 404


# =============================================================================
# POST /api/v1/activities/
# =============================================================================

class TestCreateActivity:
    VALID_PAYLOAD = {
        "name": "New Activity",
        "venue": "Room 101",
        "date_range": "2024-03-01 ~ 2024-03-02",
        "start_date": "2024-03-01",
        "end_date": "2024-03-02",
        "total_point": "10.00",
        "sub_activities": [
            {"name": "Sub A", "point": "5.00", "sort_order": 0},
            {"name": "Sub B", "point": "5.00", "sort_order": 1},
        ],
    }

    async def test_create_success(self, client):
        with (
            patch("app.api.v1.activities.ActivityRepository") as MockRepo,
            patch("app.api.v1.activities.SubActivityRepository") as MockSubRepo,
        ):
            MockRepo.return_value = _mock_activity_repo()
            MockSubRepo.return_value = _mock_sub_repo()
            response = await client.post(f"{BASE}/", json=self.VALID_PAYLOAD)

        assert response.status_code == 201
        assert "activity_id" in response.json()["data"]

    async def test_create_no_sub_activities(self, client):
        payload = {**self.VALID_PAYLOAD, "sub_activities": []}
        with (
            patch("app.api.v1.activities.ActivityRepository") as MockRepo,
            patch("app.api.v1.activities.SubActivityRepository") as MockSubRepo,
        ):
            MockRepo.return_value = _mock_activity_repo()
            MockSubRepo.return_value = _mock_sub_repo()
            response = await client.post(f"{BASE}/", json=payload)

        assert response.status_code == 201

    async def test_create_missing_required_fields(self, client):
        response = await client.post(f"{BASE}/", json={"name": "Only Name"})
        assert response.status_code == 422

    async def test_create_total_point_exceeds_limit(self, client):
        payload = {**self.VALID_PAYLOAD, "total_point": "200.00"}
        response = await client.post(f"{BASE}/", json=payload)
        assert response.status_code == 422

    async def test_create_sub_activity_point_exceeds_limit(self, client):
        payload = {
            **self.VALID_PAYLOAD,
            "sub_activities": [{"name": "Too much", "point": "99.00", "sort_order": 0}],
        }
        response = await client.post(f"{BASE}/", json=payload)
        assert response.status_code == 422


# =============================================================================
# PUT /api/v1/activities/{id}
# =============================================================================

class TestUpdateActivity:
    async def test_update_success(self, client):
        with patch("app.api.v1.activities.ActivityRepository") as MockRepo:
            MockRepo.return_value = _mock_activity_repo()
            response = await client.put(
                f"{BASE}/{MOCK_ACTIVITY['id']}",
                json={"name": "Updated Name", "is_active": False},
            )

        assert response.status_code == 200

    async def test_update_not_found(self, client):
        with patch("app.api.v1.activities.ActivityRepository") as MockRepo:
            MockRepo.return_value = _mock_activity_repo(find_by_id=AsyncMock(return_value=None))
            response = await client.put(f"{BASE}/nonexistent", json={"name": "X"})

        assert response.status_code == 404

    async def test_update_no_changes(self, client):
        with patch("app.api.v1.activities.ActivityRepository") as MockRepo:
            MockRepo.return_value = _mock_activity_repo()
            response = await client.put(f"{BASE}/{MOCK_ACTIVITY['id']}", json={})

        assert response.status_code == 200
        assert "No changes" in response.json()["message"]


# =============================================================================
# DELETE /api/v1/activities/{id}
# =============================================================================

class TestDeleteActivity:
    async def test_delete_success(self, client):
        with patch("app.api.v1.activities.ActivityRepository") as MockRepo:
            MockRepo.return_value = _mock_activity_repo()
            response = await client.delete(f"{BASE}/{MOCK_ACTIVITY['id']}")

        assert response.status_code == 200

    async def test_delete_not_found(self, client):
        with patch("app.api.v1.activities.ActivityRepository") as MockRepo:
            MockRepo.return_value = _mock_activity_repo(find_by_id=AsyncMock(return_value=None))
            response = await client.delete(f"{BASE}/nonexistent")

        assert response.status_code == 404


# =============================================================================
# POST /api/v1/activities/{id}/sub-activities
# =============================================================================

class TestCreateSubActivity:
    async def test_create_success(self, client):
        with (
            patch("app.api.v1.activities.ActivityRepository") as MockRepo,
            patch("app.api.v1.activities.SubActivityRepository") as MockSubRepo,
        ):
            MockRepo.return_value = _mock_activity_repo()
            MockSubRepo.return_value = _mock_sub_repo()
            response = await client.post(
                f"{BASE}/{MOCK_ACTIVITY['id']}/sub-activities",
                json={"name": "New Sub", "point": "3.00", "sort_order": 2},
            )

        assert response.status_code == 201
        assert "sub_activity_id" in response.json()["data"]

    async def test_create_parent_not_found(self, client):
        with (
            patch("app.api.v1.activities.ActivityRepository") as MockRepo,
            patch("app.api.v1.activities.SubActivityRepository"),
        ):
            MockRepo.return_value = _mock_activity_repo(find_by_id=AsyncMock(return_value=None))
            response = await client.post(
                f"{BASE}/nonexistent/sub-activities",
                json={"name": "Sub", "point": "2.00"},
            )

        assert response.status_code == 404


# =============================================================================
# POST /api/v1/activities/{id}/qrcode
# =============================================================================

class TestGenerateQRCode:
    async def test_generate_qr_code_success(self, client):
        with patch("app.api.v1.activities.ActivityRepository") as MockRepo:
            MockRepo.return_value = _mock_activity_repo()
            response = await client.post(f"{BASE}/{MOCK_ACTIVITY['id']}/qrcode")

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["qr_code_url"].startswith("data:image/png;base64,")
        assert "expires_at" in body["data"]

    async def test_generate_qr_code_not_found(self, client):
        with patch("app.api.v1.activities.ActivityRepository") as MockRepo:
            MockRepo.return_value = _mock_activity_repo(find_by_id=AsyncMock(return_value=None))
            response = await client.post(f"{BASE}/nonexistent/qrcode")

        assert response.status_code == 404
