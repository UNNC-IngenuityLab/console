"""Authentication API endpoints."""

from typing import Annotated

from fastapi import APIRouter, Depends, status

from app.core.exceptions import UnauthorizedException, ValidationException
from app.core.security import verify_password
from app.db.repositories import UserRepository
from app.dependencies import get_admin_user, get_db_connection, get_user_repo
from app.models import ApiResponse, LoginRequest, LoginResponse, UserSummary

router = APIRouter()


@router.post("/login", response_model=ApiResponse)
async def login(
    data: LoginRequest,
    conn: Annotated[object, Depends(get_db_connection)],
) -> ApiResponse:
    """Admin login endpoint.

    Validates credentials and returns a JWT access token.
    """
    repo = UserRepository(conn)
    user = await repo.find_by_student_id(data.student_id)

    if user is None:
        raise UnauthorizedException("Invalid student ID or password")

    if not user.get("is_active"):
        raise UnauthorizedException("Account is disabled")

    # Verify password (assuming password is stored as bcrypt hash)
    if not verify_password(data.password, user.get("password", "")):
        raise UnauthorizedException("Invalid student ID or password")

    # Create JWT token
    from app.core.security import create_access_token

    access_token = create_access_token(data={"sub": user["id"], "student_id": user["student_id"]})

    return ApiResponse(
        data=LoginResponse(
            access_token=access_token,
            user=UserSummary(
                id=user["id"],
                student_id=user["student_id"],
                nickname=user.get("nickname"),
                avatar_url=user.get("avatar_url"),
                total_points=user.get("total_points", 0),
                level=user.get("level", 1),
                is_active=user.get("is_active", True),
            ),
        ).model_dump(),
    )


@router.post("/logout", response_model=ApiResponse)
async def logout(
    current_user: Annotated[dict, Depends(get_admin_user)],
) -> ApiResponse:
    """Logout endpoint.

    JWT tokens are stateless, so logout is handled on the client side
    by discarding the token.
    """
    return ApiResponse(message="Logged out successfully")


@router.get("/me", response_model=ApiResponse)
async def get_current_user_info(
    current_user: Annotated[dict, Depends(get_admin_user)],
) -> ApiResponse:
    """Get current user information."""
    return ApiResponse(
        data=UserSummary(
            id=current_user["id"],
            student_id=current_user["student_id"],
            nickname=current_user.get("nickname"),
            avatar_url=current_user.get("avatar_url"),
            total_points=current_user.get("total_points", 0),
            level=current_user.get("level", 1),
            is_active=current_user.get("is_active", True),
        ).model_dump(),
    )
