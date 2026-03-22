"""Activity management API endpoints."""

from io import BytesIO
from typing import Annotated

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import Response
from pydantic import BaseModel

from app.core.exceptions import NotFoundException, ValidationException
from app.core.security import generate_object_id
from app.db.repositories import ActivityRepository, SubActivityRepository
from app.dependencies import (
    get_admin_log_repo,
    get_admin_user,
    get_client_ip,
    get_db_connection,
)
from app.models import (
    ActivityCreate,
    ActivityDetail,
    ActivityListQuery,
    ActivityResponse,
    ActivityUpdate,
    ApiResponse,
    PaginatedResponse,
    QRCodeResponse,
    SubActivityCreate,
    SubActivityResponse,
    SubActivityUpdate,
)

router = APIRouter()


class SubActivityListCreate(BaseModel):
    """Request to create multiple sub-activities."""
    sub_activities: list[SubActivityCreate]


@router.get("/", response_model=ApiResponse)
async def list_activities(
    search: str | None = None,
    is_active: bool | None = None,
    start_date_from: str | None = None,
    start_date_to: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    current_user: Annotated[dict, Depends(get_admin_user)] = None,
    conn: Annotated[object, Depends(get_db_connection)] = None,
) -> ApiResponse:
    """List activities with filters and pagination."""
    activity_repo = ActivityRepository(conn)
    result = await activity_repo.list_activities(
        search=search,
        is_active=is_active,
        start_date_from=start_date_from,
        start_date_to=start_date_to,
        page=page,
        page_size=page_size,
    )

    items = [ActivityResponse(**item).model_dump() for item in result["items"]]

    return ApiResponse(
        data=PaginatedResponse(
            items=items,
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
            total_pages=result["total_pages"],
        ).model_dump(),
    )


@router.get("/{activity_id}", response_model=ApiResponse)
async def get_activity(
    activity_id: str,
    current_user: Annotated[dict, Depends(get_admin_user)] = None,
    conn: Annotated[object, Depends(get_db_connection)] = None,
) -> ApiResponse:
    """Get activity by ID with sub-activities."""
    activity_repo = ActivityRepository(conn)
    sub_activity_repo = SubActivityRepository(conn)

    activity = await activity_repo.find_by_id(activity_id)

    if activity is None:
        raise NotFoundException("Activity not found")

    sub_activities = await sub_activity_repo.list_by_activity(activity_id)
    sub_activity_data = [SubActivityResponse(**sa).model_dump() for sa in sub_activities]

    return ApiResponse(
        data=ActivityDetail(**{**activity, "sub_activities": sub_activity_data}).model_dump(),
    )


@router.post("/", response_model=ApiResponse, status_code=201)
async def create_activity(
    data: ActivityCreate,
    current_user: Annotated[dict, Depends(get_admin_user)] = None,
    conn: Annotated[object, Depends(get_db_connection)] = None,
    log_repo: Annotated[object, Depends(get_admin_log_repo)] = None,
    client_ip: Annotated[str | None, Depends(get_client_ip)] = None,
) -> ApiResponse:
    """Create a new activity."""
    activity_repo = ActivityRepository(conn)

    # Prepare activity data
    activity_data = {
        "id": generate_object_id(),
        "activity_id": int(datetime.now(timezone.utc).timestamp() * 1000),
        "creator_openid": current_user.get("openid", ""),
        "name": data.name,
        "venue": data.venue,
        "date_range": data.date_range,
        "start_date": data.start_date,
        "end_date": data.end_date,
        "total_point": data.total_point,
        "sign_up_count": 0,
        "completed_count": 0,
        "is_active": 1,
    }

    # Create activity
    activity_id = await activity_repo.create_activity(activity_data)

    # Create sub-activities
    sub_activity_repo = SubActivityRepository(conn)
    for idx, sub in enumerate(data.sub_activities):
        sub_data = {
            "activity_id": activity_id,
            "name": sub.name,
            "point": sub.point,
            "is_stopped": 0,
            "sort_order": sub.sort_order or idx,
        }
        await sub_activity_repo.create_sub_activity(sub_data)

    # Log the action
    await log_repo.create(
        admin_openid=current_user.get("openid", ""),
        action="create_activity",
        target_id=activity_id,
        description=f"Created activity: {data.name}",
        new_value={
            "name": data.name,
            "venue": data.venue,
            "date_range": data.date_range,
            "total_point": str(data.total_point),
            "sub_activities_count": len(data.sub_activities),
        },
        ip_address=client_ip,
    )

    return ApiResponse(
        message="Activity created successfully",
        data={"activity_id": activity_id},
    )


