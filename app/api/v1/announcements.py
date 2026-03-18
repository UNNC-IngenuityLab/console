"""Announcement management API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.core.exceptions import NotFoundException, ValidationException
from app.core.security import generate_object_id
from app.db.repositories import AnnouncementRepository
from app.dependencies import (
    get_admin_log_repo,
    get_admin_user,
    get_client_ip,
    get_db_connection,
)
from app.models import (
    AnnouncementCreate,
    AnnouncementResponse,
    AnnouncementUpdate,
    ApiResponse,
    PaginatedResponse,
)

router = APIRouter()


@router.get("/", response_model=ApiResponse)
async def list_announcements(
    is_active: bool | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: Annotated[dict, Depends(get_admin_user)] = None,
    conn: Annotated[object, Depends(get_db_connection)] = None,
) -> ApiResponse:
    """List announcements with pagination."""
    repo = AnnouncementRepository(conn)
    result = await repo.list_announcements(is_active=is_active, page=page, page_size=page_size)

    items = [AnnouncementResponse(**item).model_dump() for item in result["items"]]

    return ApiResponse(
        data=PaginatedResponse(
            items=items,
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
            total_pages=result["total_pages"],
        ).model_dump(),
    )


@router.get("/{announcement_id}", response_model=ApiResponse)
async def get_announcement(
    announcement_id: str,
    current_user: Annotated[dict, Depends(get_admin_user)] = None,
    conn: Annotated[object, Depends(get_db_connection)] = None,
) -> ApiResponse:
    """Get announcement by ID."""
    repo = AnnouncementRepository(conn)
    announcement = await repo.find_by_id(announcement_id)

    if announcement is None:
        raise NotFoundException("Announcement not found")

    return ApiResponse(data=AnnouncementResponse(**announcement).model_dump())


@router.post("/", response_model=ApiResponse, status_code=201)
async def create_announcement(
    data: AnnouncementCreate,
    current_user: Annotated[dict, Depends(get_admin_user)] = None,
    conn: Annotated[object, Depends(get_db_connection)] = None,
    log_repo: Annotated[object, Depends(get_admin_log_repo)] = None,
    client_ip: Annotated[str | None, Depends(get_client_ip)] = None,
) -> ApiResponse:
    """Create a new announcement."""
    repo = AnnouncementRepository(conn)

    announcement_data = {
        "id": generate_object_id(),
        "creator_openid": current_user.get("openid", ""),
        "title": data.title,
        "content": data.content,
        "is_active": 1,
        "priority": data.priority,
    }

    announcement_id = await repo.create_announcement(announcement_data)

    # Log the action
    await log_repo.create(
        admin_openid=current_user.get("openid", ""),
        action="create_announcement",
        target_id=announcement_id,
        description=f"Created announcement: {data.title}",
        new_value={"title": data.title, "priority": data.priority},
        ip_address=client_ip,
    )

    return ApiResponse(
        message="Announcement created successfully",
        data={"announcement_id": announcement_id},
    )


@router.put("/{announcement_id}", response_model=ApiResponse)
async def update_announcement(
    announcement_id: str,
    data: AnnouncementUpdate,
    current_user: Annotated[dict, Depends(get_admin_user)] = None,
    conn: Annotated[object, Depends(get_db_connection)] = None,
    log_repo: Annotated[object, Depends(get_admin_log_repo)] = None,
    client_ip: Annotated[str | None, Depends(get_client_ip)] = None,
) -> ApiResponse:
    """Update an announcement."""
    repo = AnnouncementRepository(conn)
    announcement = await repo.find_by_id(announcement_id)

    if announcement is None:
        raise NotFoundException("Announcement not found")

    # Build update data
    update_data = {}
    old_values = {}
    new_values = {}

    for field in ["title", "content", "priority"]:
        value = getattr(data, field)
        if value is not None:
            update_data[field] = value
            old_values[field] = announcement.get(field)
            new_values[field] = value

    if data.is_active is not None:
        update_data["is_active"] = 1 if data.is_active else 0
        old_values["is_active"] = announcement.get("is_active")
        new_values["is_active"] = data.is_active

    if not update_data:
        return ApiResponse(message="No changes provided")

    success = await repo.update_announcement(announcement_id, update_data)

    if not success:
        raise ValidationException("Failed to update announcement")

    # Log the action
    await log_repo.create(
        admin_openid=current_user.get("openid", ""),
        action="update_settings" if "is_active" not in update_data else "delete_announcement",
        target_id=announcement_id,
        description=f"Updated announcement: {announcement.get('title')}",
        old_value=old_values if old_values else None,
        new_value=new_values if new_values else None,
        ip_address=client_ip,
    )

    return ApiResponse(message="Announcement updated successfully")


@router.delete("/{announcement_id}", response_model=ApiResponse)
async def delete_announcement(
    announcement_id: str,
    current_user: Annotated[dict, Depends(get_admin_user)] = None,
    conn: Annotated[object, Depends(get_db_connection)] = None,
    log_repo: Annotated[object, Depends(get_admin_log_repo)] = None,
    client_ip: Annotated[str | None, Depends(get_client_ip)] = None,
) -> ApiResponse:
    """Delete an announcement."""
    repo = AnnouncementRepository(conn)
    announcement = await repo.find_by_id(announcement_id)

    if announcement is None:
        raise NotFoundException("Announcement not found")

    success = await repo.delete_announcement(announcement_id)

    if not success:
        raise ValidationException("Failed to delete announcement")

    # Log the action
    await log_repo.create(
        admin_openid=current_user.get("openid", ""),
        action="delete_announcement",
        target_id=announcement_id,
        description=f"Deleted announcement: {announcement.get('title')}",
        old_value={"announcement": announcement},
        ip_address=client_ip,
    )

    return ApiResponse(message="Announcement deleted successfully")
