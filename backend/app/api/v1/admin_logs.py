"""Admin log management API endpoints."""

import csv
from io import StringIO
from typing import Annotated

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response

from app.dependencies import get_admin_user, get_db_connection
from app.models import AdminLogQuery, AdminLogResponse, ApiResponse, PaginatedResponse

router = APIRouter()


@router.get("/", response_model=ApiResponse)
async def list_admin_logs(
    action: str | None = None,
    admin_openid: str | None = None,
    target_id: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    current_user: Annotated[dict, Depends(get_admin_user)] = None,
    conn: Annotated[object, Depends(get_db_connection)] = None,
) -> ApiResponse:
    """List admin logs with filters and pagination."""
    from app.db.repositories import AdminLogRepository

    repo = AdminLogRepository(conn)
    result = await repo.list_logs(
        action=action,
        admin_openid=admin_openid,
        target_id=target_id,
        page=page,
        page_size=page_size,
    )

    items = [AdminLogResponse(**item).model_dump() for item in result["items"]]

    return ApiResponse(
        data=PaginatedResponse(
            items=items,
            total=result["total"],
            page=result["page"],
            page_size=result["page_size"],
            total_pages=result["total_pages"],
        ).model_dump(),
    )


@router.get("/export", response_class=Response)
async def export_admin_logs(
    action: str | None = None,
    admin_openid: str | None = None,
    target_id: str | None = None,
    limit: int = Query(1000, ge=1, le=10000),
    current_user: Annotated[dict, Depends(get_admin_user)] = None,
    conn: Annotated[object, Depends(get_db_connection)] = None,
) -> Response:
    """Export admin logs as CSV."""
    from app.db.repositories import AdminLogRepository

    repo = AdminLogRepository(conn)
    result = await repo.list_logs(
        action=action,
        admin_openid=admin_openid,
        target_id=target_id,
        page=1,
        page_size=limit,
    )

    # Create CSV
    output = StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow(
        ["ID", "Admin OpenID", "Action", "Target ID", "Description", "IP Address", "Created At"]
    )

    # Rows
    for item in result["items"]:
        writer.writerow(
            [
                item["id"],
                item["admin_openid"],
                item["action"],
                item.get("target_id", ""),
                item["description"],
                item.get("ip_address", ""),
                item["created_at"],
            ]
        )

    # Return as downloadable file
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={
            "Content-Disposition": 'attachment; filename="admin_logs.csv"',
        },
    )
