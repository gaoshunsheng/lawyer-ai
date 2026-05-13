# Phase 1 实施计划：核心基础

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 搭建律智通全栈项目骨架，完成认证/多租户/Token监控基础设施，交付智能咨询、赔偿计算器、知识库三个核心功能。

**Architecture:** Next.js 14 (App Router) 前端 + FastAPI 后端，统一Python全栈。Supabase PostgreSQL + pgvector 存储关系数据和向量数据，Upstash Redis 缓存。LangChain 1.0 构建RAG管道，LangGraph 1.0 编排Agent工作流。智谱AI GLM-5.1/GLM-5-Turbo 作为LLM。

**Tech Stack:** Next.js 14, TypeScript, Tailwind CSS, shadcn/ui, FastAPI, Python 3.12, SQLAlchemy 2.x (async), Alembic, pgvector, LangChain 1.0, LangGraph 1.0, 智谱AI GLM-5.1/GLM-5-Turbo/GLM-4-Flash, Supabase, Upstash Redis

---

## File Structure

### Backend (`backend/`)

```
backend/
├── alembic/
│   ├── versions/
│   ├── env.py
│   └── alembic.ini
├── app/
│   ├── __init__.py
│   ├── main.py                        # FastAPI entry, lifespan, routers
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py                  # Pydantic BaseSettings
│   │   ├── database.py                # Async engine + session
│   │   ├── security.py                # JWT create/verify, password hash
│   │   ├── dependencies.py            # get_db, get_current_user, get_tenant
│   │   └── redis.py                   # Upstash Redis client
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py                    # DeclarativeBase, common mixins
│   │   ├── tenant.py                  # Tenant + Department
│   │   ├── user.py                    # User
│   │   ├── chat.py                    # ChatSession, ChatMessage
│   │   ├── knowledge.py               # Law, LawArticle, PrecedentCase, KnowledgeBase
│   │   ├── embedding.py               # LawEmbedding, CaseEmbedding (pgvector)
│   │   ├── token_usage.py             # TokenUsage, TokenUsageDaily
│   │   ├── feedback.py                # ResponseFeedback
│   │   └── model_config.py            # ModelProvider, ModelConfig
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── user.py
│   │   ├── chat.py
│   │   ├── knowledge.py
│   │   ├── calculator.py
│   │   ├── feedback.py
│   │   └── token_usage.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── router.py                  # Aggregated router
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       ├── users.py
│   │       ├── chat.py
│   │       ├── knowledge.py
│   │       ├── calculator.py
│   │       ├── feedback.py
│   │       └── token_usage.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── user_service.py
│   │   ├── chat_service.py
│   │   ├── knowledge_service.py
│   │   ├── calculator_service.py
│   │   └── token_service.py
│   ├── ai/
│   │   ├── __init__.py
│   │   ├── graphs/
│   │   │   ├── __init__.py
│   │   │   └── consult_graph.py       # Consultation LangGraph
│   │   ├── chains/
│   │   │   ├── __init__.py
│   │   │   └── retrieval_chain.py     # RAG retrieval chain
│   │   ├── tools/
│   │   │   ├── __init__.py
│   │   │   ├── search_laws.py
│   │   │   └── search_cases.py
│   │   └── prompts/
│   │       ├── __init__.py
│   │       └── legal_prompts.py
│   └── middleware/
│       ├── __init__.py
│       └── tenant.py                  # Tenant resolution middleware
├── tests/
│   ├── conftest.py
│   ├── test_auth.py
│   ├── test_calculator.py
│   ├── test_chat.py
│   ├── test_knowledge.py
│   └── test_token_usage.py
├── pyproject.toml
├── Dockerfile
├── .env.example
└── .gitignore
```

### Frontend (`frontend/`)

```
frontend/
├── public/
├── src/
│   ├── app/
│   │   ├── layout.tsx                 # Root layout
│   │   ├── page.tsx                   # Redirect to dashboard or login
│   │   ├── globals.css
│   │   ├── (auth)/
│   │   │   ├── layout.tsx
│   │   │   ├── login/page.tsx
│   │   │   └── register/page.tsx
│   │   └── (dashboard)/
│   │       ├── layout.tsx             # Sidebar + header
│   │       ├── dashboard/page.tsx
│   │       ├── chat/
│   │       │   ├── page.tsx
│   │       │   └── [sessionId]/page.tsx
│   │       ├── calculator/page.tsx
│   │       ├── knowledge/
│   │       │   ├── page.tsx
│   │       │   ├── laws/page.tsx
│   │       │   └── cases/page.tsx
│   │       └── settings/page.tsx
│   ├── components/
│   │   ├── ui/                        # shadcn/ui (auto-generated)
│   │   ├── layout/
│   │   │   ├── header.tsx
│   │   │   ├── sidebar.tsx
│   │   │   └── user-menu.tsx
│   │   ├── chat/
│   │   │   ├── chat-interface.tsx
│   │   │   ├── message-list.tsx
│   │   │   ├── message-item.tsx
│   │   │   ├── message-input.tsx
│   │   │   └── feedback-form.tsx
│   │   ├── calculator/
│   │   │   ├── calculator-form.tsx
│   │   │   └── calculation-result.tsx
│   │   └── knowledge/
│   │       ├── law-search.tsx
│   │       ├── law-detail.tsx
│   │       └── case-search.tsx
│   ├── lib/
│   │   ├── api-client.ts             # Typed fetch wrapper
│   │   ├── auth.ts                    # Auth utilities
│   │   ├── utils.ts                   # cn() etc.
│   │   └── constants.ts
│   ├── hooks/
│   │   ├── use-chat.ts
│   │   └── use-debounce.ts
│   ├── types/
│   │   └── index.ts
│   └── providers/
│       └── auth-provider.tsx
├── components.json
├── tailwind.config.ts
├── tsconfig.json
├── next.config.mjs
├── package.json
└── .env.local
```

