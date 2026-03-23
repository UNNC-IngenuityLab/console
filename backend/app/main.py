"""FastAPI application entry point."""

import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1 import api_router
from app.config import settings
from app.core.exceptions import AppException
from app.db import close_pool, get_pool


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    await get_pool()
    yield
    # Shutdown
    await close_pool()


app = FastAPI(
    title="IngenuityLab Console API",
    description="Backend API for IngenuityLab Mini Program Management Console",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS middleware - Allow all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (CORS disabled)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException):
    """Handle application exceptions."""
    return JSONResponse(
        status_code=exc.http_status,
        content={"code": exc.code, "message": exc.message, "data": exc.detail},
    )


@app.exception_handler(status.HTTP_500_INTERNAL_SERVER_ERROR)
async def internal_error_handler(request: Request, exc: Exception):
    """Handle internal server errors."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"code": 500, "message": "Internal server error", "data": str(exc) if settings.debug else None},
    )


# Include API routes
app.include_router(api_router)


# Health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "service": "ingenuitylab-console"}


# Root endpoint
@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "IngenuityLab Console API",
        "version": "0.1.0",
        "docs": "/docs",
        "health": "/health",
    }
