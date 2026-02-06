"""API router aggregation for version 1."""
from fastapi import APIRouter

from .endpoints import lessons, auth

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(lessons.router, prefix="/lessons", tags=["lessons"])
