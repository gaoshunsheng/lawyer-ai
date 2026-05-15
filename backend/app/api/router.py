from fastapi import APIRouter

from app.api.v1.auth import router as auth_router
from app.api.v1.calculator import router as calculator_router
from app.api.v1.chat import router as chat_router
from app.api.v1.feedback import router as feedback_router
from app.api.v1.knowledge import router as knowledge_router
from app.api.v1.models import router as models_router
from app.api.v1.cases import router as cases_router
from app.api.v1.documents import doc_router, template_router
from app.api.v1.contracts import router as contracts_router
from app.api.v1.token_usage import router as token_usage_router
from app.api.v1.favorites import router as favorites_router
from app.api.v1.trial import router as trial_router
from app.api.v1.gantt import router as gantt_router
from app.api.v1.reports import router as reports_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
api_router.include_router(calculator_router)
api_router.include_router(cases_router)
api_router.include_router(chat_router)
api_router.include_router(contracts_router)
api_router.include_router(doc_router)
api_router.include_router(template_router)
api_router.include_router(feedback_router)
api_router.include_router(knowledge_router)
api_router.include_router(token_usage_router)
api_router.include_router(models_router)
api_router.include_router(favorites_router)
api_router.include_router(trial_router)
api_router.include_router(gantt_router)
api_router.include_router(reports_router)