---

## Sub-Plan P1-A: 项目脚手架 + 数据库Schema

### Task 1: 初始化后端项目

**Files:**
- Create: `backend/pyproject.toml`
- Create: `backend/.env.example`
- Create: `backend/.gitignore`
- Create: `backend/app/__init__.py`
- Create: `backend/app/main.py`
- Create: `backend/app/core/__init__.py`
- Create: `backend/app/core/config.py`
- Create: `backend/app/core/database.py`

- [ ] **Step 1: 创建后端目录并初始化pyproject.toml**

```bash
mkdir -p backend/app/core backend/app/models backend/app/schemas
mkdir -p backend/app/api/v1 backend/app/services backend/app/ai/graphs
mkdir -p backend/app/ai/chains backend/app/ai/tools backend/app/ai/prompts
mkdir -p backend/app/middleware backend/tests
```

`backend/pyproject.toml`:
```toml
[project]
name = "lawyer-ai-backend"
version = "0.1.0"
requires-python = ">=3.12"
dependencies = [
    "fastapi>=0.115.0",
    "uvicorn[standard]>=0.30.0",
    "pydantic>=2.9.0",
    "pydantic-settings>=2.5.0",
    "sqlalchemy[asyncio]>=2.0.35",
    "asyncpg>=0.30.0",
    "alembic>=1.14.0",
    "pgvector>=0.3.6",
    "python-jose[cryptography]>=3.3.0",
    "bcrypt>=4.2.0",
    "httpx>=0.27.0",
    "python-multipart>=0.0.12",
    "redis>=5.2.0",
    "langchain>=0.3.0",
    "langchain-core>=0.3.0",
    "langchain-community>=0.3.0",
    "langchain-openai>=0.2.0",
    "langgraph>=0.2.0",
    "langsmith>=0.1.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.3.0",
    "pytest-asyncio>=0.24.0",
    "httpx>=0.27.0",
    "ruff>=0.6.0",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
testpaths = ["tests"]

[tool.ruff]
line-length = 120
target-version = "py312"
```

- [ ] **Step 2: 创建 .env.example**

`backend/.env.example`:
```bash
# Supabase - 使用直连端口5432（非PgBouncer的6543）
DATABASE_URL=postgresql+asyncpg://postgres.[project-ref]:[password]@aws-0-[region].pooler.supabase.com:5432/postgres
SUPABASE_URL=https://[project-ref].supabase.co
SUPABASE_ANON_KEY=
SUPABASE_SERVICE_ROLE_KEY=
SUPABASE_JWT_SECRET=

# Upstash Redis
UPSTASH_REDIS_REST_URL=
UPSTASH_REDIS_REST_TOKEN=

# 智谱AI
ZHIPU_API_KEY=
ZHIPU_API_BASE=https://open.bigmodel.cn/api/paas/v4

# JWT
JWT_SECRET_KEY=change-this-to-a-secure-random-string
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
REFRESH_TOKEN_EXPIRE_DAYS=7

# App
APP_ENV=development
APP_NAME=律智通
DEBUG=true
```

- [ ] **Step 3: 创建 config.py**

`backend/app/core/config.py`:
```python
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "律智通"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str

    # Supabase
    SUPABASE_URL: str = ""
    SUPABASE_ANON_KEY: str = ""
    SUPABASE_SERVICE_ROLE_KEY: str = ""
    SUPABASE_JWT_SECRET: str = ""

    # Upstash Redis
    UPSTASH_REDIS_REST_URL: str = ""
    UPSTASH_REDIS_REST_TOKEN: str = ""

    # 智谱AI
    ZHIPU_API_KEY: str = ""
    ZHIPU_API_BASE: str = "https://open.bigmodel.cn/api/paas/v4"

    # JWT
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
```

