"""Pydantic models for request/response validation."""

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, Field, field_validator, model_validator


class BaseResponse(BaseModel):
    """Base response model: auto-converts date/datetime to ISO string."""

    @model_validator(mode="before")
    @classmethod
    def _convert_datetimes(cls, data: Any) -> Any:
        if isinstance(data, dict):
            return {
                k: str(v) if isinstance(v, (datetime, date)) else v
                for k, v in data.items()
            }
        return data

    model_config = {"from_attributes": True}


# =============================================================================
# Base Response Models
# =============================================================================

class ApiResponse(BaseModel):
    """Standard API response wrapper."""
    code: int = Field(default=0, description="Response code (0 for success)")
    message: str = Field(default="success", description="Response message")
    data: Any = Field(default=None, description="Response data")


class PaginatedResponse(BaseModel):
    """Paginated response data."""
    items: list[Any]
    total: int
    page: int
    page_size: int
    total_pages: int


# =============================================================================
# Authentication Models
# =============================================================================

class LoginRequest(BaseModel):
    """Admin login request."""
    student_id: str = Field(..., min_length=1, max_length=20)
    password: str = Field(..., min_length=1)


class LoginResponse(BaseModel):
    """Login response with token."""
    access_token: str
    token_type: str = "bearer"
    user: "UserSummary"


# =============================================================================
# User Models
# =============================================================================

class UserSummary(BaseResponse):
    """Basic user information."""
    id: str
    student_id: str
    nickname: str | None = None
    avatar_url: str | None = None
    total_points: Decimal
    level: int
    is_active: bool


class UserDetail(UserSummary):
    """Detailed user information."""
    openid: str
    created_at: str
    updated_at: str


class UserListQuery(BaseModel):
    """Query parameters for user list."""
    search: str | None = None
    level: int | None = None
    is_active: bool | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)
    sort_by: str = "created_at"
    sort_order: str = "DESC"


class UpdatePointsRequest(BaseModel):
    """Request to update user points."""
    points: Decimal = Field(..., ge=0)
    reason: str = Field(..., min_length=1, max_length=500)


class UpdateUserRequest(BaseModel):
    """Request to update user info."""
    nickname: str | None = Field(None, max_length=100)
    level: int | None = Field(None, ge=1, le=10)
    is_active: bool | None = None


# =============================================================================
# Activity Models
# =============================================================================

class SubActivityCreate(BaseModel):
    """Request to create a sub-activity."""
    name: str = Field(..., min_length=1, max_length=255)
    point: Decimal = Field(..., ge=0, le=50)
    sort_order: int = Field(default=0, ge=0)


class SubActivityUpdate(BaseModel):
    """Request to update a sub-activity."""
    name: str | None = Field(None, min_length=1, max_length=255)
    point: Decimal | None = Field(None, ge=0, le=50)
    is_stopped: bool | None = None
    sort_order: int | None = Field(None, ge=0)


class SubActivityResponse(BaseResponse):
    """Sub-activity response."""
    id: int
    activity_id: str
    name: str
    point: Decimal
    is_stopped: bool
    sort_order: int
    created_at: str
    updated_at: str


class ActivityCreate(BaseModel):
    """Request to create an activity."""
    name: str = Field(..., min_length=1, max_length=255)
    venue: str = Field(..., min_length=1, max_length=255)
    start_date: datetime = Field(..., description="Activity start datetime")
    end_date: datetime = Field(..., description="Activity end datetime")
    total_point: Decimal = Field(default=Decimal("0.00"), ge=0, le=100)
    sub_activities: list[SubActivityCreate] = []


class ActivityUpdate(BaseModel):
    """Request to update an activity."""
    name: str | None = Field(None, min_length=1, max_length=255)
    venue: str | None = Field(None, min_length=1, max_length=255)
    start_date: datetime | None = None
    end_date: datetime | None = None
    total_point: Decimal | None = Field(None, ge=0, le=100)
    is_active: bool | None = None


