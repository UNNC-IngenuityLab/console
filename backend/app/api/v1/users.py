"""User management API endpoints."""

from decimal import Decimal
from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query

from app.core.exceptions import NotFoundException, ValidationException
from app.db.repositories import UserRepository
from app.dependencies import (
    get_admin_log_repo,
    get_admin_user,
    get_client_ip,
    get_db_connection,
    get_user_repo,
)
from app.models import (
    ApiResponse,
    PaginatedResponse,
    UpdatePointsRequest,
    UpdateUserRequest,
    UserDetail,
    UserListQuery,
    UserSummary,
)

router = APIRouter()


@router.get("/", response_model=ApiResponse)
async def list_users(
    search: str | None = None,
    level: int | None = None,
    is_active: bool | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    sort_by: str = "created_at",
    sort_order: str = "DESC",
    current_user: Annotated[dict, Depends(get_admin_user)] = None,
    conn: Annotated[object, Depends(get_db_connection)] = None,
    user_repo: Annotated[UserRepository, Depends(get_user_repo)] = None,
) -> ApiResponse:
    """List users with filters and pagination."""
    query = UserListQuery(
        search=search,
        level=level,
        is_active=is_active,
        page=page,
        page_size=page_size,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    result = await user_repo.list_users(
        search=query.search,
        level=query.level,
        is_active=query.is_active,
        page=query.page,
        page_size=query.page_size,
        sort_by=query.sort_by,
        sort_order=query.sort_order,
    )

    # Format user data
    items = [UserSummary(**item).model_dump() for item in result["items"]]

    return ApiResponse(
        data=PaginatedResponse(
            items=items,
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
            total_pages=result["total_pages"],
        ).model_dump(),
    )


@router.get("/{user_id}", response_model=ApiResponse)
async def get_user(
    user_id: str,
    current_user: Annotated[dict, Depends(get_admin_user)] = None,
    user_repo: Annotated[UserRepository, Depends(get_user_repo)] = None,
) -> ApiResponse:
    """Get user by ID."""
    user = await user_repo.find_by_id(user_id)

    if user is None:
        raise NotFoundException("User not found")

    return ApiResponse(data=UserDetail(**user).model_dump())


@router.put("/{user_id}/points", response_model=ApiResponse)
async def update_user_points(
    user_id: str,
    data: UpdatePointsRequest,
    current_user: Annotated[dict, Depends(get_admin_user)] = None,
    user_repo: Annotated[UserRepository, Depends(get_user_repo)] = None,
    log_repo: Annotated[object, Depends(get_admin_log_repo)] = None,
    client_ip: Annotated[str | None, Depends(get_client_ip)] = None,
) -> ApiResponse:
    """Update user points."""
    user = await user_repo.find_by_id(user_id)

    if user is None:
        raise NotFoundException("User not found")

    old_points = user.get("total_points", Decimal("0.00"))

    success = await user_repo.update_points(user_id, data.points, data.reason)

    if not success:
        raise ValidationException("Failed to update points")

    # Log the action
    await log_repo.create(
        admin_openid=current_user.get("openid", ""),
        action="edit_points",
        target_id=user_id,
        description=f"Updated points for {user.get('student_id')}: {old_points} -> {data.points}. Reason: {data.reason}",
        old_value={"points": str(old_points)},
        new_value={"points": str(data.points), "reason": data.reason},
        ip_address=client_ip,
    )

    return ApiResponse(
        message="Points updated successfully",
        data={"old_points": str(old_points), "new_points": str(data.points)},
    )


@router.put("/{user_id}", response_model=ApiResponse)
async def update_user(
    user_id: str,
    data: UpdateUserRequest,
    current_user: Annotated[dict, Depends(get_admin_user)] = None,
    user_repo: Annotated[UserRepository, Depends(get_user_repo)] = None,
    log_repo: Annotated[object, Depends(get_admin_log_repo)] = None,
    client_ip: Annotated[str | None, Depends(get_client_ip)] = None,
) -> ApiResponse:
    """Update user information."""
    user = await user_repo.find_by_id(user_id)

    if user is None:
        raise NotFoundException("User not found")

    # Build update data
    update_data = {}
    old_values = {}
    new_values = {}

    if data.nickname is not None:
        update_data["nickname"] = data.nickname
        old_values["nickname"] = user.get("nickname")
        new_values["nickname"] = data.nickname

    if data.level is not None:
        update_data["level"] = data.level
        old_values["level"] = user.get("level")
        new_values["level"] = data.level

    if data.is_active is not None:
        update_data["is_active"] = 1 if data.is_active else 0
        old_values["is_active"] = user.get("is_active")
        new_values["is_active"] = data.is_active

    if not update_data:
        return ApiResponse(message="No changes provided")

    success = await user_repo.update("users", "id", user_id, update_data)

    if not success:
        raise ValidationException("Failed to update user")

    # Log the action
    await log_repo.create(
        admin_openid=current_user.get("openid", ""),
        action="ban_user" if (data.is_active is not None and not data.is_active) else "update_settings",
        target_id=user_id,
        description=f"Updated user {user.get('student_id')}",
        old_value=old_values if old_values else None,
        new_value=new_values if new_values else None,
        ip_address=client_ip,
    )

    return ApiResponse(message="User updated successfully")


@router.get("/{user_id}/activities", response_model=ApiResponse)
async def get_user_activities(
    user_id: str,
    current_user: Annotated[dict, Depends(get_admin_user)] = None,
    user_repo: Annotated[UserRepository, Depends(get_user_repo)] = None,
) -> ApiResponse:
    """Get all registered activities for a user."""
    user = await user_repo.find_by_id(user_id)

    if user is None:
        raise NotFoundException("User not found")

    activities = await user_repo.get_user_activities(user_id)

    return ApiResponse(data=activities)


@router.delete("/{user_id}", response_model=ApiResponse)
async def delete_user(
    user_id: str,
    current_user: Annotated[dict, Depends(get_admin_user)] = None,
    user_repo: Annotated[UserRepository, Depends(get_user_repo)] = None,
    log_repo: Annotated[object, Depends(get_admin_log_repo)] = None,
    client_ip: Annotated[str | None, Depends(get_client_ip)] = None,
) -> ApiResponse:
    """Delete a user."""
    user = await user_repo.find_by_id(user_id)

    if user is None:
        raise NotFoundException("User not found")

    success = await user_repo.delete_user(user_id)

    if not success:
        raise ValidationException("Failed to delete user")

    # Log the action
    await log_repo.create(
        admin_openid=current_user.get("openid", ""),
        action="delete_user",
        target_id=user_id,
        description=f"Deleted user {user.get('student_id')}",
        old_value={"user": user},
        ip_address=client_ip,
    )

    return ApiResponse(message="User deleted successfully")
