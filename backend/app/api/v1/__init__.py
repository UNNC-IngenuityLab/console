# API v1 routes package

from fastapi import APIRouter

from app.api.v1 import (
    admin_logs,
    analytics,
    announcements,
    auth,
    config,
    activities,
    levels,
    settings,
    users,
)

api_router = APIRouter(prefix="/api/v1")

# Include all route modules
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(activities.router, prefix="/activities", tags=["Activities"])
api_router.include_router(announcements.router, prefix="/announcements", tags=["Announcements"])
api_router.include_router(levels.router, prefix="/levels", tags=["Level Configs"])
api_router.include_router(config.router, prefix="/config", tags=["UI Config"])
api_router.include_router(settings.router, prefix="/settings", tags=["System Settings"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics"])
api_router.include_router(admin_logs.router, prefix="/admin-logs", tags=["Admin Logs"])