- [ ] **Step 4: 创建 database.py（异步引擎+pgvector注册）**

`backend/app/core/database.py`:
```python
from collections.abc import AsyncGenerator

from pgvector.asyncpg import register_vector
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_size=5,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=300,
)

AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@event.listens_for(engine.sync_engine, "connect")
def _register_vector(dbapi_connection, connection_record):
    dbapi_connection.run_async(register_vector)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
```

- [ ] **Step 5: 创建 main.py**

`backend/app/main.py`:
```python
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(
    title=f"{settings.APP_NAME} API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    return {"status": "ok", "app": settings.APP_NAME}
```

- [ ] **Step 6: 安装依赖并验证启动**

```bash
cd backend
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
# 验证: curl http://localhost:8000/health → {"status":"ok","app":"律智通"}
```

- [ ] **Step 7: 提交**

```bash
cd .. && git add backend/ && git commit -m "feat: init backend project with FastAPI + async SQLAlchemy + pgvector config"
```

---

### Task 2: 数据库模型 + Alembic迁移

**Files:**
- Create: `backend/app/models/base.py`
- Create: `backend/app/models/tenant.py`
- Create: `backend/app/models/user.py`
- Create: `backend/app/models/chat.py`
- Create: `backend/app/models/knowledge.py`
- Create: `backend/app/models/embedding.py`
- Create: `backend/app/models/token_usage.py`
- Create: `backend/app/models/feedback.py`
- Create: `backend/app/models/model_config.py`
- Create: `backend/app/models/__init__.py`
- Create: `backend/alembic/env.py`
- Create: `backend/alembic/alembic.ini`

- [ ] **Step 1: 创建 base model**

`backend/app/models/base.py`:
```python
import uuid
from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class BaseMixin:
    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
```

- [ ] **Step 2: 创建 tenant model（律所+部门）**

`backend/app/models/tenant.py`:
```python
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import BigInteger, DateTime, ForeignKey, Integer, SmallInteger, String, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, BaseMixin


class Tenant(Base, BaseMixin):
    __tablename__ = "tenants"

    name: Mapped[str] = mapped_column(String(200))
    plan: Mapped[str] = mapped_column(String(20), default="free")  # free/pro/team/enterprise
    status: Mapped[str] = mapped_column(String(20), default="active")  # active/suspended/cancelled
    settings: Mapped[dict] = mapped_column(JSONB, default=dict)
    token_budget_monthly: Mapped[int | None] = mapped_column(BigInteger)

    departments: Mapped[list[Department]] = relationship(back_populates="tenant")
    users: Mapped[list["User"]] = relationship(back_populates="tenant")


class Department(Base, BaseMixin):
    __tablename__ = "departments"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), index=True)
    parent_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("departments.id"))
    name: Mapped[str] = mapped_column(String(200))
    path: Mapped[str | None] = mapped_column(String(500))
    level: Mapped[int] = mapped_column(SmallInteger, default=0)
    settings: Mapped[dict] = mapped_column(JSONB, default=dict)
    token_budget_monthly: Mapped[int | None] = mapped_column(BigInteger)

    tenant: Mapped[Tenant] = relationship(back_populates="departments")
    parent: Mapped[Department | None] = relationship(remote_side="Department.id", back_populates="children")
    children: Mapped[list[Department]] = relationship(back_populates="parent")
```

- [ ] **Step 3: 创建 user model**

`backend/app/models/user.py`:
```python
from __future__ import annotations

import uuid

from sqlalchemy import BigInteger, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, BaseMixin


class User(Base, BaseMixin):
    __tablename__ = "users"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), index=True)
    department_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("departments.id"))
    username: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(200))
    real_name: Mapped[str | None] = mapped_column(String(100))
    phone: Mapped[str | None] = mapped_column(String(20))
    avatar_url: Mapped[str | None] = mapped_column(String(500))
    role: Mapped[str] = mapped_column(String(20), default="lawyer")  # platform_admin/tenant_admin/dept_admin/lawyer/assistant
    status: Mapped[str] = mapped_column(String(20), default="active")
    token_budget_monthly: Mapped[int | None] = mapped_column(BigInteger)

    tenant: Mapped["Tenant"] = relationship(back_populates="users")
```

- [ ] **Step 4: 创建 chat model**

`backend/app/models/chat.py`:
```python
from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, BaseMixin


class ChatSession(Base, BaseMixin):
    __tablename__ = "chat_sessions"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    case_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    title: Mapped[str | None] = mapped_column(String(200))
    status: Mapped[str] = mapped_column(String(20), default="active")

    messages: Mapped[list[ChatMessage]] = relationship(back_populates="session", order_by="ChatMessage.created_at")


class ChatMessage(Base, BaseMixin):
    __tablename__ = "chat_messages"

    session_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("chat_sessions.id"), index=True)
    role: Mapped[str] = mapped_column(String(20))  # user/assistant/system
    content: Mapped[str] = mapped_column(Text)
    tokens_used: Mapped[int | None] = mapped_column(Integer)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB)
```

