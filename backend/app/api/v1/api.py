from fastapi import APIRouter
from app.api.v1.endpoints import profiles, analyze, voice, export

api_router = APIRouter()
api_router.include_router(profiles.router, prefix="/profiles", tags=["profiles"])
api_router.include_router(analyze.router, prefix="/analyze", tags=["analyze"])
api_router.include_router(voice.router, prefix="/voice", tags=["voice"])
api_router.include_router(export.router, prefix="/export", tags=["export"])
