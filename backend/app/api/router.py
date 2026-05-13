from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.calculator import router as calculator_router
from app.api.v1.knowledge import router as knowledge_router
from app.api.v1.models import router as models_router
from app.api.v1.token_usage import router as token_usage_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(calculator_router)
api_router.include_router(knowledge_router)
api_router.include_router(token_usage_router)
api_router.include_router(models_router)