- [ ] **Step 5: 创建 knowledge + embedding models**

`backend/app/models/knowledge.py`:
```python
import uuid

from sqlalchemy import Date, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, BaseMixin


class Law(Base, BaseMixin):
    __tablename__ = "laws"

    tenant_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"))
    title: Mapped[str] = mapped_column(String(500))
    law_type: Mapped[str] = mapped_column(String(50))  # law/regulation/judicial_interpretation/local
    promulgating_body: Mapped[str | None] = mapped_column(String(200))
    promulgation_date: Mapped[object | None] = mapped_column(Date)
    effective_date: Mapped[object | None] = mapped_column(Date)
    status: Mapped[str] = mapped_column(String(20), default="effective")
    full_text: Mapped[str] = mapped_column(Text)
    metadata_: Mapped[dict | None] = mapped_column("metadata", JSONB)


class LawArticle(Base, BaseMixin):
    __tablename__ = "law_articles"

    law_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("laws.id"), index=True)
    article_number: Mapped[str] = mapped_column(String(50))
    content: Mapped[str] = mapped_column(Text)
    chapter: Mapped[str | None] = mapped_column(String(200))


class PrecedentCase(Base, BaseMixin):
    __tablename__ = "precedent_cases"

    tenant_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"))
    case_name: Mapped[str] = mapped_column(String(500))
    case_type: Mapped[str | None] = mapped_column(String(50))
    court: Mapped[str | None] = mapped_column(String(200))
    court_level: Mapped[str | None] = mapped_column(String(50))
    procedure: Mapped[str | None] = mapped_column(String(50))  # first/second/retrial
    judgment_date: Mapped[object | None] = mapped_column(Date)
    region: Mapped[str | None] = mapped_column(String(100))
    result: Mapped[str | None] = mapped_column(String(50))  # win/lose/partial
    summary: Mapped[str | None] = mapped_column(Text)
    full_text: Mapped[str] = mapped_column(Text)
    key_points: Mapped[dict | None] = mapped_column(JSONB)
```

`backend/app/models/embedding.py`:
```python
import uuid

from pgvector.sqlalchemy import Vector
from sqlalchemy import Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, BaseMixin


class LawEmbedding(Base, BaseMixin):
    __tablename__ = "law_embeddings"

    law_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    article_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    article_number: Mapped[str | None] = mapped_column(String(50))
    chunk_text: Mapped[str] = mapped_column(Text)
    chunk_type: Mapped[str] = mapped_column(String(20), default="article")
    embedding = mapped_column(Vector(1536))
    metadata_: Mapped[dict | None] = mapped_column("metadata", "JSONB")

    __table_args__ = (
        Index(
            "ix_law_embeddings_hnsw",
            embedding,
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )


class CaseEmbedding(Base, BaseMixin):
    __tablename__ = "case_embeddings"

    case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    chunk_text: Mapped[str] = mapped_column(Text)
    chunk_type: Mapped[str] = mapped_column(String(20), default="ruling")
    embedding = mapped_column(Vector(1536))
    metadata_: Mapped[dict | None] = mapped_column("metadata", "JSONB")

    __table_args__ = (
        Index(
            "ix_case_embeddings_hnsw",
            embedding,
            postgresql_using="hnsw",
            postgresql_with={"m": 16, "ef_construction": 64},
            postgresql_ops={"embedding": "vector_cosine_ops"},
        ),
    )
```

- [ ] **Step 6: 创建 token_usage + feedback + model_config models**

`backend/app/models/token_usage.py`:
```python
import uuid
from datetime import date

from sqlalchemy import BigInteger, Date, ForeignKey, Integer, Numeric, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, BaseMixin


class TokenUsage(Base, BaseMixin):
    __tablename__ = "token_usages"

    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), index=True)
    department_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("departments.id"))
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    session_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True))
    model_provider: Mapped[str] = mapped_column(String(50))
    model_name: Mapped[str] = mapped_column(String(100))
    agent_type: Mapped[str | None] = mapped_column(String(50))
    input_tokens: Mapped[int] = mapped_column(Integer)
    output_tokens: Mapped[int] = mapped_column(Integer)
    total_tokens: Mapped[int] = mapped_column(Integer)
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    cost_cny: Mapped[float | None] = mapped_column(Numeric(10, 6))


class TokenUsageDaily(Base):
    __tablename__ = "token_usage_daily"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    date: Mapped[date] = mapped_column(Date, primary_key=True)
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), primary_key=True)
    department_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), primary_key=True)
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), primary_key=True)
    model_name: Mapped[str] = mapped_column(String(100), primary_key=True)
    agent_type: Mapped[str | None] = mapped_column(String(50), primary_key=True)
    total_input_tokens: Mapped[int] = mapped_column(BigInteger, default=0)
    total_output_tokens: Mapped[int] = mapped_column(BigInteger, default=0)
    total_tokens: Mapped[int] = mapped_column(BigInteger, default=0)
    total_cost_cny: Mapped[float | None] = mapped_column(Numeric(10, 4), default=0)
    request_count: Mapped[int] = mapped_column(Integer, default=0)
```

