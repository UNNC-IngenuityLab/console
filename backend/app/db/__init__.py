"""Database layer for the application."""

from aiomysql import Pool, create_pool
from pymysql.constants import CLIENT

from app.config import settings

_pool: Pool | None = None


async def get_pool() -> Pool:
    """Get or create the database connection pool."""
    global _pool
    if _pool is None:
        _pool = await create_pool(
            host=settings.db_host,
            port=settings.db_port,
            user=settings.db_user,
            password=settings.db_password,
            db=settings.db_name,
            charset="utf8mb4",
            autocommit=True,
            maxsize=20,
            minsize=5,
            client_flag=CLIENT.FOUND_ROWS,
        )
    return _pool


async def close_pool() -> None:
    """Close the database connection pool."""
    global _pool
    if _pool is not None:
        _pool.close()
        await _pool.wait_closed()
        _pool = None


async def get_connection():
    """Get a database connection from the pool."""
    pool = await get_pool()
    async with pool.acquire() as conn:
        yield conn
