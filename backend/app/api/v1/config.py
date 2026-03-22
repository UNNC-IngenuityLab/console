"""UI configuration management API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends

from app.core.exceptions import NotFoundException, ValidationException
from app.db.repositories import UIConfigRepository
from app.dependencies import (
    get_admin_log_repo,
    get_admin_user,
    get_client_ip,
    get_db_connection,
)
from app.models import ApiResponse, BatchUIConfigUpdate, UIConfigResponse, UIConfigUpdate

router = APIRouter()


@router.get("/ui", response_model=ApiResponse)
async def list_ui_configs(
    current_user: Annotated[dict, Depends(get_admin_user)] = None,
    conn: Annotated[object, Depends(get_db_connection)] = None,
) -> ApiResponse:
    """Get all UI configurations."""
    repo = UIConfigRepository(conn)
    configs = await repo.get_all()

    items = [UIConfigResponse(**config).model_dump() for config in configs]

    # Group by category
    grouped = {}
    for item in items:
        category = item.pop("category", "general")
        if category not in grouped:
            grouped[category] = {}
        key = item.pop("key")
        grouped[category][key] = item

    return ApiResponse(data=grouped)


@router.get("/ui/category/{category}", response_model=ApiResponse)
async def get_ui_configs_by_category(
    category: str,
    current_user: Annotated[dict, Depends(get_admin_user)] = None,
    conn: Annotated[object, Depends(get_db_connection)] = None,
) -> ApiResponse:
    """Get UI configurations by category."""
    repo = UIConfigRepository(conn)
    configs = await repo.get_by_category(category)

    items = {config["key"]: UIConfigResponse(**config).model_dump() for config in configs}

    return ApiResponse(data=items)


@router.get("/ui/key/{key}", response_model=ApiResponse)
async def get_ui_config(
    key: str,
    current_user: Annotated[dict, Depends(get_admin_user)] = None,
    conn: Annotated[object, Depends(get_db_connection)] = None,
) -> ApiResponse:
    """Get a single UI configuration by key."""
    repo = UIConfigRepository(conn)
    config = await repo.get_by_key(key)

    if config is None:
        raise NotFoundException(f"UI config '{key}' not found")

    return ApiResponse(data=UIConfigResponse(**config).model_dump())


@router.put("/ui/{key}", response_model=ApiResponse)
async def update_ui_config(
    key: str,
    data: UIConfigUpdate,
    current_user: Annotated[dict, Depends(get_admin_user)] = None,
    conn: Annotated[object, Depends(get_db_connection)] = None,
    log_repo: Annotated[object, Depends(get_admin_log_repo)] = None,
    client_ip: Annotated[str | None, Depends(get_client_ip)] = None,
) -> ApiResponse:
    """Update a single UI configuration."""
    repo = UIConfigRepository(conn)

    # Get old value
    old_config = await repo.get_by_key(key)
    if old_config is None:
        raise NotFoundException(f"UI config '{key}' not found")

    success = await repo.update_config(key, data.value, current_user.get("openid", ""))

    if not success:
        raise ValidationException("Failed to update UI configuration")

    # Log the action
    await log_repo.create(
        admin_openid=current_user.get("openid", ""),
        action="update_ui_config",
        target_id=key,
        description=f"Updated UI config: {key}",
        old_value={"old_value": old_config.get("value")},
        new_value={"new_value": data.value},
        ip_address=client_ip,
    )

    return ApiResponse(message="UI configuration updated successfully")


@router.put("/ui/batch", response_model=ApiResponse)
async def batch_update_ui_configs(
    data: BatchUIConfigUpdate,
    current_user: Annotated[dict, Depends(get_admin_user)] = None,
    conn: Annotated[object, Depends(get_db_connection)] = None,
    log_repo: Annotated[object, Depends(get_admin_log_repo)] = None,
    client_ip: Annotated[str | None, Depends(get_client_ip)] = None,
) -> ApiResponse:
    """Batch update UI configurations."""
    repo = UIConfigRepository(conn)

    # Get old values
    old_values = {}
    for key in data.configs.keys():
        old_config = await repo.get_by_key(key)
        if old_config:
            old_values[key] = old_config.get("value")

    success = await repo.batch_update(data.configs, current_user.get("openid", ""))

    if not success:
        raise ValidationException("Failed to update UI configurations")

    # Log the action
    await log_repo.create(
        admin_openid=current_user.get("openid", ""),
        action="update_ui_config",
        target_id="batch",
        description=f"Batch updated {len(data.configs)} UI configs",
        old_value=old_values if old_values else None,
        new_value=data.configs,
        ip_address=client_ip,
    )

    return ApiResponse(message="UI configurations updated successfully")