`backend/app/models/feedback.py`:
```python
import uuid

from sqlalchemy import Boolean, ForeignKey, SmallInt, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, BaseMixin


class ResponseFeedback(Base, BaseMixin):
    __tablename__ = "response_feedbacks"

    message_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("chat_messages.id"), index=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"))
    tenant_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("tenants.id"), index=True)
    overall_positive: Mapped[bool] = mapped_column(Boolean)
    law_accuracy_score: Mapped[int | None] = mapped_column(SmallInt)
    analysis_depth_score: Mapped[int | None] = mapped_column(SmallInt)
    practical_value_score: Mapped[int | None] = mapped_column(SmallInt)
    text_feedback: Mapped[str | None] = mapped_column(Text)
    ai_analysis: Mapped[str | None] = mapped_column(Text)
```

`backend/app/models/model_config.py`:
```python
import uuid

from sqlalchemy import Boolean, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, BaseMixin


class ModelProvider(Base, BaseMixin):
    __tablename__ = "model_providers"

    name: Mapped[str] = mapped_column(String(100))
    api_base_url: Mapped[str] = mapped_column(String(500))
    api_key_encrypted: Mapped[str] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="active")
    priority: Mapped[int] = mapped_column(Integer, default=0)


class ModelConfig(Base, BaseMixin):
    __tablename__ = "model_configs"

    provider_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True))
    model_name: Mapped[str] = mapped_column(String(100))
    model_type: Mapped[str] = mapped_column(String(50))  # chat/embedding
    capability: Mapped[str | None] = mapped_column(String(50))  # router/consult/document/review/trial
    input_price_per_m: Mapped[float | None] = mapped_column(Numeric(10, 6))
    output_price_per_m: Mapped[float | None] = mapped_column(Numeric(10, 6))
    max_tokens: Mapped[int | None] = mapped_column(Integer)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)
    status: Mapped[str] = mapped_column(String(20), default="active")
```

- [ ] **Step 7: 创建 models/__init__.py**

`backend/app/models/__init__.py`:
```python
from app.models.base import Base
from app.models.tenant import Department, Tenant
from app.models.user import User
from app.models.chat import ChatMessage, ChatSession
from app.models.knowledge import Law, LawArticle, PrecedentCase
from app.models.embedding import CaseEmbedding, LawEmbedding
from app.models.token_usage import TokenUsage, TokenUsageDaily
from app.models.feedback import ResponseFeedback
from app.models.model_config import ModelConfig, ModelProvider

__all__ = [
    "Base",
    "Tenant",
    "Department",
    "User",
    "ChatSession",
    "ChatMessage",
    "Law",
    "LawArticle",
    "PrecedentCase",
    "LawEmbedding",
    "CaseEmbedding",
    "TokenUsage",
    "TokenUsageDaily",
    "ResponseFeedback",
    "ModelProvider",
    "ModelConfig",
]
```

- [ ] **Step 8: 初始化Alembic并生成首次迁移**

```bash
cd backend
alembic init -t async alembic
# 编辑 alembic/env.py: import所有models, 设置target_metadata = Base.metadata
# 编辑 alembic.ini: 设置占位sqlalchemy.url（env.py会从Settings覆盖）
alembic revision --autogenerate -m "init: all tables with pgvector"
# 检查生成的迁移文件是否包含所有表和HNSW索引
```

- [ ] **Step 9: 执行迁移**

```bash
# 确保Supabase数据库已创建，.env中DATABASE_URL已配置
alembic upgrade head
# 在Supabase Dashboard验证表已创建
```

- [ ] **Step 10: 提交**

```bash
cd .. && git add backend/ && git commit -m "feat: add all database models with pgvector, multi-tenant, token tracking"
```

---

### Task 3: 初始化前端项目

**Files:**
- Create: `frontend/package.json` (via create-next-app)
- Create: `frontend/.env.local`
- Create: `frontend/src/lib/api-client.ts`
- Create: `frontend/src/types/index.ts`

- [ ] **Step 1: 创建Next.js项目**

```bash
npx create-next-app@latest frontend --typescript --tailwind --eslint --app --src-dir --import-alias "@/*" --use-pnpm
cd frontend
npx shadcn@latest init
# Style: Default, Base color: Slate, CSS variables: yes
```

- [ ] **Step 2: 安装额外依赖**

```bash
pnpm add zustand js-cookie uuid
pnpm add -D @types/js-cookie @types/uuid
```

