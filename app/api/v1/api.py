from fastapi import APIRouter
from app.api.v1.endpoints import clubs

api_router = APIRouter()

api_router.include_router(clubs.router, prefix="/clubs", tags=["clubs"])
