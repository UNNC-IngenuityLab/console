"""System settings management API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.exceptions import NotFoundException, ValidationException
from app.db.repositories import SystemSettingsRepository
from app.dependencies import (
    get_admin_log_repo,
    get_admin_user,
    get_client_ip,
    get_db_connection,
)
from app.models import ApiResponse, SystemSettingsResponse, SystemSettingsUpdate

router = APIRouter()


@router.get("/", response_model=ApiResponse)
async def get_system_settings(
    current_user: Annotated[dict, Depends(get_admin_user)] = None,
    conn: Annotated[object, Depends(get_db_connection)] = None,
) -> ApiResponse:
    """Get system settings."""
    repo = SystemSettingsRepository(conn)
    settings = await repo.get()

    if settings is None:
        raise NotFoundException("System settings not found")

    return ApiResponse(data=SystemSettingsResponse(**settings).model_dump())


@router.put("/", response_model=ApiResponse)
async def update_system_settings(
    data: SystemSettingsUpdate,
    current_user: Annotated[dict, Depends(get_admin_user)] = None,
    conn: Annotated[object, Depends(get_db_connection)] = None,
    log_repo: Annotated[object, Depends(get_admin_log_repo)] = None,
    client_ip: Annotated[str | None, Depends(get_client_ip)] = None,
) -> ApiResponse:
    """Update system settings."""
    repo = SystemSettingsRepository(conn)

    # Get old settings
    old_settings = await repo.get()
    if old_settings is None:
        raise NotFoundException("System settings not found")

    # Build update data
    update_data = {}
    old_values = {}
    new_values = {}

    for field in [
        "qr_code_expiration_seconds",
        "max_points_per_activity",
        "max_points_per_sub_activity",
        "registration_open",
        "new_user_initial_points",
        "leaderboard_top_n",
        "leaderboard_refresh_interval_seconds",
        "activities_per_page",
        "scan_rate_limit_per_minute",
        "maintenance_mode",
        "maintenance_message",
    ]:
        value = getattr(data, field)
        if value is not None:
            update_data[field] = value
            old_values[field] = old_settings.get(field)
            new_values[field] = value

    if not update_data:
        return ApiResponse(message="No changes provided")

    success = await repo.update(update_data)

    if not success:
        raise ValidationException("Failed to update system settings")

    # Log the action
    await log_repo.create(
        admin_openid=current_user.get("openid", ""),
        action="update_settings",
        target_id="system",
        description="Updated system settings",
        old_value=old_values if old_values else None,
        new_value=new_values if new_values else None,
        ip_address=client_ip,
    )

    return ApiResponse(message="System settings updated successfully")
