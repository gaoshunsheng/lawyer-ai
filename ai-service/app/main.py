from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.core.config import settings
from app.api import api_router
from app.core.database import init_db
from app.services.vector_store import VectorStoreService

# 配置日志
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时初始化
    logger.info("正在初始化数据库连接...")
    await init_db()

    logger.info("正在初始化向量数据库...")
    try:
        vector_store = VectorStoreService()
        await vector_store.create_collections()
        logger.info("向量数据库初始化成功")
    except Exception as e:
        logger.warning(f"向量数据库初始化失败（将使用模拟向量）: {e}")

    logger.info(f"应用启动完成 - LLM提供商: {settings.LLM_PROVIDER}")
    yield
    # 关闭时清理
    logger.info("应用正在关闭...")


# 创建应用
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="""
律师AI助手 - AI服务模块

## 功能模块

### 智能咨询
- 基于RAG的法律问答
- 多轮对话支持
- 法律条文和案例引用

### 知识检索
- 语义搜索法律法规
- 案例检索
- 向量检索支持

### 文书生成
- AI辅助文书撰写
- 模板管理
- 智能建议

### 赔偿计算
- 违法解除赔偿计算
- 加班费计算
- 年休假工资计算
    """,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan
)

# CORS配置
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix=settings.API_PREFIX)


@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "version": settings.APP_VERSION,
        "service": "ai-service",
        "llm_provider": settings.LLM_PROVIDER
    }


@app.get("/")
async def root():
    """根路径"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=settings.DEBUG
    )
