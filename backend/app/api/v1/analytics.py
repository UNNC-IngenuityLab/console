"""Analytics and statistics API endpoints."""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Annotated

import aiomysql
from fastapi import APIRouter, Depends, Query

from app.dependencies import get_admin_user, get_db_connection
from app.models import (
    ActivityStats,
    ApiResponse,
    DashboardStats,
    LeaderboardEntry,
    LevelDistribution,
    TrendData,
)

router = APIRouter()


@router.get("/dashboard", response_model=ApiResponse)
async def get_dashboard_stats(
    current_user: Annotated[dict, Depends(get_admin_user)] = None,
    conn: Annotated[object, Depends(get_db_connection)] = None,
) -> ApiResponse:
    """Get dashboard statistics."""
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        # Total users
        await cursor.execute("SELECT COUNT(*) as count FROM users WHERE is_active = 1")
        total_users = (await cursor.fetchone())["count"]

        # Total activities
        await cursor.execute("SELECT COUNT(*) as count FROM activities")
        total_activities = (await cursor.fetchone())["count"]

        # Active activities
        await cursor.execute("SELECT COUNT(*) as count FROM activities WHERE is_active = 1")
        active_activities = (await cursor.fetchone())["count"]

        # Total signups（不依赖 activities.sign_up_count 字段）
        await cursor.execute("""
            SELECT COALESCE(SUM(t.sign_up_count), 0) AS total
            FROM (
                SELECT
                    a.id,
                    COUNT(DISTINCT ra.user_id) AS sign_up_count
                FROM activities a
                LEFT JOIN registered_activities ra ON a.id = ra.activity_id
                WHERE a.is_active = 1
                GROUP BY a.id
            ) t
        """)
        signups_result = await cursor.fetchone()
        total_signups = signups_result["total"] or 0

        # Total completions（不依赖 activities.completed_count 字段）
        await cursor.execute("""
            SELECT COALESCE(SUM(t.completed_count), 0) AS total
            FROM (
                SELECT
                    a.id,
                    SUM(CASE WHEN ra.is_completed = 1 THEN 1 ELSE 0 END) AS completed_count
                FROM activities a
                LEFT JOIN registered_activities ra ON a.id = ra.activity_id
                WHERE a.is_active = 1
                GROUP BY a.id
            ) t
        """)
        completions_result = await cursor.fetchone()
        total_completions = completions_result["total"] or 0

        # Average completion rate（按活动平均）
        await cursor.execute("""
            SELECT COALESCE(AVG(t.completion_rate), 0) AS avg_rate
            FROM (
                SELECT
                    a.id,
                    CASE
                        WHEN COUNT(DISTINCT ra.user_id) > 0
                        THEN ROUND(SUM(CASE WHEN ra.is_completed = 1 THEN 1 ELSE 0 END)
                            / COUNT(DISTINCT ra.user_id) * 100, 2)
                        ELSE 0
                    END AS completion_rate
                FROM activities a
                LEFT JOIN registered_activities ra ON a.id = ra.activity_id
                WHERE a.is_active = 1
                GROUP BY a.id
            ) t
        """)
        avg_result = await cursor.fetchone()
        avg_completion_rate = float(avg_result["avg_rate"] or 0)

        # Total points awarded
        await cursor.execute("SELECT SUM(total_points) as total FROM users")
        points_result = await cursor.fetchone()
        total_points_awarded = Decimal(points_result["total"] or 0)

    return ApiResponse(
        data=DashboardStats(
            total_users=total_users,
            total_activities=total_activities,
            active_activities=active_activities,
            total_signups=total_signups,
            total_completions=total_completions,
            avg_completion_rate=round(avg_completion_rate, 2),
            total_points_awarded=total_points_awarded,
        ).model_dump(),
    )


@router.get("/activity-stats", response_model=ApiResponse)
async def get_activity_stats(
    limit: int = Query(20, ge=1, le=100),
    current_user: Annotated[dict, Depends(get_admin_user)] = None,
    conn: Annotated[object, Depends(get_db_connection)] = None,
) -> ApiResponse:
    """Get activity completion statistics."""
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute(
            """
            SELECT
                a.id as activity_id,
                a.name as activity_name,
                COUNT(DISTINCT ra.user_id) AS sign_up_count,
                SUM(CASE WHEN ra.is_completed = 1 THEN 1 ELSE 0 END) AS completed_count,
                CASE
                    WHEN COUNT(DISTINCT ra.user_id) > 0
                    THEN ROUND(SUM(CASE WHEN ra.is_completed = 1 THEN 1 ELSE 0 END)
                        / COUNT(DISTINCT ra.user_id) * 100, 2)
                    ELSE 0
                END AS completion_rate,
                a.total_point as total_points
            FROM activities a
            LEFT JOIN registered_activities ra ON a.id = ra.activity_id
            WHERE a.is_active = 1
            GROUP BY a.id, a.name, a.total_point, a.start_date
            ORDER BY a.start_date DESC
            LIMIT %s
            """,
            (limit,),
        )
        rows = await cursor.fetchall()

    items = [
        ActivityStats(
            activity_id=row["activity_id"],
            activity_name=row["activity_name"],
            sign_up_count=row["sign_up_count"],
            completed_count=row["completed_count"],
            completion_rate=float(row["completion_rate"]),
            total_points=Decimal(row["total_points"]),
        ).model_dump()
        for row in rows
    ]

    return ApiResponse(data=items)


