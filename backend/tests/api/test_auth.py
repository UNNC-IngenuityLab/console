"""Tests for Authentication API endpoints (/api/v1/auth/*)."""

from decimal import Decimal
from unittest.mock import AsyncMock, patch

import pytest

from tests.conftest import MOCK_ADMIN_USER


# =============================================================================
# POST /api/v1/auth/login
# =============================================================================

class TestLogin:
    URL = "/api/v1/auth/login"

    def _make_user_row(self, **overrides):
        base = {
            "id": MOCK_ADMIN_USER["id"],
            "student_id": "N20230001",
            "password": "hashed_password_placeholder",
            "is_active": True,
            "nickname": "Test Admin",
            "avatar_url": None,
            "total_points": Decimal("15.00"),
            "level": 3,
            "openid": "openid_test_admin_123",
        }
        base.update(overrides)
        return base

    async def test_login_success(self, client):
        mock_user = self._make_user_row()

        with (
            patch("app.api.v1.auth.UserRepository") as MockRepo,
            patch("app.api.v1.auth.verify_password", return_value=True),
        ):
            MockRepo.return_value.find_by_student_id = AsyncMock(return_value=mock_user)
            response = await client.post(self.URL, json={"student_id": "N20230001", "password": "correct"})

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert "access_token" in body["data"]
        assert body["data"]["user"]["student_id"] == "N20230001"

    async def test_login_user_not_found(self, client):
        with patch("app.api.v1.auth.UserRepository") as MockRepo:
            MockRepo.return_value.find_by_student_id = AsyncMock(return_value=None)
            response = await client.post(self.URL, json={"student_id": "UNKNOWN", "password": "any"})

        assert response.status_code == 401
        assert response.json()["code"] == 401

    async def test_login_wrong_password(self, client):
        mock_user = self._make_user_row()

        with (
            patch("app.api.v1.auth.UserRepository") as MockRepo,
            patch("app.api.v1.auth.verify_password", return_value=False),
        ):
            MockRepo.return_value.find_by_student_id = AsyncMock(return_value=mock_user)
            response = await client.post(self.URL, json={"student_id": "N20230001", "password": "wrong"})

        assert response.status_code == 401

    async def test_login_disabled_user(self, client):
        mock_user = self._make_user_row(is_active=False)

        with patch("app.api.v1.auth.UserRepository") as MockRepo:
            MockRepo.return_value.find_by_student_id = AsyncMock(return_value=mock_user)
            response = await client.post(self.URL, json={"student_id": "N20230001", "password": "any"})

        assert response.status_code == 401

    async def test_login_missing_password(self, client):
        response = await client.post(self.URL, json={"student_id": "N20230001"})
        assert response.status_code == 422

    async def test_login_empty_student_id(self, client):
        response = await client.post(self.URL, json={"student_id": "", "password": "password"})
        assert response.status_code == 422


# =============================================================================
# POST /api/v1/auth/logout
# =============================================================================

class TestLogout:
    URL = "/api/v1/auth/logout"

    async def test_logout_success(self, client):
        response = await client.post(self.URL)
        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert "Logged out" in body["message"]

    async def test_logout_unauthorized(self, client_no_auth):
        response = await client_no_auth.post(self.URL)
        assert response.status_code in (401, 403)


# =============================================================================
# GET /api/v1/auth/me
# =============================================================================

class TestGetCurrentUser:
    URL = "/api/v1/auth/me"

    async def test_get_me_success(self, client):
        response = await client.get(self.URL)
        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["student_id"] == MOCK_ADMIN_USER["student_id"]
        assert body["data"]["level"] == MOCK_ADMIN_USER["level"]

    async def test_get_me_unauthorized(self, client_no_auth):
        response = await client_no_auth.get(self.URL)
        assert response.status_code in (401, 403)