class ActivityResponse(BaseResponse):
    """Activity response."""
    id: str
    activity_id: int
    creator_openid: str | None
    name: str
    venue: str
    start_date: str | None
    end_date: str | None
    total_point: Decimal
    sign_up_count: int
    completed_count: int
    is_active: bool
    created_at: str
    updated_at: str
    sub_activity_count: int = 0


class ActivityDetail(ActivityResponse):
    """Activity detail with sub-activities."""
    sub_activities: list[SubActivityResponse] = []


class ActivityListQuery(BaseModel):
    """Query parameters for activity list."""
    search: str | None = None
    is_active: bool | None = None
    start_date_from: str | None = None
    start_date_to: str | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=20, ge=1, le=100)


# =============================================================================
# Announcement Models
# =============================================================================

class AnnouncementCreate(BaseModel):
    """Request to create an announcement."""
    title: str = Field(..., min_length=1, max_length=255)
    content: str = Field(..., min_length=1)
    priority: int = Field(default=0, ge=0)


class AnnouncementUpdate(BaseModel):
    """Request to update an announcement."""
    title: str | None = Field(None, min_length=1, max_length=255)
    content: str | None = Field(None, min_length=1)
    is_active: bool | None = None
    priority: int | None = Field(None, ge=0)


class AnnouncementResponse(BaseResponse):
    """Announcement response."""
    id: str
    creator_openid: str
    title: str
    content: str
    is_active: bool
    priority: int
    created_at: str
    updated_at: str


# =============================================================================
# Level Config Models
# =============================================================================

class LevelConfigCreate(BaseModel):
    """Request to create a level config."""
    level: int = Field(..., ge=1)
    name: str = Field(..., min_length=1, max_length=100)
    name_en: str | None = Field(None, max_length=100)
    name_zh_tw: str | None = Field(None, max_length=100)
    min_score: Decimal = Field(..., ge=0)
    max_score: Decimal | None = Field(None, ge=0)
    icon_url: str | None = Field(None, max_length=512)
    icon_dark_url: str | None = Field(None, max_length=512)
    bg_color: str | None = Field(None, max_length=20)
    bg_gradient_start: str | None = Field(None, max_length=20)
    bg_gradient_end: str | None = Field(None, max_length=20)
    description: str | None = Field(None, max_length=500)
    description_en: str | None = Field(None, max_length=500)
    animation_type: str = Field(default="none")
    sound_url: str | None = Field(None, max_length=512)
    is_active: bool = Field(default=True)
    sort_order: int = Field(default=0, ge=0)


class LevelConfigUpdate(BaseModel):
    """Request to update a level config."""
    name: str | None = Field(None, min_length=1, max_length=100)
    name_en: str | None = Field(None, max_length=100)
    name_zh_tw: str | None = Field(None, max_length=100)
    min_score: Decimal | None = Field(None, ge=0)
    max_score: Decimal | None = Field(None, ge=0)
    icon_url: str | None = Field(None, max_length=512)
    icon_dark_url: str | None = Field(None, max_length=512)
    bg_color: str | None = Field(None, max_length=20)
    bg_gradient_start: str | None = Field(None, max_length=20)
    bg_gradient_end: str | None = Field(None, max_length=20)
    description: str | None = Field(None, max_length=500)
    description_en: str | None = Field(None, max_length=500)
    animation_type: str | None = None
    sound_url: str | None = Field(None, max_length=512)
    is_active: bool | None = None
    sort_order: int | None = Field(None, ge=0)


class LevelConfigResponse(BaseResponse):
    """Level config response."""
    id: int
    level: int
    name: str
    name_en: str | None
    name_zh_tw: str | None
    min_score: Decimal
    max_score: Decimal | None
    icon_url: str | None
    icon_dark_url: str | None
    bg_color: str | None
    bg_gradient_start: str | None
    bg_gradient_end: str | None
    description: str | None
    description_en: str | None
    animation_type: str
    sound_url: str | None
    is_active: bool
    sort_order: int
    created_at: str
    updated_at: str


class ReorderLevelsRequest(BaseModel):
    """Request to reorder levels."""
    level_orders: dict[int, int] = Field(..., description="Map of level -> sort_order")


