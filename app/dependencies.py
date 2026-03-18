"""Dependency injection for the application."""

from functools import lru_cache
from typing import Annotated, Any

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.config import settings
from app.core.exceptions import UnauthorizedException
from app.core.security import decode_access_token
from app.db.repositories import (
    ActivityRepository,
    AdminLogRepository,
    AnnouncementRepository,
    LevelConfigRepository,
    SubActivityRepository,
    SystemSettingsRepository,
    UIConfigRepository,
    UserRepository,
)

security = HTTPBearer()


async def get_db_connection():
    """Get database connection from pool."""
    from app.db import get_connection
    async for conn in get_connection():
        yield conn


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)],
) -> dict[str, Any]:
    """Get the current authenticated user from JWT token."""
    token = credentials.credentials
    payload = decode_access_token(token)

    if payload is None:
        raise UnauthorizedException("Invalid or expired token")

    # Check if user exists and is active
    from app.db import get_pool
    pool = await get_pool()
    async with pool.acquire() as conn:
        repo = UserRepository(conn)
        user = await repo.find_by_id(payload.get("sub"))

    if user is None:
        raise UnauthorizedException("User not found")

    if not user.get("is_active"):
        raise UnauthorizedException("User account is disabled")

    return user


async def get_admin_user(
    current_user: Annotated[dict, Depends(get_current_user)],
) -> dict[str, Any]:
    """Get the current authenticated admin user.

    For now, we treat all active users as potential admins.
    In production, you should add an is_admin field to the users table.
    """
    # TODO: Add proper admin role checking
    # For now, allow all active users
    return current_user


def get_client_ip(
    x_forwarded_for: Annotated[str | None, Header(alias="X-Forwarded-For")] = None,
    x_real_ip: Annotated[str | None, Header(alias="X-Real-IP")] = None,
) -> str | None:
    """Get the client IP address from headers."""
    if x_forwarded_for:
        return x_forwarded_for.split(",")[0].strip()
    if x_real_ip:
        return x_real_ip
    return None


# Repository dependencies
async def get_user_repo(
    conn: Annotated[Any, Depends(get_db_connection)],
) -> UserRepository:
    """Get user repository."""
    return UserRepository(conn)


async def get_activity_repo(
    conn: Annotated[Any, Depends(get_db_connection)],
) -> ActivityRepository:
    """Get activity repository."""
    return ActivityRepository(conn)


async def get_sub_activity_repo(
    conn: Annotated[Any, Depends(get_db_connection)],
) -> SubActivityRepository:
    """Get sub-activity repository."""
    return SubActivityRepository(conn)


async def get_announcement_repo(
    conn: Annotated[Any, Depends(get_db_connection)],
) -> AnnouncementRepository:
    """Get announcement repository."""
    return AnnouncementRepository(conn)


async def get_level_config_repo(
    conn: Annotated[Any, Depends(get_db_connection)],
) -> LevelConfigRepository:
    """Get level config repository."""
    return LevelConfigRepository(conn)


async def get_ui_config_repo(
    conn: Annotated[Any, Depends(get_db_connection)],
) -> UIConfigRepository:
    """Get UI config repository."""
    return UIConfigRepository(conn)


async def get_system_settings_repo(
    conn: Annotated[Any, Depends(get_db_connection)],
) -> SystemSettingsRepository:
    """Get system settings repository."""
    return SystemSettingsRepository(conn)


async def get_admin_log_repo(
    conn: Annotated[Any, Depends(get_db_connection)],
) -> AdminLogRepository:
    """Get admin log repository."""
    return AdminLogRepository(conn)
