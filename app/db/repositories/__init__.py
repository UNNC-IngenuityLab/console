"""Database repositories for data access."""

from decimal import Decimal
from typing import Any

from app.db.queries import (
    SELECT_ACTIVITY_FIELDS,
    SELECT_ANNOUNCEMENT_FIELDS,
    SELECT_LEVEL_CONFIG_FIELDS,
    SELECT_USER_FIELDS,
)
from app.core.exceptions import NotFoundException


class BaseRepository:
    """Base repository with common database operations."""

    def __init__(self, conn):
        self.conn = conn

    async def execute(self, query: str, *args) -> Any:
        """Execute a query and return the result."""
        async with self.conn.cursor() as cursor:
            await cursor.execute(query, args)
            return cursor

    async def execute_many(self, query: str, args: list) -> Any:
        """Execute a query with multiple parameter sets."""
        async with self.conn.cursor() as cursor:
            await cursor.executemany(query, args)
            return cursor

    async def fetch_one(self, query: str, *args) -> dict | None:
        """Fetch a single row."""
        async with self.conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query, args)
            return await cursor.fetchone()

    async def fetch_all(self, query: str, *args) -> list[dict]:
        """Fetch all rows."""
        async with self.conn.cursor(aiomysql.DictCursor) as cursor:
            await cursor.execute(query, args)
            return await cursor.fetchall()

    async def fetch_page(
        self,
        query: str,
        params: tuple,
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        """Fetch a paginated result."""
        # Get total count
        count_query = f"SELECT COUNT(*) as total FROM ({query}) as count_query"
        total_result = await self.fetch_one(count_query, *params)
        total = total_result["total"] if total_result else 0

        # Get paginated data
        offset = (page - 1) * page_size
        paginated_query = f"{query} LIMIT %s OFFSET %s"
        items = await self.fetch_all(paginated_query, *params, page_size, offset)

        return {
            "items": items,
            "total": total,
            "page": page,
            "page_size": page_size,
            "total_pages": (total + page_size - 1) // page_size,
        }

    async def insert(self, table: str, data: dict) -> str | int:
        """Insert a row and return the inserted ID."""
        columns = ", ".join(data.keys())
        placeholders = ", ".join(["%s"] * len(data))
        query = f"INSERT INTO {table} ({columns}) VALUES ({placeholders})"
        async with self.conn.cursor() as cursor:
            await cursor.execute(query, list(data.values()))
            return cursor.lastrowid

    async def update(self, table: str, id_field: str, id_value: str | int, data: dict) -> bool:
        """Update a row by ID."""
        set_clause = ", ".join([f"{key} = %s" for key in data.keys()])
        query = f"UPDATE {table} SET {set_clause} WHERE {id_field} = %s"
        async with self.conn.cursor() as cursor:
            await cursor.execute(query, list(data.values()) + [id_value])
            return cursor.rowcount > 0

    async def delete(self, table: str, id_field: str, id_value: str | int) -> bool:
        """Delete a row by ID."""
        query = f"DELETE FROM {table} WHERE {id_field} = %s"
        async with self.conn.cursor() as cursor:
            await cursor.execute(query, (id_value,))
            return cursor.rowcount > 0


class UserRepository(BaseRepository):
    """Repository for user operations."""

    async def find_by_id(self, user_id: str) -> dict | None:
        """Find user by ID."""
        query = f"SELECT {SELECT_USER_FIELDS} FROM users WHERE id = %s"
        return await self.fetch_one(query, user_id)

    async def find_by_student_id(self, student_id: str) -> dict | None:
        """Find user by student ID."""
        query = f"SELECT {SELECT_USER_FIELDS} FROM users WHERE student_id = %s"
        return await self.fetch_one(query, student_id)

    async def find_by_openid(self, openid: str) -> dict | None:
        """Find user by WeChat OpenID."""
        query = f"SELECT {SELECT_USER_FIELDS} FROM users WHERE openid = %s"
        return await self.fetch_one(query, openid)

    async def list_users(
        self,
        search: str | None = None,
        level: int | None = None,
        is_active: bool | None = None,
        page: int = 1,
        page_size: int = 20,
        sort_by: str = "created_at",
        sort_order: str = "DESC",
    ) -> dict[str, Any]:
        """List users with filters and pagination."""
        conditions = []
        params = []

        if search:
            conditions.append("(student_id LIKE %s OR nickname LIKE %s)")
            params.extend([f"%{search}%", f"%{search}%"])

        if level is not None:
            conditions.append("level = %s")
            params.append(level)

        if is_active is not None:
            conditions.append("is_active = %s")
            params.append(is_active)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        # Validate sort column
        valid_sort_columns = {
            "created_at",
            "updated_at",
            "total_points",
            "level",
            "student_id",
            "nickname",
        }
        sort_column = sort_by if sort_by in valid_sort_columns else "created_at"
        sort_dir = sort_order if sort_order.upper() in ("ASC", "DESC") else "DESC"

        query = f"""
            SELECT {SELECT_USER_FIELDS}
            FROM users
            {where_clause}
            ORDER BY {sort_column} {sort_dir}
        """

        return await self.fetch_page(query, tuple(params), page, page_size)

    async def update_points(self, user_id: str, points: Decimal, reason: str) -> bool:
        """Update user points (will trigger level update via stored procedure)."""
        query = "UPDATE users SET total_points = %s WHERE id = %s"
        async with self.conn.cursor() as cursor:
            await cursor.execute(query, (points, user_id))
            return cursor.rowcount > 0

    async def update_level(self, user_id: str, level: int) -> bool:
        """Directly update user level."""
        query = "UPDATE users SET level = %s WHERE id = %s"
        async with self.conn.cursor() as cursor:
            await cursor.execute(query, (level, user_id))
            return cursor.rowcount > 0

    async def toggle_active(self, user_id: str, is_active: bool) -> bool:
        """Toggle user active status."""
        query = "UPDATE users SET is_active = %s WHERE id = %s"
        async with self.conn.cursor() as cursor:
            await cursor.execute(query, (is_active, user_id))
            return cursor.rowcount > 0

    async def delete_user(self, user_id: str) -> bool:
        """Delete a user (cascades to related records)."""
        return await self.delete("users", "id", user_id)


class ActivityRepository(BaseRepository):
    """Repository for activity operations."""

    async def find_by_id(self, activity_id: str) -> dict | None:
        """Find activity by ID."""
        query = f"SELECT {SELECT_ACTIVITY_FIELDS} FROM activities WHERE id = %s"
        return await self.fetch_one(query, activity_id)

    async def find_by_timestamp_id(self, timestamp_id: int) -> dict | None:
        """Find activity by timestamp ID."""
        query = f"SELECT {SELECT_ACTIVITY_FIELDS} FROM activities WHERE activity_id = %s"
        return await self.fetch_one(query, timestamp_id)

    async def list_activities(
        self,
        search: str | None = None,
        is_active: bool | None = None,
        start_date_from: str | None = None,
        start_date_to: str | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        """List activities with filters and pagination."""
        conditions = ["is_active >= 0"]  # Always include valid records
        params = []

        if search:
            conditions.append("(name LIKE %s OR venue LIKE %s)")
            params.extend([f"%{search}%", f"%{search}%"])

        if is_active is not None:
            conditions.append("is_active = %s")
            params.append(is_active)

        if start_date_from:
            conditions.append("start_date >= %s")
            params.append(start_date_from)

        if start_date_to:
            conditions.append("start_date <= %s")
            params.append(start_date_to)

        where_clause = f"WHERE {' AND '.join(conditions)}"

        query = f"""
            SELECT {SELECT_ACTIVITY_FIELDS}
            FROM activities
            {where_clause}
            ORDER BY start_date DESC, created_at DESC
        """

        return await self.fetch_page(query, tuple(params), page, page_size)

    async def create_activity(self, data: dict) -> str:
        """Create a new activity."""
        activity_id = int(datetime.now().timestamp() * 1000)
        data["activity_id"] = activity_id
        data["id"] = generate_object_id()
        await self.insert("activities", data)
        return data["id"]

    async def update_activity(self, activity_id: str, data: dict) -> bool:
        """Update an activity."""
        return await self.update("activities", "id", activity_id, data)

    async def delete_activity(self, activity_id: str) -> bool:
        """Delete an activity (cascades to sub-activities and registrations)."""
        return await self.delete("activities", "id", activity_id)

    async def update_signup_counts(self, activity_id: str) -> None:
        """Recalculate signup and completion counts for an activity."""
        query = """
            UPDATE activities a
            SET
                sign_up_count = (
                    SELECT COUNT(*)
                    FROM registered_activities
                    WHERE activity_id = %s
                ),
                completed_count = (
                    SELECT COUNT(*)
                    FROM registered_activities
                    WHERE activity_id = %s AND is_completed = 1
                )
            WHERE id = %s
        """
        await self.execute(query, activity_id, activity_id, activity_id)


class SubActivityRepository(BaseRepository):
    """Repository for sub-activity operations."""

    async def find_by_id(self, sub_activity_id: int) -> dict | None:
        """Find sub-activity by ID."""
        query = """
            SELECT id, activity_id, name, point, is_stopped, sort_order, created_at, updated_at
            FROM sub_activities
            WHERE id = %s
        """
        return await self.fetch_one(query, sub_activity_id)

    async def list_by_activity(self, activity_id: str) -> list[dict]:
        """List all sub-activities for an activity."""
        query = """
            SELECT id, activity_id, name, point, is_stopped, sort_order, created_at, updated_at
            FROM sub_activities
            WHERE activity_id = %s
            ORDER BY sort_order ASC, id ASC
        """
        return await self.fetch_all(query, activity_id)

    async def create_sub_activity(self, data: dict) -> int:
        """Create a new sub-activity."""
        data["id"] = int(datetime.now().timestamp() * 1000)
        await self.insert("sub_activities", data)
        return data["id"]

    async def update_sub_activity(self, sub_activity_id: int, data: dict) -> bool:
        """Update a sub-activity."""
        return await self.update("sub_activities", "id", sub_activity_id, data)

    async def delete_sub_activity(self, sub_activity_id: int) -> bool:
        """Delete a sub-activity."""
        return await self.delete("sub_activities", "id", sub_activity_id)


class AnnouncementRepository(BaseRepository):
    """Repository for announcement operations."""

    async def find_by_id(self, announcement_id: str) -> dict | None:
        """Find announcement by ID."""
        query = f"SELECT {SELECT_ANNOUNCEMENT_FIELDS} FROM announcements WHERE id = %s"
        return await self.fetch_one(query, announcement_id)

    async def list_announcements(
        self,
        is_active: bool | None = None,
        page: int = 1,
        page_size: int = 20,
    ) -> dict[str, Any]:
        """List announcements with pagination."""
        conditions = []
        params = []

        if is_active is not None:
            conditions.append("is_active = %s")
            params.append(is_active)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        query = f"""
            SELECT {SELECT_ANNOUNCEMENT_FIELDS}
            FROM announcements
            {where_clause}
            ORDER BY priority DESC, created_at DESC
        """

        return await self.fetch_page(query, tuple(params), page, page_size)

    async def create_announcement(self, data: dict) -> str:
        """Create a new announcement."""
        data["id"] = generate_object_id()
        await self.insert("announcements", data)
        return data["id"]

    async def update_announcement(self, announcement_id: str, data: dict) -> bool:
        """Update an announcement."""
        return await self.update("announcements", "id", announcement_id, data)

    async def delete_announcement(self, announcement_id: str) -> bool:
        """Delete an announcement."""
        return await self.delete("announcements", "id", announcement_id)


class LevelConfigRepository(BaseRepository):
    """Repository for level configuration operations."""

    async def find_by_id(self, level_config_id: int) -> dict | None:
        """Find level config by ID."""
        query = f"SELECT {SELECT_LEVEL_CONFIG_FIELDS} FROM level_configs WHERE id = %s"
        return await self.fetch_one(query, level_config_id)

    async def find_by_level(self, level: int) -> dict | None:
        """Find level config by level number."""
        query = f"SELECT {SELECT_LEVEL_CONFIG_FIELDS} FROM level_configs WHERE level = %s"
        return await self.fetch_one(query, level)

    async def list_all(self, is_active: bool | None = None) -> list[dict]:
        """List all level configs."""
        conditions = []
        params = []

        if is_active is not None:
            conditions.append("is_active = %s")
            params.append(is_active)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        query = f"""
            SELECT {SELECT_LEVEL_CONFIG_FIELDS}
            FROM level_configs
            {where_clause}
            ORDER BY sort_order ASC, level ASC
        """

        return await self.fetch_all(query, *params)

    async def create_level_config(self, data: dict) -> int:
        """Create a new level config."""
        await self.insert("level_configs", data)
        return await self.fetch_one("SELECT LAST_INSERT_ID() as id")

    async def update_level_config(self, level_config_id: int, data: dict) -> bool:
        """Update a level config."""
        return await self.update("level_configs", "id", level_config_id, data)

    async def delete_level_config(self, level_config_id: int) -> bool:
        """Delete a level config."""
        return await self.delete("level_configs", "id", level_config_id)

    async def reorder_levels(self, level_orders: dict[int, int]) -> bool:
        """Update sort orders for multiple levels."""
        values = [(sort_order, level) for level, sort_order in level_orders.items()]
        query = "UPDATE level_configs SET sort_order = %s WHERE level = %s"
        await self.execute_many(query, values)
        return True


class UIConfigRepository(BaseRepository):
    """Repository for UI configuration operations."""

    async def get_all(self) -> list[dict]:
        """Get all UI configs."""
        query = """
            SELECT key, value, type, category, label, description, min_value, max_value,
                   allowed_values, updated_at, updated_by
            FROM ui_configs
            ORDER BY category, key
        """
        return await self.fetch_all(query)

    async def get_by_category(self, category: str) -> list[dict]:
        """Get UI configs by category."""
        query = """
            SELECT key, value, type, category, label, description, min_value, max_value,
                   allowed_values, updated_at, updated_by
            FROM ui_configs
            WHERE category = %s
            ORDER BY key
        """
        return await self.fetch_all(query, category)

    async def get_by_key(self, key: str) -> dict | None:
        """Get a single UI config by key."""
        query = """
            SELECT key, value, type, category, label, description, min_value, max_value,
                   allowed_values, updated_at, updated_by
            FROM ui_configs
            WHERE key = %s
        """
        return await self.fetch_one(query, key)

    async def update_config(self, key: str, value: str, updated_by: str) -> bool:
        """Update a single UI config."""
        query = "UPDATE ui_configs SET value = %s, updated_by = %s WHERE `key` = %s"
        async with self.conn.cursor() as cursor:
            await cursor.execute(query, (value, updated_by, key))
            return cursor.rowcount > 0

    async def batch_update(self, configs: dict[str, str], updated_by: str) -> bool:
        """Update multiple UI configs."""
        values = [(value, updated_by, key) for key, value in configs.items()]
        query = "UPDATE ui_configs SET value = %s, updated_by = %s WHERE `key` = %s"
        await self.execute_many(query, values)
        return True


class SystemSettingsRepository(BaseRepository):
    """Repository for system settings operations."""

    async def get(self) -> dict | None:
        """Get system settings (singleton)."""
        query = """
            SELECT id, qr_code_expiration_seconds, max_points_per_activity,
                   max_points_per_sub_activity, registration_open, new_user_initial_points,
                   leaderboard_top_n, leaderboard_refresh_interval_seconds, activities_per_page,
                   scan_rate_limit_per_minute, maintenance_mode, maintenance_message, updated_at
            FROM system_settings
            WHERE id = 'system'
        """
        return await self.fetch_one(query)

    async def update(self, data: dict) -> bool:
        """Update system settings."""
        set_clause = ", ".join([f"{key} = %s" for key in data.keys()])
        query = f"UPDATE system_settings SET {set_clause} WHERE id = 'system'"
        async with self.conn.cursor() as cursor:
            await cursor.execute(query, list(data.values()))
            return cursor.rowcount > 0


class AdminLogRepository(BaseRepository):
    """Repository for admin log operations."""

    async def create(
        self,
        admin_openid: str,
        action: str,
        target_id: str | None,
        description: str,
        old_value: dict | None = None,
        new_value: dict | None = None,
        ip_address: str | None = None,
    ) -> int:
        """Create an admin log entry."""
        import json

        data = {
            "admin_openid": admin_openid,
            "action": action,
            "target_id": target_id,
            "description": description,
            "old_value": json.dumps(old_value) if old_value else None,
            "new_value": json.dumps(new_value) if new_value else None,
            "ip_address": ip_address,
        }
        await self.insert("admin_logs", data)
        result = await self.fetch_one("SELECT LAST_INSERT_ID() as id")
        return result["id"] if result else 0

    async def list_logs(
        self,
        action: str | None = None,
        admin_openid: str | None = None,
        target_id: str | None = None,
        page: int = 1,
        page_size: int = 50,
    ) -> dict[str, Any]:
        """List admin logs with filters."""
        conditions = []
        params = []

        if action:
            conditions.append("action = %s")
            params.append(action)

        if admin_openid:
            conditions.append("admin_openid = %s")
            params.append(admin_openid)

        if target_id:
            conditions.append("target_id = %s")
            params.append(target_id)

        where_clause = f"WHERE {' AND '.join(conditions)}" if conditions else ""

        query = f"""
            SELECT id, admin_openid, action, target_id, description, old_value, new_value,
                   ip_address, created_at
            FROM admin_logs
            {where_clause}
            ORDER BY created_at DESC
        """

        return await self.fetch_page(query, tuple(params), page, page_size)


# Import for timestamp generation
from datetime import datetime
from app.core.security import generate_object_id
import aiomysql
