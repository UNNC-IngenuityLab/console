"""Tests for Level Config API endpoints (/api/v1/levels/*)."""

from unittest.mock import AsyncMock, patch

import pytest

from tests.conftest import MOCK_LEVEL_CONFIG

BASE = "/api/v1/levels"

VALID_CREATE_PAYLOAD = {
    "level": 2,
    "name": "城市小店",
    "name_en": "City Shop",
    "min_score": "10.00",
    "max_score": "25.00",
    "icon_url": "/assets/level-2.png",
    "bg_color": "#2196F3",
    "is_active": True,
    "sort_order": 1,
}


def _mock_repo(**overrides):
    repo = AsyncMock()
    # Actual method names as used in levels.py
    repo.list_all = AsyncMock(return_value=[MOCK_LEVEL_CONFIG])
    repo.find_by_id = AsyncMock(return_value=MOCK_LEVEL_CONFIG)
    repo.find_by_level = AsyncMock(return_value=None)           # None = level doesn't exist yet
    repo.create_level_config = AsyncMock(return_value={"id": MOCK_LEVEL_CONFIG["id"]})
    repo.update_level_config = AsyncMock(return_value=True)
    repo.delete_level_config = AsyncMock(return_value=True)
    repo.reorder_levels = AsyncMock(return_value=True)
    for k, v in overrides.items():
        setattr(repo, k, v)
    return repo


# =============================================================================
# GET /api/v1/levels/
# =============================================================================

class TestListLevels:
    async def test_list_success(self, client):
        with patch("app.api.v1.levels.LevelConfigRepository") as MockRepo:
            MockRepo.return_value = _mock_repo()
            response = await client.get(f"{BASE}/")

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert isinstance(body["data"], list)
        assert len(body["data"]) == 1
        assert body["data"][0]["level"] == MOCK_LEVEL_CONFIG["level"]
        assert body["data"][0]["name"] == MOCK_LEVEL_CONFIG["name"]

    async def test_list_unauthorized(self, client_no_auth):
        response = await client_no_auth.get(f"{BASE}/")
        assert response.status_code in (401, 403)


# =============================================================================
# GET /api/v1/levels/export
# =============================================================================

class TestExportLevels:
    async def test_export_success(self, client):
        with patch("app.api.v1.levels.LevelConfigRepository") as MockRepo:
            MockRepo.return_value = _mock_repo()
            response = await client.get(f"{BASE}/export")

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert "levels" in body["data"]
        assert "exported_at" in body["data"]


# =============================================================================
# GET /api/v1/levels/{id}
# =============================================================================

class TestGetLevel:
    async def test_get_success(self, client):
        with patch("app.api.v1.levels.LevelConfigRepository") as MockRepo:
            MockRepo.return_value = _mock_repo()
            response = await client.get(f"{BASE}/{MOCK_LEVEL_CONFIG['id']}")

        assert response.status_code == 200
        body = response.json()
        assert body["data"]["id"] == MOCK_LEVEL_CONFIG["id"]
        assert body["data"]["name"] == MOCK_LEVEL_CONFIG["name"]

    async def test_get_not_found(self, client):
        with patch("app.api.v1.levels.LevelConfigRepository") as MockRepo:
            MockRepo.return_value = _mock_repo(find_by_id=AsyncMock(return_value=None))
            response = await client.get(f"{BASE}/999")

        assert response.status_code == 404


# =============================================================================
# POST /api/v1/levels/
# =============================================================================

class TestCreateLevel:
    async def test_create_success(self, client):
        with patch("app.api.v1.levels.LevelConfigRepository") as MockRepo:
            MockRepo.return_value = _mock_repo()
            response = await client.post(f"{BASE}/", json=VALID_CREATE_PAYLOAD)

        assert response.status_code == 201
        assert "level_id" in response.json()["data"]

    async def test_create_duplicate_level_rejected(self, client):
        """Creating a level that already exists returns 400."""
        with patch("app.api.v1.levels.LevelConfigRepository") as MockRepo:
            MockRepo.return_value = _mock_repo(
                find_by_level=AsyncMock(return_value=MOCK_LEVEL_CONFIG)
            )
            response = await client.post(f"{BASE}/", json=VALID_CREATE_PAYLOAD)

        assert response.status_code == 400

    async def test_create_missing_name(self, client):
        payload = {k: v for k, v in VALID_CREATE_PAYLOAD.items() if k != "name"}
        response = await client.post(f"{BASE}/", json=payload)
        assert response.status_code == 422

    async def test_create_invalid_level_zero(self, client):
        payload = {**VALID_CREATE_PAYLOAD, "level": 0}
        response = await client.post(f"{BASE}/", json=payload)
        assert response.status_code == 422


# =============================================================================
# PUT /api/v1/levels/{id}
# =============================================================================

class TestUpdateLevel:
    async def test_update_success(self, client):
        with patch("app.api.v1.levels.LevelConfigRepository") as MockRepo:
            MockRepo.return_value = _mock_repo()
            response = await client.put(
                f"{BASE}/{MOCK_LEVEL_CONFIG['id']}",
                json={"name": "Updated Level Name"},
            )

        assert response.status_code == 200

    async def test_update_not_found(self, client):
        with patch("app.api.v1.levels.LevelConfigRepository") as MockRepo:
            MockRepo.return_value = _mock_repo(find_by_id=AsyncMock(return_value=None))
            response = await client.put(f"{BASE}/999", json={"name": "X"})

        assert response.status_code == 404

    async def test_update_no_changes(self, client):
        with patch("app.api.v1.levels.LevelConfigRepository") as MockRepo:
            MockRepo.return_value = _mock_repo()
            response = await client.put(f"{BASE}/{MOCK_LEVEL_CONFIG['id']}", json={})

        assert response.status_code == 200