- [ ] **Step 3: 创建 .env.local**

`frontend/.env.local`:
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_APP_NAME=律智通
```

- [ ] **Step 4: 创建 api-client.ts**

`frontend/src/lib/api-client.ts`:
```typescript
import { cookies } from "next/headers";

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface RequestOptions extends RequestInit {
  token?: string;
}

async function request<T>(endpoint: string, options: RequestOptions = {}): Promise<T> {
  const { token, headers: customHeaders, ...rest } = options;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    ...(customHeaders as Record<string, string>),
  };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const res = await fetch(`${API_BASE}${endpoint}`, { ...rest, headers });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(error.detail || `API Error: ${res.status}`);
  }

  return res.json();
}

export const api = {
  get: <T>(endpoint: string, token?: string) =>
    request<T>(endpoint, { method: "GET", token }),

  post: <T>(endpoint: string, data: unknown, token?: string) =>
    request<T>(endpoint, { method: "POST", body: JSON.stringify(data), token }),

  put: <T>(endpoint: string, data: unknown, token?: string) =>
    request<T>(endpoint, { method: "PUT", body: JSON.stringify(data), token }),

  delete: <T>(endpoint: string, token?: string) =>
    request<T>(endpoint, { method: "DELETE", token }),
};
```

- [ ] **Step 5: 创建 TypeScript types**

`frontend/src/types/index.ts`:
```typescript
export interface User {
  id: string;
  username: string;
  email: string;
  real_name: string | null;
  role: "platform_admin" | "tenant_admin" | "dept_admin" | "lawyer" | "assistant";
  tenant_id: string;
  department_id: string | null;
  avatar_url: string | null;
  status: string;
}

export interface Tenant {
  id: string;
  name: string;
  plan: "free" | "pro" | "team" | "enterprise";
  status: string;
}

export interface Department {
  id: string;
  tenant_id: string;
  parent_id: string | null;
  name: string;
  path: string | null;
  level: number;
  children?: Department[];
}

export interface ChatSession {
  id: string;
  title: string | null;
  status: string;
  created_at: string;
}

export interface ChatMessage {
  id: string;
  session_id: string;
  role: "user" | "assistant" | "system";
  content: string;
  tokens_used: number | null;
  created_at: string;
}

export interface Law {
  id: string;
  title: string;
  law_type: string;
  promulgating_body: string | null;
  effective_date: string | null;
  status: string;
}

export interface LawArticle {
  id: string;
  law_id: string;
  article_number: string;
  content: string;
}

