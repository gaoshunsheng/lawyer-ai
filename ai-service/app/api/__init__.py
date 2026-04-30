"""
API路由配置
"""
from fastapi import APIRouter

from app.api.endpoints import auth, chat, rag, document, calculator, knowledge

api_router = APIRouter()

# 认证路由
api_router.include_router(auth.router)

# 聊天路由
api_router.include_router(chat.router, prefix="/chat", tags=["智能咨询"])

# RAG检索路由
api_router.include_router(rag.router, prefix="/rag", tags=["知识检索"])

# 文书生成路由
api_router.include_router(document.router, prefix="/documents", tags=["文书生成"])

# 赔偿计算路由
api_router.include_router(calculator.router, prefix="/calculator", tags=["赔偿计算"])

# 知识导入路由
api_router.include_router(knowledge.router, prefix="/knowledge", tags=["知识导入"])