@router.put("/{activity_id}", response_model=ApiResponse)
async def update_activity(
    activity_id: str,
    data: ActivityUpdate,
    current_user: Annotated[dict, Depends(get_admin_user)] = None,
    conn: Annotated[object, Depends(get_db_connection)] = None,
    log_repo: Annotated[object, Depends(get_admin_log_repo)] = None,
    client_ip: Annotated[str | None, Depends(get_client_ip)] = None,
) -> ApiResponse:
    """Update an activity."""
    activity_repo = ActivityRepository(conn)
    activity = await activity_repo.find_by_id(activity_id)

    if activity is None:
        raise NotFoundException("Activity not found")

    # Build update data
    update_data = {}
    old_values = {}
    new_values = {}

    for field in ["name", "venue", "date_range", "start_date", "end_date", "total_point", "is_active"]:
        value = getattr(data, field)
        if value is not None:
            update_data[field] = value
            old_values[field] = activity.get(field)
            new_values[field] = value

    if data.is_active is not None:
        update_data["is_active"] = 1 if data.is_active else 0

    if not update_data:
        return ApiResponse(message="No changes provided")

    success = await activity_repo.update_activity(activity_id, update_data)

    if not success:
        raise ValidationException("Failed to update activity")

    # Log the action
    await log_repo.create(
        admin_openid=current_user.get("openid", ""),
        action="update_activity",
        target_id=activity_id,
        description=f"Updated activity: {activity.get('name')}",
        old_value=old_values if old_values else None,
        new_value=new_values if new_values else None,
        ip_address=client_ip,
    )

    return ApiResponse(message="Activity updated successfully")


@router.delete("/{activity_id}", response_model=ApiResponse)
async def delete_activity(
    activity_id: str,
    current_user: Annotated[dict, Depends(get_admin_user)] = None,
    conn: Annotated[object, Depends(get_db_connection)] = None,
    log_repo: Annotated[object, Depends(get_admin_log_repo)] = None,
    client_ip: Annotated[str | None, Depends(get_client_ip)] = None,
) -> ApiResponse:
    """Delete an activity."""
    activity_repo = ActivityRepository(conn)
    activity = await activity_repo.find_by_id(activity_id)

    if activity is None:
        raise NotFoundException("Activity not found")

    success = await activity_repo.delete_activity(activity_id)

    if not success:
        raise ValidationException("Failed to delete activity")

    # Log the action
    await log_repo.create(
        admin_openid=current_user.get("openid", ""),
        action="delete_activity",
        target_id=activity_id,
        description=f"Deleted activity: {activity.get('name')}",
        old_value={"activity": activity},
        ip_address=client_ip,
    )

    return ApiResponse(message="Activity deleted successfully")


# =============================================================================
# Sub-activity endpoints
# =============================================================================


@router.post("/{activity_id}/sub-activities", response_model=ApiResponse, status_code=201)
async def create_sub_activity(
    activity_id: str,
    data: SubActivityCreate,
    current_user: Annotated[dict, Depends(get_admin_user)] = None,
    conn: Annotated[object, Depends(get_db_connection)] = None,
    log_repo: Annotated[object, Depends(get_admin_log_repo)] = None,
    client_ip: Annotated[str | None, Depends(get_client_ip)] = None,
) -> ApiResponse:
    """Create a new sub-activity."""
    activity_repo = ActivityRepository(conn)
    activity = await activity_repo.find_by_id(activity_id)

    if activity is None:
        raise NotFoundException("Activity not found")

    sub_activity_repo = SubActivityRepository(conn)

    sub_data = {
        "activity_id": activity_id,
        "name": data.name,
        "point": data.point,
        "is_stopped": 0,
        "sort_order": data.sort_order,
    }

    sub_id = await sub_activity_repo.create_sub_activity(sub_data)

    # Update activity total points
    await activity_repo.update_signup_counts(activity_id)

    return ApiResponse(
        message="Sub-activity created successfully",
        data={"sub_activity_id": sub_id},
    )


