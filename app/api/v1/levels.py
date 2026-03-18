"""Level configuration management API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.core.exceptions import NotFoundException, ValidationException
from app.db.repositories import LevelConfigRepository
from app.dependencies import (
    get_admin_log_repo,
    get_admin_user,
    get_client_ip,
    get_db_connection,
)
from app.models import (
    ApiResponse,
    LevelConfigCreate,
    LevelConfigResponse,
    LevelConfigUpdate,
    ReorderLevelsRequest,
)

router = APIRouter()


@router.get("/", response_model=ApiResponse)
async def list_level_configs(
    is_active: bool | None = None,
    current_user: Annotated[dict, Depends(get_admin_user)] = None,
    conn: Annotated[object, Depends(get_db_connection)] = None,
) -> ApiResponse:
    """List all level configurations."""
    repo = LevelConfigRepository(conn)
    levels = await repo.list_all(is_active=is_active)

    items = [LevelConfigResponse(**level).model_dump() for level in levels]

    return ApiResponse(data=items)


@router.get("/export", response_model=ApiResponse)
async def export_level_configs(
    current_user: Annotated[dict, Depends(get_admin_user)] = None,
    conn: Annotated[object, Depends(get_db_connection)] = None,
) -> ApiResponse:
    """Export level configurations as JSON."""
    repo = LevelConfigRepository(conn)
    levels = await repo.list_all(is_active=None)

    # Format for export
    export_data = [
        {
            "level": level["level"],
            "name": level["name"],
            "name_en": level.get("name_en"),
            "name_zh_tw": level.get("name_zh_tw"),
            "min_score": str(level["min_score"]),
            "max_score": str(level["max_score"]) if level.get("max_score") else None,
            "icon_url": level.get("icon_url"),
            "icon_dark_url": level.get("icon_dark_url"),
            "bg_color": level.get("bg_color"),
            "bg_gradient_start": level.get("bg_gradient_start"),
            "bg_gradient_end": level.get("bg_gradient_end"),
            "description": level.get("description"),
            "description_en": level.get("description_en"),
            "animation_type": level.get("animation_type"),
            "sound_url": level.get("sound_url"),
            "is_active": level.get("is_active"),
            "sort_order": level.get("sort_order"),
        }
        for level in levels
    ]

    return ApiResponse(
        data={
            "levels": export_data,
            "exported_at": levels[0]["updated_at"] if levels else None,
        },
    )


@router.get("/{level_config_id}", response_model=ApiResponse)
async def get_level_config(
    level_config_id: int,
    current_user: Annotated[dict, Depends(get_admin_user)] = None,
    conn: Annotated[object, Depends(get_db_connection)] = None,
) -> ApiResponse:
    """Get level config by ID."""
    repo = LevelConfigRepository(conn)
    level = await repo.find_by_id(level_config_id)

    if level is None:
        raise NotFoundException("Level config not found")

    return ApiResponse(data=LevelConfigResponse(**level).model_dump())


@router.post("/", response_model=ApiResponse, status_code=201)
async def create_level_config(
    data: LevelConfigCreate,
    current_user: Annotated[dict, Depends(get_admin_user)] = None,
    conn: Annotated[object, Depends(get_db_connection)] = None,
    log_repo: Annotated[object, Depends(get_admin_log_repo)] = None,
    client_ip: Annotated[str | None, Depends(get_client_ip)] = None,
) -> ApiResponse:
    """Create a new level configuration."""
    repo = LevelConfigRepository(conn)

    # Check if level already exists
    existing = await repo.find_by_level(data.level)
    if existing:
        raise ValidationException(f"Level {data.level} already exists")

    level_data = {
        "level": data.level,
        "name": data.name,
        "name_en": data.name_en,
        "name_zh_tw": data.name_zh_tw,
        "min_score": data.min_score,
        "max_score": data.max_score,
        "icon_url": data.icon_url,
        "icon_dark_url": data.icon_dark_url,
        "bg_color": data.bg_color,
        "bg_gradient_start": data.bg_gradient_start,
        "bg_gradient_end": data.bg_gradient_end,
        "description": data.description,
        "description_en": data.description_en,
        "animation_type": data.animation_type,
        "sound_url": data.sound_url,
        "is_active": 1 if data.is_active else 0,
        "sort_order": data.sort_order,
    }

    result = await repo.create_level_config(level_data)

    # Log the action
    await log_repo.create(
        admin_openid=current_user.get("openid", ""),
        action="create_level",
        target_id=str(result.get("id", "")) if result else "",
        description=f"Created level {data.level}: {data.name}",
        new_value=level_data,
        ip_address=client_ip,
    )

    return ApiResponse(
        message="Level configuration created successfully",
        data={"level_id": result.get("id") if result else None},
    )


@router.put("/{level_config_id}", response_model=ApiResponse)
async def update_level_config(
    level_config_id: int,
    data: LevelConfigUpdate,
    current_user: Annotated[dict, Depends(get_admin_user)] = None,
    conn: Annotated[object, Depends(get_db_connection)] = None,
    log_repo: Annotated[object, Depends(get_admin_log_repo)] = None,
    client_ip: Annotated[str | None, Depends(get_client_ip)] = None,
) -> ApiResponse:
    """Update a level configuration."""
    repo = LevelConfigRepository(conn)
    level = await repo.find_by_id(level_config_id)

    if level is None:
        raise NotFoundException("Level config not found")

    # Build update data
    update_data = {}
    old_values = {}
    new_values = {}

    for field in [
        "name",
        "name_en",
        "name_zh_tw",
        "min_score",
        "max_score",
        "icon_url",
        "icon_dark_url",
        "bg_color",
        "bg_gradient_start",
        "bg_gradient_end",
        "description",
        "description_en",
        "animation_type",
        "sound_url",
        "sort_order",
    ]:
        value = getattr(data, field)
        if value is not None:
            update_data[field] = value
            old_values[field] = level.get(field)
            new_values[field] = value

    if data.is_active is not None:
        update_data["is_active"] = 1 if data.is_active else 0
        old_values["is_active"] = level.get("is_active")
        new_values["is_active"] = data.is_active

    if not update_data:
        return ApiResponse(message="No changes provided")

    success = await repo.update_level_config(level_config_id, update_data)

    if not success:
        raise ValidationException("Failed to update level configuration")

    # Log the action
    await log_repo.create(
        admin_openid=current_user.get("openid", ""),
        action="update_level",
        target_id=str(level_config_id),
        description=f"Updated level {level.get('level')}: {level.get('name')}",
        old_value=old_values if old_values else None,
        new_value=new_values if new_values else None,
        ip_address=client_ip,
    )

    return ApiResponse(message="Level configuration updated successfully")


@router.delete("/{level_config_id}", response_model=ApiResponse)
async def delete_level_config(
    level_config_id: int,
    current_user: Annotated[dict, Depends(get_admin_user)] = None,
    conn: Annotated[object, Depends(get_db_connection)] = None,
    log_repo: Annotated[object, Depends(get_admin_log_repo)] = None,
    client_ip: Annotated[str | None, Depends(get_client_ip)] = None,
) -> ApiResponse:
    """Delete a level configuration."""
    repo = LevelConfigRepository(conn)
    level = await repo.find_by_id(level_config_id)

    if level is None:
        raise NotFoundException("Level config not found")

    success = await repo.delete_level_config(level_config_id)

    if not success:
        raise ValidationException("Failed to delete level configuration")

    # Log the action
    await log_repo.create(
        admin_openid=current_user.get("openid", ""),
        action="delete_level",
        target_id=str(level_config_id),
        description=f"Deleted level {level.get('level')}: {level.get('name')}",
        old_value={"level": level},
        ip_address=client_ip,
    )

    return ApiResponse(message="Level configuration deleted successfully")


@router.put("/reorder", response_model=ApiResponse)
async def reorder_levels(
    data: ReorderLevelsRequest,
    current_user: Annotated[dict, Depends(get_admin_user)] = None,
    conn: Annotated[object, Depends(get_db_connection)] = None,
    log_repo: Annotated[object, Depends(get_admin_log_repo)] = None,
    client_ip: Annotated[str | None, Depends(get_client_ip)] = None,
) -> ApiResponse:
    """Reorder level configurations."""
    repo = LevelConfigRepository(conn)

    success = await repo.reorder_levels(data.level_orders)

    if not success:
        raise ValidationException("Failed to reorder levels")

    # Log the action
    await log_repo.create(
        admin_openid=current_user.get("openid", ""),
        action="reorder_levels",
        target_id=None,
        description=f"Reordered levels: {data.level_orders}",
        new_value={"level_orders": data.level_orders},
        ip_address=client_ip,
    )

    return ApiResponse(message="Levels reordered successfully")