export interface PrecedentCase {
  id: string;
  case_name: string;
  case_type: string | null;
  court: string | null;
  judgment_date: string | null;
  result: string | null;
  summary: string | null;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  username: string;
  email: string;
  password: string;
  real_name?: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

export interface CalculationRequest {
  calc_type: "illegal_termination" | "overtime" | "annual_leave" | "work_injury";
  params: Record<string, unknown>;
}

export interface CalculationResult {
  result: number;
  breakdown: Record<string, unknown>;
  basis: string[];
  steps: string[];
}

export interface FeedbackRequest {
  message_id: string;
  overall_positive: boolean;
  law_accuracy_score?: number;
  analysis_depth_score?: number;
  practical_value_score?: number;
  text_feedback?: string;
}
```

- [ ] **Step 6: 提交**

```bash
cd .. && git add frontend/ && git commit -m "feat: init Next.js 14 frontend with TypeScript, shadcn/ui, API client, types"
```

---

## Sub-Plan P1-B: 认证 + 四级多租户

### Task 4: JWT认证 + 用户注册/登录

**Files:**
- Create: `backend/app/core/security.py`
- Create: `backend/app/core/dependencies.py`
- Create: `backend/app/schemas/auth.py`
- Create: `backend/app/api/v1/auth.py`
- Create: `backend/app/services/user_service.py`
- Create: `backend/app/api/router.py`
- Create: `backend/tests/test_auth.py`

- [ ] **Step 1: 写认证测试**

`backend/tests/conftest.py`:
```python
import asyncio
from collections.abc import AsyncGenerator

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
```

`backend/tests/test_auth.py`:
```python
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/register",
        json={
            "username": "testlawyer",
            "email": "test@example.com",
            "password": "Test123456!",
            "real_name": "测试律师",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["user"]["username"] == "testlawyer"


@pytest.mark.asyncio
async def test_login(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "testlawyer", "password": "Test123456!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert "refresh_token" in data


@pytest.mark.asyncio
async def test_login_wrong_password(client: AsyncClient):
    response = await client.post(
        "/api/v1/auth/login",
        json={"username": "testlawyer", "password": "wrong"},
    )
    assert response.status_code == 401
```

- [ ] **Step 2: 实现security.py**

`backend/app/core/security.py`:
```python
from datetime import datetime, timedelta, timezone

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(plain.encode(), hashed.encode())


def create_access_token(subject: str, extra: dict | None = None, expires_delta: timedelta | None = None) -> str:
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    payload = {"sub": subject, "exp": expire, "type": "access"}
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def create_refresh_token(subject: str) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    payload = {"sub": subject, "exp": expire, "type": "refresh"}
    return jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
    except JWTError:
        raise ValueError("Invalid token")
```

- [ ] **Step 3: 实现auth schemas、service、路由**

`backend/app/schemas/auth.py`:
```python
import uuid

from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str
    real_name: str | None = None


class LoginRequest(BaseModel):
    username: str
    password: str


class AuthResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: "UserBrief"


class UserBrief(BaseModel):
    id: uuid.UUID
    username: str
    email: str
    real_name: str | None
    role: str
    tenant_id: uuid.UUID
    department_id: uuid.UUID | None

    model_config = {"from_attributes": True}
```

`backend/app/services/user_service.py`:
```python
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password
from app.models import Tenant, User


async def create_user(db: AsyncSession, username: str, email: str, password: str, real_name: str | None = None) -> User:
    result = await db.execute(select(Tenant).where(Tenant.name == "Default"))
    tenant = result.scalar_one_or_none()
    if not tenant:
        tenant = Tenant(name="Default", plan="pro", status="active")
        db.add(tenant)
        await db.flush()

    user = User(
        tenant_id=tenant.id,
        username=username,
        email=email,
        password_hash=hash_password(password),
        real_name=real_name,
        role="tenant_admin",
    )
    db.add(user)
    await db.flush()
    return user


async def authenticate_user(db: AsyncSession, username: str, password: str) -> User | None:
    result = await db.execute(select(User).where(User.username == username))
    user = result.scalar_one_or_none()
    if not user or not verify_password(password, user.password_hash):
        return None
    return user
```

`backend/app/api/v1/auth.py`:
```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, UserBrief
from app.services.user_service import authenticate_user, create_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    user = await create_user(db, req.username, req.email, req.password, req.real_name)
    access = create_access_token(str(user.id), {"tenant_id": str(user.tenant_id), "role": user.role})
    refresh = create_refresh_token(str(user.id))
    return AuthResponse(access_token=access, refresh_token=refresh, user=UserBrief.model_validate(user))


@router.post("/login", response_model=AuthResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    user = await authenticate_user(db, req.username, req.password)
    if not user:
        raise HTTPException(status_code=401, detail="用户名或密码错误")
    access = create_access_token(str(user.id), {"tenant_id": str(user.tenant_id), "role": user.role})
    refresh = create_refresh_token(str(user.id))
    return AuthResponse(access_token=access, refresh_token=refresh, user=UserBrief.model_validate(user))
```

`backend/app/api/router.py`:
```python
from fastapi import APIRouter

from app.api.v1.auth import router as auth_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth_router)
```

- [ ] **Step 4: 在main.py注册路由并运行测试**

在 `main.py` 的 lifespan 之后添加:
```python
from app.api.router import api_router
app.include_router(api_router)
```

```bash
pytest tests/test_auth.py -v
```

- [ ] **Step 5: 提交**

```bash
git add backend/ && git commit -m "feat: add JWT auth with register/login endpoints"
```

---

## Sub-Plan P1-C: Token监控基础设施

### Task 5: Token记录中间件 + 模型配置

**Files:**
- Create: `backend/app/services/token_service.py`
- Create: `backend/app/schemas/token_usage.py`
- Create: `backend/app/api/v1/token_usage.py`

核心逻辑：每次LLM调用后自动记录 token_usages，定时聚合到 token_usage_daily，查询时按层级聚合。

- [ ] **Step 1: 实现 token_service.py** — `record_usage()` 写入明细，`check_budget()` 检查三级预算
- [ ] **Step 2: 实现 token_usage API** — 当前用量、预算进度、按日趋势
- [ ] **Step 3: 添加模型配置 seed** — 插入智谱AI GLM-5.1/GLM-5-Turbo/GLM-4-Flash 的默认配置
- [ ] **Step 4: 提交**

---

## Sub-Plan P1-D: RAG管道

### Task 6: LangChain + pgvector 检索链

**Files:**
- Create: `backend/app/ai/chains/retrieval_chain.py`
- Create: `backend/app/ai/tools/search_laws.py`
- Create: `backend/app/ai/tools/search_cases.py`
- Create: `backend/app/ai/prompts/legal_prompts.py`
- Create: `backend/app/services/knowledge_service.py`

核心逻辑：向量检索（pgvector cosine）+ 全文检索（PostgreSQL tsquery）→ RRF融合 → 按类型/时效加权 → 注入Prompt。

- [ ] **Step 1: 实现 embedding 生成** — 调用智谱 Embedding API，存入 pgvector
- [ ] **Step 2: 实现 hybrid retriever** — 向量 + 全文混合检索
- [ ] **Step 3: 实现 legal_prompts** — 法律咨询系统Prompt模板
- [ ] **Step 4: 实现 knowledge_service** — 法规/案例CRUD + 向量化
- [ ] **Step 5: 实现 knowledge API** — 搜索、详情、批量导入
- [ ] **Step 6: 提交**

---

## Sub-Plan P1-E: Agent系统

### Task 7: LangGraph 咨询Agent

**Files:**
- Create: `backend/app/ai/graphs/consult_graph.py`

核心逻辑：Router→RAG检索→Consult Agent→响应，StateGraph编排，SSE流式输出。

- [ ] **Step 1: 定义 AgentState**
- [ ] **Step 2: 实现 router_node** — 意图分类，使用GLM-4-Flash
- [ ] **Step 3: 实现 rag_retrieve_node** — 调用 retrieval_chain
- [ ] **Step 4: 实现 consult_agent_node** — 调用GLM-5.1，SSE流式
- [ ] **Step 5: 组装 StateGraph** — 条件路由+边
- [ ] **Step 6: 提交**

---

## Sub-Plan P1-F: 智能咨询前后端联调

### Task 8: 咨询API + 前端聊天界面

**Files:**
- Create: `backend/app/api/v1/chat.py`
- Create: `backend/app/services/chat_service.py`
- Create: `backend/app/schemas/chat.py`
- Create: `frontend/src/app/(dashboard)/chat/page.tsx`
- Create: `frontend/src/components/chat/chat-interface.tsx`
- Create: `frontend/src/components/chat/message-list.tsx`
- Create: `frontend/src/components/chat/message-input.tsx`
- Create: `frontend/src/components/chat/feedback-form.tsx`
- Create: `frontend/src/hooks/use-chat.ts`

- [ ] **Step 1: 实现后端chat API** — 创建会话、发送消息（SSE流式）、获取历史
- [ ] **Step 2: 实现前端聊天界面** — 会话列表、消息区、输入框、SSE读取
- [ ] **Step 3: 实现反馈组件** — 👍👎 + 3维度星级 + 文字反馈
- [ ] **Step 4: 端到端联调测试**
- [ ] **Step 5: 提交**

---

## Sub-Plan P1-G: 赔偿计算器

### Task 9: 计算器后端 + 前端

**Files:**
- Create: `backend/app/services/calculator_service.py`
- Create: `backend/app/schemas/calculator.py`
- Create: `backend/app/api/v1/calculator.py`
- Create: `frontend/src/app/(dashboard)/calculator/page.tsx`
- Create: `frontend/src/components/calculator/calculator-form.tsx`
- Create: `frontend/src/components/calculator/calculation-result.tsx`

核心逻辑：纯函数计算，无LLM调用。违法解除(2N)、加班费、年休假、工伤赔偿。含15城市社平工资数据、高薪封顶、步骤展示。

- [ ] **Step 1: 写计算器测试** — 100个真实案例验算，100%准确率
- [ ] **Step 2: 实现 calculator_service.py**
- [ ] **Step 3: 实现 calculator API + schemas**
- [ ] **Step 4: 实现前端计算器表单 + 结果展示**
- [ ] **Step 5: 提交**

---

## Sub-Plan P1-H: 知识库前后端联调

### Task 10: 知识库搜索 + 详情

**Files:**
- Create: `frontend/src/app/(dashboard)/knowledge/page.tsx`
- Create: `frontend/src/app/(dashboard)/knowledge/laws/page.tsx`
- Create: `frontend/src/app/(dashboard)/knowledge/cases/page.tsx`
- Create: `frontend/src/components/knowledge/law-search.tsx`
- Create: `frontend/src/components/knowledge/law-detail.tsx`

- [ ] **Step 1: 实现法规搜索页面** — 关键词+语义搜索，结果列表
- [ ] **Step 2: 实现法规详情页面** — 全文+条款+AI解读
- [ ] **Step 3: 实现案例搜索页面** — 多条件筛选，结果列表
- [ ] **Step 4: 数据初始化脚本** — 批量导入500+法规和1000+案例到pgvector
- [ ] **Step 5: 提交**

---

## Self-Review

**1. Spec coverage:**
- ✅ 技术基建 → Task 1, 3
- ✅ 认证+四级多租户 → Task 2, 4
- ✅ Token监控基础 → Task 5
- ✅ 智能咨询 → Task 6, 7, 8
- ✅ 赔偿计算器 → Task 9
- ✅ 知识库基础 → Task 10

**2. Placeholder scan:** Sub-plans P1-C through P1-H use summary format without full TDD code — these need expansion when executing each sub-plan.

**3. Type consistency:** All models use UUID primary keys, consistent with PostgreSQL UUID type. Pydantic schemas reference same field names as SQLAlchemy models.