class ImportLevelsRequest(BaseModel):
    """Request to import level configurations."""
    levels: list[LevelConfigCreate] = Field(..., min_length=1, description="List of level configurations to import")
    replace_existing: bool = Field(default=False, description="Replace all existing levels before import")


# =============================================================================
# UI Config Models
# =============================================================================

class UIConfigResponse(BaseResponse):
    """UI config response."""
    key: str
    value: str
    type: str
    category: str
    label: str
    description: str | None
    min_value: Decimal | None
    max_value: Decimal | None
    allowed_values: Any | None
    updated_at: str
    updated_by: str | None


class UIConfigUpdate(BaseModel):
    """Request to update a UI config."""
    value: str = Field(..., min_length=1)


class BatchUIConfigUpdate(BaseModel):
    """Request to batch update UI configs."""
    configs: dict[str, str] = Field(..., min_length=1)


# =============================================================================
# System Settings Models
# =============================================================================

class SystemSettingsResponse(BaseResponse):
    """System settings response."""
    id: str
    qr_code_expiration_seconds: int
    max_points_per_activity: Decimal
    max_points_per_sub_activity: Decimal
    registration_open: bool
    new_user_initial_points: Decimal
    leaderboard_top_n: int
    leaderboard_refresh_interval_seconds: int
    activities_per_page: int
    scan_rate_limit_per_minute: int
    maintenance_mode: bool
    maintenance_message: str | None
    updated_at: str


class SystemSettingsUpdate(BaseModel):
    """Request to update system settings."""
    qr_code_expiration_seconds: int | None = Field(None, ge=30, le=3600)
    max_points_per_activity: Decimal | None = Field(None, ge=0)
    max_points_per_sub_activity: Decimal | None = Field(None, ge=0)
    registration_open: bool | None = None
    new_user_initial_points: Decimal | None = Field(None, ge=0)
    leaderboard_top_n: int | None = Field(None, ge=1, le=100)
    leaderboard_refresh_interval_seconds: int | None = Field(None, ge=10, le=600)
    activities_per_page: int | None = Field(None, ge=5, le=100)
    scan_rate_limit_per_minute: int | None = Field(None, ge=1, le=60)
    maintenance_mode: bool | None = None
    maintenance_message: str | None = Field(None, max_length=500)


# =============================================================================
# Analytics Models
# =============================================================================

class DashboardStats(BaseModel):
    """Dashboard statistics."""
    total_users: int
    total_activities: int
    active_activities: int
    total_signups: int
    total_completions: int
    avg_completion_rate: float
    total_points_awarded: Decimal


class ActivityStats(BaseModel):
    """Activity completion statistics."""
    activity_id: str
    activity_name: str
    sign_up_count: int
    completed_count: int
    completion_rate: float
    total_points: Decimal


class TrendData(BaseModel):
    """Trend data point."""
    date: str
    new_users: int
    new_signups: int
    new_completions: int
    points_awarded: Decimal


class LeaderboardEntry(BaseModel):
    """Leaderboard entry."""
    rank: int
    user_id: str
    student_id: str
    nickname: str | None
    avatar_url: str | None
    total_points: Decimal
    level: int


class LevelDistribution(BaseModel):
    """Level distribution data."""
    level: int
    level_name: str
    user_count: int
    percentage: float


class AnalyticsQuery(BaseModel):
    """Query parameters for analytics."""
    start_date: str | None = None
    end_date: str | None = None
    limit: int = Field(default=50, ge=1, le=100)


# =============================================================================
# Admin Log Models
# =============================================================================

class AdminLogResponse(BaseResponse):
    """Admin log response."""
    id: int
    admin_openid: str
    action: str
    target_id: str | None
    description: str
    old_value: Any | None
    new_value: Any | None
    ip_address: str | None
    created_at: str


class AdminLogQuery(BaseModel):
    """Query parameters for admin logs."""
    action: str | None = None
    admin_openid: str | None = None
    target_id: str | None = None
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=50, ge=1, le=100)


# =============================================================================
# QR Code Models
# =============================================================================

class QRCodeResponse(BaseModel):
    """QR code response."""
    qr_code_url: str
    activity_id: str
    activity_name: str
    expires_at: str