@router.put("/sub-activities/{sub_activity_id}", response_model=ApiResponse)
async def update_sub_activity(
    sub_activity_id: int,
    data: SubActivityUpdate,
    current_user: Annotated[dict, Depends(get_admin_user)] = None,
    conn: Annotated[object, Depends(get_db_connection)] = None,
) -> ApiResponse:
    """Update a sub-activity."""
    sub_activity_repo = SubActivityRepository(conn)
    sub_activity = await sub_activity_repo.find_by_id(sub_activity_id)

    if sub_activity is None:
        raise NotFoundException("Sub-activity not found")

    # Build update data
    update_data = {}
    for field in ["name", "point", "is_stopped", "sort_order"]:
        value = getattr(data, field)
        if value is not None:
            update_data[field] = value

    if not update_data:
        return ApiResponse(message="No changes provided")

    success = await sub_activity_repo.update_sub_activity(sub_activity_id, update_data)

    if not success:
        raise ValidationException("Failed to update sub-activity")

    return ApiResponse(message="Sub-activity updated successfully")


@router.delete("/sub-activities/{sub_activity_id}", response_model=ApiResponse)
async def delete_sub_activity(
    sub_activity_id: int,
    current_user: Annotated[dict, Depends(get_admin_user)] = None,
    conn: Annotated[object, Depends(get_db_connection)] = None,
) -> ApiResponse:
    """Delete a sub-activity."""
    sub_activity_repo = SubActivityRepository(conn)
    sub_activity = await sub_activity_repo.find_by_id(sub_activity_id)

    if sub_activity is None:
        raise NotFoundException("Sub-activity not found")

    activity_id = sub_activity.get("activity_id")
    success = await sub_activity_repo.delete_sub_activity(sub_activity_id)

    if not success:
        raise ValidationException("Failed to delete sub-activity")

    # Update activity total points
    if activity_id:
        activity_repo = ActivityRepository(conn)
        await activity_repo.update_signup_counts(activity_id)

    return ApiResponse(message="Sub-activity deleted successfully")


# =============================================================================
# QR Code endpoint
# =============================================================================


@router.post("/{activity_id}/qrcode", response_model=ApiResponse)
async def generate_qr_code(
    activity_id: str,
    current_user: Annotated[dict, Depends(get_admin_user)] = None,
    conn: Annotated[object, Depends(get_db_connection)] = None,
) -> ApiResponse:
    """Generate a QR code for activity check-in.

    Returns a QR code containing the activity ID and expiration info.
    """
    activity_repo = ActivityRepository(conn)
    activity = await activity_repo.find_by_id(activity_id)

    if activity is None:
        raise NotFoundException("Activity not found")

    # Generate QR code data
    import base64
    import json
    from datetime import datetime, timedelta, timezone

    expires_at = datetime.now(timezone.utc) + timedelta(seconds=300)  # 5 minutes
    qr_data = {
        "type": "activity_checkin",
        "activity_id": activity_id,
        "activity_timestamp_id": activity.get("activity_id"),
        "expires_at": expires_at.isoformat(),
    }

    # Generate QR code image
    import qrcode
    from io import BytesIO

    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(json.dumps(qr_data))
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")

    # Convert to base64
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    img_str = base64.b64encode(buffer.getvalue()).decode()
    img_url = f"data:image/png;base64,{img_str}"

    return ApiResponse(
        data=QRCodeResponse(
            qr_code_url=img_url,
            activity_id=activity_id,
            activity_name=activity.get("name"),
            expires_at=expires_at.isoformat(),
        ).model_dump(),
    )
