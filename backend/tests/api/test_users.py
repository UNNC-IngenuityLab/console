"""Tests for User Management API endpoints (/api/v1/users/*)."""

from decimal import Decimal
from unittest.mock import AsyncMock

import pytest

from app.dependencies import get_user_repo
from app.main import app
from tests.conftest import MOCK_USER, PAGINATED_RESULT_TEMPLATE


def make_user_repo_mock(**overrides):
    repo = AsyncMock()
    repo.list_users = AsyncMock(return_value={
        **PAGINATED_RESULT_TEMPLATE,
        "items": [MOCK_USER],
        "total": 1,
        "total_pages": 1,
    })
    repo.find_by_id = AsyncMock(return_value=MOCK_USER)
    repo.update_points = AsyncMock(return_value=True)
    repo.update = AsyncMock(return_value=True)
    repo.delete_user = AsyncMock(return_value=True)
    for k, v in overrides.items():
        setattr(repo, k, v)
    return repo


@pytest.fixture
async def client_with_user_repo(client):
    """Extend client fixture with get_user_repo override."""
    mock_repo = make_user_repo_mock()

    async def override():
        return mock_repo

    app.dependency_overrides[get_user_repo] = override
    yield client, mock_repo
    # conftest restores dependency_overrides after client fixture exits


# =============================================================================
# GET /api/v1/users/
# =============================================================================

class TestListUsers:
    URL = "/api/v1/users/"

    async def test_list_success(self, client_with_user_repo):
        client, repo = client_with_user_repo
        response = await client.get(self.URL)

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["total"] == 1
        assert body["data"]["items"][0]["student_id"] == MOCK_USER["student_id"]

    async def test_list_empty(self, client_with_user_repo):
        client, repo = client_with_user_repo
        repo.list_users = AsyncMock(return_value={**PAGINATED_RESULT_TEMPLATE, "total_pages": 0})

        response = await client.get(self.URL)

        assert response.status_code == 200
        assert response.json()["data"]["total"] == 0

    async def test_list_with_filters(self, client_with_user_repo):
        client, repo = client_with_user_repo
        response = await client.get(self.URL, params={"search": "N2023", "level": 4})

        assert response.status_code == 200
        call_kwargs = repo.list_users.call_args.kwargs
        assert call_kwargs["search"] == "N2023"
        assert call_kwargs["level"] == 4

    async def test_list_invalid_page_size(self, client_with_user_repo):
        client, _ = client_with_user_repo
        response = await client.get(self.URL, params={"page_size": 200})
        assert response.status_code == 422

    async def test_list_unauthorized(self, client_no_auth):
        response = await client_no_auth.get(self.URL)
        assert response.status_code in (401, 403)


# =============================================================================
# GET /api/v1/users/{user_id}
# =============================================================================

class TestGetUser:
    URL = "/api/v1/users/{user_id}"

    async def test_get_success(self, client_with_user_repo):
        client, repo = client_with_user_repo
        response = await client.get(self.URL.format(user_id=MOCK_USER["id"]))

        assert response.status_code == 200
        body = response.json()
        assert body["data"]["id"] == MOCK_USER["id"]

    async def test_get_not_found(self, client_with_user_repo):
        client, repo = client_with_user_repo
        repo.find_by_id = AsyncMock(return_value=None)

        response = await client.get(self.URL.format(user_id="nonexistent_id"))

        assert response.status_code == 404
        assert response.json()["code"] == 404


# =============================================================================
# PUT /api/v1/users/{user_id}/points
# =============================================================================

class TestUpdateUserPoints:
    URL = "/api/v1/users/{user_id}/points"

    async def test_update_points_success(self, client_with_user_repo):
        client, repo = client_with_user_repo
        response = await client.put(
            self.URL.format(user_id=MOCK_USER["id"]),
            json={"points": "20.00", "reason": "Manual adjustment"},
        )

        assert response.status_code == 200
        assert response.json()["data"]["new_points"] == "20.00"

    async def test_update_points_user_not_found(self, client_with_user_repo):
        client, repo = client_with_user_repo
        repo.find_by_id = AsyncMock(return_value=None)

        response = await client.put(
            self.URL.format(user_id="nonexistent"),
            json={"points": "10.00", "reason": "Test"},
        )

        assert response.status_code == 404

    async def test_update_points_negative_rejected(self, client_with_user_repo):
        client, _ = client_with_user_repo
        response = await client.put(
            self.URL.format(user_id=MOCK_USER["id"]),
            json={"points": "-5.00", "reason": "Invalid"},
        )
        assert response.status_code == 422

    async def test_update_points_empty_reason_rejected(self, client_with_user_repo):
        client, _ = client_with_user_repo
        response = await client.put(
            self.URL.format(user_id=MOCK_USER["id"]),
            json={"points": "10.00", "reason": ""},
        )
        assert response.status_code == 422


# =============================================================================
# PUT /api/v1/users/{user_id}
# =============================================================================

class TestUpdateUser:
    URL = "/api/v1/users/{user_id}"

    async def test_update_nickname(self, client_with_user_repo):
        client, repo = client_with_user_repo
        response = await client.put(
            self.URL.format(user_id=MOCK_USER["id"]),
            json={"nickname": "New Name"},
        )
        assert response.status_code == 200

    async def test_update_disable_user(self, client_with_user_repo):
        client, repo = client_with_user_repo
        response = await client.put(
            self.URL.format(user_id=MOCK_USER["id"]),
            json={"is_active": False},
        )
        assert response.status_code == 200

    async def test_update_not_found(self, client_with_user_repo):
        client, repo = client_with_user_repo
        repo.find_by_id = AsyncMock(return_value=None)

        response = await client.put(self.URL.format(user_id="nonexistent"), json={"nickname": "X"})
        assert response.status_code == 404

    async def test_update_invalid_level(self, client_with_user_repo):
        client, _ = client_with_user_repo
        response = await client.put(
            self.URL.format(user_id=MOCK_USER["id"]),
            json={"level": 99},
        )
        assert response.status_code == 422

    async def test_update_no_changes(self, client_with_user_repo):
        client, repo = client_with_user_repo
        response = await client.put(self.URL.format(user_id=MOCK_USER["id"]), json={})

        assert response.status_code == 200
        repo.update.assert_not_called()


# =============================================================================
# DELETE /api/v1/users/{user_id}
# =============================================================================

class TestDeleteUser:
    URL = "/api/v1/users/{user_id}"

    async def test_delete_success(self, client_with_user_repo):
        client, repo = client_with_user_repo
        response = await client.delete(self.URL.format(user_id=MOCK_USER["id"]))

        assert response.status_code == 200
        assert response.json()["code"] == 0

    async def test_delete_not_found(self, client_with_user_repo):
        client, repo = client_with_user_repo
        repo.find_by_id = AsyncMock(return_value=None)

        response = await client.delete(self.URL.format(user_id="nonexistent"))
        assert response.status_code == 404