@router.get("/trend", response_model=ApiResponse)
async def get_trend_data(
    days: int = Query(30, ge=7, le=365),
    current_user: Annotated[dict, Depends(get_admin_user)] = None,
    conn: Annotated[object, Depends(get_db_connection)] = None,
) -> ApiResponse:
    """Get user activity trend data."""
    start_date = (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")

    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute(f"""
            SELECT
                DATE(created_at) as date,
                COUNT(*) as new_users
            FROM users
            WHERE DATE(created_at) >= '{start_date}'
            GROUP BY DATE(created_at)
            ORDER BY date
        """)
        user_rows = await cursor.fetchall()

        await cursor.execute(f"""
            SELECT
                DATE(registered_at) as date,
                COUNT(*) as new_signups
            FROM registered_activities
            WHERE DATE(registered_at) >= '{start_date}'
            GROUP BY DATE(registered_at)
            ORDER BY date
        """)
        signup_rows = await cursor.fetchall()

        await cursor.execute(f"""
            SELECT
                DATE(completed_at) as date,
                COUNT(*) as new_completions,
                SUM(points_earned) as points_awarded
            FROM registered_activities
            WHERE DATE(completed_at) >= '{start_date}' AND is_completed = 1
            GROUP BY DATE(completed_at)
            ORDER BY date
        """)
        completion_rows = await cursor.fetchall()

    # Merge data by date
    data_by_date = {}
    for i in range(days):
        date = (datetime.now(timezone.utc) - timedelta(days=days - 1 - i)).strftime("%Y-%m-%d")
        data_by_date[date] = {
            "date": date,
            "new_users": 0,
            "new_signups": 0,
            "new_completions": 0,
            "points_awarded": Decimal("0"),
        }

    for row in user_rows:
        date_str = str(row["date"])
        if date_str in data_by_date:
            data_by_date[date_str]["new_users"] = row["new_users"]

    for row in signup_rows:
        date_str = str(row["date"])
        if date_str in data_by_date:
            data_by_date[date_str]["new_signups"] = row["new_signups"]

    for row in completion_rows:
        date_str = str(row["date"])
        if date_str in data_by_date:
            data_by_date[date_str]["new_completions"] = row["new_completions"]
            data_by_date[date_str]["points_awarded"] = Decimal(row["points_awarded"])

    items = [TrendData(**data_by_date[date]).model_dump() for date in sorted(data_by_date.keys())]

    return ApiResponse(data=items)


@router.get("/leaderboard", response_model=ApiResponse)
async def get_leaderboard(
    limit: int = Query(50, ge=1, le=100),
    current_user: Annotated[dict, Depends(get_admin_user)] = None,
    conn: Annotated[object, Depends(get_db_connection)] = None,
) -> ApiResponse:
    """Get leaderboard data."""
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        await cursor.execute(f"""
            SELECT
                `rank`,
                id as user_id,
                student_id,
                nickname,
                avatar_url,
                total_points,
                level
            FROM v_leaderboard
            LIMIT {limit}
        """)
        rows = await cursor.fetchall()

    items = [
        LeaderboardEntry(
            rank=row["rank"],
            user_id=row["user_id"],
            student_id=row["student_id"],
            nickname=row.get("nickname"),
            avatar_url=row.get("avatar_url"),
            total_points=Decimal(row["total_points"]),
            level=row["level"],
        ).model_dump()
        for row in rows
    ]

    return ApiResponse(data=items)


@router.get("/level-distribution", response_model=ApiResponse)
async def get_level_distribution(
    current_user: Annotated[dict, Depends(get_admin_user)] = None,
    conn: Annotated[object, Depends(get_db_connection)] = None,
) -> ApiResponse:
    """Get user level distribution."""
    async with conn.cursor(aiomysql.DictCursor) as cursor:
        # Get total users
        await cursor.execute("SELECT COUNT(*) as total FROM users WHERE is_active = 1")
        total_result = await cursor.fetchone()
        total_users = total_result["total"]

        # Get level distribution
        await cursor.execute("""
            SELECT
                u.level,
                lc.name as level_name,
                COUNT(*) as user_count
            FROM users u
            LEFT JOIN level_configs lc ON u.level = lc.level
            WHERE u.is_active = 1
            GROUP BY u.level, lc.name
            ORDER BY u.level
        """)
        rows = await cursor.fetchall()

    items = []
    for row in rows:
        percentage = (row["user_count"] / total_users * 100) if total_users > 0 else 0
        items.append(
            LevelDistribution(
                level=row["level"],
                level_name=row.get("level_name") or f"Level {row['level']}",
                user_count=row["user_count"],
                percentage=round(percentage, 2),
            ).model_dump(),
        )

    return ApiResponse(data=items)
