"""Tests for System Settings API endpoints (/api/v1/settings/*)."""

from unittest.mock import AsyncMock, patch

import pytest

from tests.conftest import MOCK_SETTINGS

BASE = "/api/v1/settings"


def _mock_repo(**overrides):
    repo = AsyncMock()
    # Actual method names as used in settings.py
    repo.get = AsyncMock(return_value=MOCK_SETTINGS)
    repo.update = AsyncMock(return_value=True)
    for k, v in overrides.items():
        setattr(repo, k, v)
    return repo


# =============================================================================
# GET /api/v1/settings/
# =============================================================================

class TestGetSettings:
    async def test_get_success(self, client):
        with patch("app.api.v1.settings.SystemSettingsRepository") as MockRepo:
            MockRepo.return_value = _mock_repo()
            response = await client.get(f"{BASE}/")

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        data = body["data"]
        assert data["qr_code_expiration_seconds"] == MOCK_SETTINGS["qr_code_expiration_seconds"]
        assert data["registration_open"] == MOCK_SETTINGS["registration_open"]
        assert data["maintenance_mode"] == MOCK_SETTINGS["maintenance_mode"]

    async def test_get_settings_not_found(self, client):
        """If no settings row exists, endpoint returns 404."""
        with patch("app.api.v1.settings.SystemSettingsRepository") as MockRepo:
            MockRepo.return_value = _mock_repo(get=AsyncMock(return_value=None))
            response = await client.get(f"{BASE}/")

        assert response.status_code == 404

    async def test_get_settings_unauthorized(self, client_no_auth):
        response = await client_no_auth.get(f"{BASE}/")
        assert response.status_code in (401, 403)


# =============================================================================
# PUT /api/v1/settings/
# =============================================================================

class TestUpdateSettings:
    async def test_update_qr_expiration(self, client):
        with patch("app.api.v1.settings.SystemSettingsRepository") as MockRepo:
            MockRepo.return_value = _mock_repo()
            response = await client.put(f"{BASE}/", json={"qr_code_expiration_seconds": 600})

        assert response.status_code == 200

    async def test_update_maintenance_mode(self, client):
        with patch("app.api.v1.settings.SystemSettingsRepository") as MockRepo:
            MockRepo.return_value = _mock_repo()
            response = await client.put(
                f"{BASE}/",
                json={"maintenance_mode": True, "maintenance_message": "Under maintenance"},
            )

        assert response.status_code == 200

    async def test_update_registration_toggle(self, client):
        with patch("app.api.v1.settings.SystemSettingsRepository") as MockRepo:
            MockRepo.return_value = _mock_repo()
            response = await client.put(f"{BASE}/", json={"registration_open": False})

        assert response.status_code == 200

    async def test_update_settings_not_found(self, client):
        """If settings don't exist, update should return 404."""
        with patch("app.api.v1.settings.SystemSettingsRepository") as MockRepo:
            MockRepo.return_value = _mock_repo(get=AsyncMock(return_value=None))
            response = await client.put(f"{BASE}/", json={"registration_open": False})

        assert response.status_code == 404

    async def test_qr_expiration_too_short(self, client):
        response = await client.put(f"{BASE}/", json={"qr_code_expiration_seconds": 10})
        assert response.status_code == 422

    async def test_qr_expiration_too_long(self, client):
        response = await client.put(f"{BASE}/", json={"qr_code_expiration_seconds": 9999})
        assert response.status_code == 422

    async def test_leaderboard_top_n_out_of_range(self, client):
        response = await client.put(f"{BASE}/", json={"leaderboard_top_n": 200})
        assert response.status_code == 422

    async def test_maintenance_message_too_long(self, client):
        response = await client.put(f"{BASE}/", json={"maintenance_message": "x" * 501})
        assert response.status_code == 422

    async def test_update_no_changes(self, client):
        """Empty body is valid (no-op update returns 'No changes provided')."""
        with patch("app.api.v1.settings.SystemSettingsRepository") as MockRepo:
            MockRepo.return_value = _mock_repo()
            response = await client.put(f"{BASE}/", json={})

        assert response.status_code == 200
        assert "No changes" in response.json()["message"]
