"""Tests for Announcement Management API endpoints (/api/v1/announcements/*)."""

from unittest.mock import AsyncMock, patch

import pytest

from tests.conftest import MOCK_ANNOUNCEMENT, PAGINATED_RESULT_TEMPLATE

BASE = "/api/v1/announcements"


def _paginated(items):
    return {**PAGINATED_RESULT_TEMPLATE, "items": items, "total": len(items), "total_pages": 1 if items else 0}


def _mock_repo(**overrides):
    repo = AsyncMock()
    repo.list_announcements = AsyncMock(return_value=_paginated([MOCK_ANNOUNCEMENT]))
    repo.find_by_id = AsyncMock(return_value=MOCK_ANNOUNCEMENT)
    repo.create_announcement = AsyncMock(return_value=MOCK_ANNOUNCEMENT["id"])
    repo.update_announcement = AsyncMock(return_value=True)
    repo.delete_announcement = AsyncMock(return_value=True)
    for k, v in overrides.items():
        setattr(repo, k, v)
    return repo


# =============================================================================
# GET /api/v1/announcements/
# =============================================================================

class TestListAnnouncements:
    async def test_list_success(self, client):
        with patch("app.api.v1.announcements.AnnouncementRepository") as MockRepo:
            MockRepo.return_value = _mock_repo()
            response = await client.get(f"{BASE}/")

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["total"] == 1
        assert body["data"]["items"][0]["title"] == MOCK_ANNOUNCEMENT["title"]

    async def test_list_filter_active(self, client):
        with patch("app.api.v1.announcements.AnnouncementRepository") as MockRepo:
            mock_repo = _mock_repo()
            MockRepo.return_value = mock_repo
            response = await client.get(f"{BASE}/", params={"is_active": True})

        assert response.status_code == 200
        mock_repo.list_announcements.assert_called_once_with(is_active=True, page=1, page_size=20)

    async def test_list_empty(self, client):
        with patch("app.api.v1.announcements.AnnouncementRepository") as MockRepo:
            MockRepo.return_value = _mock_repo(
                list_announcements=AsyncMock(return_value=_paginated([]))
            )
            response = await client.get(f"{BASE}/")

        assert response.status_code == 200
        assert response.json()["data"]["total"] == 0

    async def test_list_unauthorized(self, client_no_auth):
        response = await client_no_auth.get(f"{BASE}/")
        assert response.status_code in (401, 403)


# =============================================================================
# GET /api/v1/announcements/{id}
# =============================================================================

class TestGetAnnouncement:
    async def test_get_success(self, client):
        with patch("app.api.v1.announcements.AnnouncementRepository") as MockRepo:
            MockRepo.return_value = _mock_repo()
            response = await client.get(f"{BASE}/{MOCK_ANNOUNCEMENT['id']}")

        assert response.status_code == 200
        body = response.json()
        assert body["data"]["id"] == MOCK_ANNOUNCEMENT["id"]
        assert body["data"]["title"] == MOCK_ANNOUNCEMENT["title"]

    async def test_get_not_found(self, client):
        with patch("app.api.v1.announcements.AnnouncementRepository") as MockRepo:
            MockRepo.return_value = _mock_repo(find_by_id=AsyncMock(return_value=None))
            response = await client.get(f"{BASE}/nonexistent")

        assert response.status_code == 404


# =============================================================================
# POST /api/v1/announcements/
# =============================================================================

class TestCreateAnnouncement:
    VALID_PAYLOAD = {
        "title": "Welcome Announcement",
        "content": "This is the announcement content.",
        "priority": 1,
    }

    async def test_create_success(self, client):
        with patch("app.api.v1.announcements.AnnouncementRepository") as MockRepo:
            MockRepo.return_value = _mock_repo()
            response = await client.post(f"{BASE}/", json=self.VALID_PAYLOAD)

        assert response.status_code == 201
        assert "announcement_id" in response.json()["data"]

    async def test_create_default_priority(self, client):
        with patch("app.api.v1.announcements.AnnouncementRepository") as MockRepo:
            MockRepo.return_value = _mock_repo()
            response = await client.post(f"{BASE}/", json={"title": "Notice", "content": "Content."})

        assert response.status_code == 201

    async def test_create_empty_title_rejected(self, client):
        response = await client.post(f"{BASE}/", json={"title": "", "content": "Content."})
        assert response.status_code == 422

    async def test_create_empty_content_rejected(self, client):
        response = await client.post(f"{BASE}/", json={"title": "Title", "content": ""})
        assert response.status_code == 422

    async def test_create_missing_title(self, client):
        response = await client.post(f"{BASE}/", json={"content": "Content."})
        assert response.status_code == 422


# =============================================================================
# PUT /api/v1/announcements/{id}
# =============================================================================

class TestUpdateAnnouncement:
    async def test_update_title(self, client):
        with patch("app.api.v1.announcements.AnnouncementRepository") as MockRepo:
            MockRepo.return_value = _mock_repo()
            response = await client.put(
                f"{BASE}/{MOCK_ANNOUNCEMENT['id']}",
                json={"title": "Updated Title"},
            )

        assert response.status_code == 200

    async def test_update_toggle_active(self, client):
        with patch("app.api.v1.announcements.AnnouncementRepository") as MockRepo:
            MockRepo.return_value = _mock_repo()
            response = await client.put(
                f"{BASE}/{MOCK_ANNOUNCEMENT['id']}",
                json={"is_active": False},
            )

        assert response.status_code == 200

    async def test_update_not_found(self, client):
        with patch("app.api.v1.announcements.AnnouncementRepository") as MockRepo:
            MockRepo.return_value = _mock_repo(find_by_id=AsyncMock(return_value=None))
            response = await client.put(f"{BASE}/nonexistent", json={"title": "X"})

        assert response.status_code == 404

    async def test_update_no_changes(self, client):
        with patch("app.api.v1.announcements.AnnouncementRepository") as MockRepo:
            MockRepo.return_value = _mock_repo()
            response = await client.put(f"{BASE}/{MOCK_ANNOUNCEMENT['id']}", json={})

        assert response.status_code == 200
        assert "No changes" in response.json()["message"]


# =============================================================================
# DELETE /api/v1/announcements/{id}
# =============================================================================

class TestDeleteAnnouncement:
    async def test_delete_success(self, client):
        with patch("app.api.v1.announcements.AnnouncementRepository") as MockRepo:
            MockRepo.return_value = _mock_repo()
            response = await client.delete(f"{BASE}/{MOCK_ANNOUNCEMENT['id']}")

        assert response.status_code == 200

    async def test_delete_not_found(self, client):
        with patch("app.api.v1.announcements.AnnouncementRepository") as MockRepo:
            MockRepo.return_value = _mock_repo(find_by_id=AsyncMock(return_value=None))
            response = await client.delete(f"{BASE}/nonexistent")

        assert response.status_code == 404