# =============================================================================
# DELETE /api/v1/levels/{id}
# =============================================================================

class TestDeleteLevel:
    async def test_delete_success(self, client):
        with patch("app.api.v1.levels.LevelConfigRepository") as MockRepo:
            MockRepo.return_value = _mock_repo()
            response = await client.delete(f"{BASE}/{MOCK_LEVEL_CONFIG['id']}")

        assert response.status_code == 200

    async def test_delete_not_found(self, client):
        with patch("app.api.v1.levels.LevelConfigRepository") as MockRepo:
            MockRepo.return_value = _mock_repo(find_by_id=AsyncMock(return_value=None))
            response = await client.delete(f"{BASE}/999")

        assert response.status_code == 404


# =============================================================================
# PUT /api/v1/levels/reorder
# =============================================================================

class TestReorderLevels:
    async def test_reorder_success(self, client):
        """PUT /levels/reorder works after route ordering fix."""
        with patch("app.api.v1.levels.LevelConfigRepository") as MockRepo:
            MockRepo.return_value = _mock_repo()
            response = await client.put(
                f"{BASE}/reorder",
                json={"level_orders": {"1": 2, "2": 1}},
            )

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert "success" in body["message"].lower() or "reorder" in body["message"].lower()

    async def test_reorder_empty_accepted(self, client):
        """Empty level_orders dict is valid (no-op)."""
        with patch("app.api.v1.levels.LevelConfigRepository") as MockRepo:
            MockRepo.return_value = _mock_repo()
            response = await client.put(f"{BASE}/reorder", json={"level_orders": {}})

        assert response.status_code == 200

    async def test_reorder_unauthorized(self, client_no_auth):
        response = await client_no_auth.put(
            f"{BASE}/reorder",
            json={"level_orders": {"1": 2}},
        )
        assert response.status_code in (401, 403)


# =============================================================================
# POST /api/v1/levels/import
# =============================================================================

class TestImportLevels:
    async def test_import_success(self, client):
        """Import new level configurations."""
        import_payload = {
            "levels": [
                {
                    "level": 1,
                    "name": "车库小店",
                    "min_score": "0.00",
                    "max_score": "10.00",
                    "is_active": True,
                    "sort_order": 0,
                },
                {
                    "level": 2,
                    "name": "城市小店",
                    "min_score": "10.00",
                    "max_score": "25.00",
                    "is_active": True,
                    "sort_order": 1,
                },
            ],
            "replace_existing": False,
        }

        with patch("app.api.v1.levels.LevelConfigRepository") as MockRepo:
            mock_repo = _mock_repo()
            # First call: find_by_level returns None (level doesn't exist)
            # Second call: find_by_level returns None for level 2
            mock_repo.find_by_level = AsyncMock(return_value=None)
            mock_repo.create_level_config = AsyncMock(return_value={"id": 1})
            MockRepo.return_value = mock_repo

            response = await client.post(f"{BASE}/import", json=import_payload)

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert "imported_count" in body["data"]

    async def test_import_with_replace_existing(self, client):
        """Import with replace_existing=True deletes all existing levels first."""
        import_payload = {
            "levels": [
                {
                    "level": 1,
                    "name": "车库小店",
                    "min_score": "0.00",
                    "is_active": True,
                },
            ],
            "replace_existing": True,
        }

        with patch("app.api.v1.levels.LevelConfigRepository") as MockRepo:
            mock_repo = _mock_repo()
            mock_repo.delete_all = AsyncMock(return_value=True)
            mock_repo.create_level_config = AsyncMock(return_value={"id": 1})
            MockRepo.return_value = mock_repo

            response = await client.post(f"{BASE}/import", json=import_payload)

        assert response.status_code == 200
        body = response.json()
        assert body["code"] == 0
        assert body["data"]["imported_count"] == 1
        # Verify delete_all was called
        mock_repo.delete_all.assert_called_once()

    async def test_import_duplicate_levels_rejected(self, client):
        """Import with duplicate level numbers returns 400."""
        import_payload = {
            "levels": [
                {"level": 1, "name": "Level 1", "min_score": "0.00"},
                {"level": 1, "name": "Duplicate Level 1", "min_score": "100.00"},
            ],
            "replace_existing": False,
        }

        response = await client.post(f"{BASE}/import", json=import_payload)

        assert response.status_code == 400
        body = response.json()
        assert "duplicate" in body["message"].lower()

    async def test_import_empty_levels_rejected(self, client):
        """Import with empty levels array returns 422."""
        import_payload = {
            "levels": [],
            "replace_existing": False,
        }

        response = await client.post(f"{BASE}/import", json=import_payload)

        assert response.status_code == 422

    async def test_import_missing_levels_field(self, client):
        """Import without levels field returns 422."""
        response = await client.post(f"{BASE}/import", json={"replace_existing": False})

        assert response.status_code == 422

    async def test_import_unauthorized(self, client_no_auth):
        """Import without auth returns 401/403."""
        import_payload = {
            "levels": [{"level": 1, "name": "Test", "min_score": "0.00"}],
        }

        response = await client_no_auth.post(f"{BASE}/import", json=import_payload)
        assert response.status_code in (401, 403)
