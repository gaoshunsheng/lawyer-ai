# AI服务 - LLM集成完成

## 概述

AI服务已完成LLM集成和RAG实现，支持多种LLM提供商和向量检索功能。

## 模块结构

```
lawyer-ai-ai/
├── app/
│   ├── api/endpoints/
│   │   ├── auth.py          # 认证路由
│   │   ├── chat.py          # 聊天路由（支持RAG）
│   │   ├── rag.py           # RAG检索路由
│   │   ├── calculator.py    # 赔偿计算器
│   │   └── document.py      # 文书生成路由
│   ├── services/
│   │   ├── llm/
│   │   │   ├── __init__.py       # LLM工厂
│   │   │   ├── openai_service.py # OpenAI实现
│   │   │   ├── zhipu_service.py  # 智谱AI实现
│   │   │   ├── mock_service.py   # 模拟服务（开发用）
│   │   │   └── local_embedding.py # 本地向量嵌入
│   │   ├── rag_service.py        # RAG检索增强生成
│   │   ├── vector_store.py       # Milvus向量存储
│   │   ├── chat_service_enhanced.py # 增强版聊天服务
│   │   ├── calculator_service.py # 赔偿计算器服务
│   │   └── auth_service.py       # 认证服务
│   └── core/
│       ├── config.py         # 配置
│       ├── database.py       # 数据库
│       └── milvus.py         # Milvus初始化
```

## LLM提供商支持

### 1. OpenAI
```python
# 配置
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-xxx
OPENAI_API_BASE=https://api.openai.com/v1
OPENAI_MODEL=gpt-4
```

### 2. 智谱AI
```python
# 配置
LLM_PROVIDER=zhipu
ZHIPU_API_KEY=xxx
ZHIPU_MODEL=glm-4
```

### 3. 模拟服务（开发/测试）
```python
# 配置
LLM_PROVIDER=mock
```

## RAG检索增强生成

### 流程
1. 用户提问 → 生成问题向量
2. 向量检索相关文档（法条、案例）
3. 构建上下文 + 系统提示
4. 调用LLM生成回答
5. 返回回答 + 引用来源

### 向量存储
- 使用Milvus存储向量
- 支持三种集合：
  - `law_articles`: 法条向量
  - `precedent_cases`: 案例向量
  - `knowledge_docs`: 通用知识文档

## 赔偿计算器

### 违法解除赔偿
```python
POST /api/v1/calculator/illegal-termination
{
    "entry_date": "2020-06-01",
    "leave_date": "2024-01-15",
    "monthly_salary": 15000,
    "city": "上海"
}
```

### 加班费计算
```python
POST /api/v1/calculator/overtime
{
    "monthly_salary": 15000,
    "workday_hours": 20,
    "weekend_hours": 8,
    "holiday_hours": 4
}
```

### 年休假工资
```python
POST /api/v1/calculator/annual-leave
{
    "monthly_salary": 15000,
    "total_work_years": 5,
    "unused_days": 3
}
```

## API端点

### 智能咨询
- `POST /api/v1/chat/message` - 发送消息（支持RAG）
- `POST /api/v1/chat/sessions` - 创建会话
- `GET /api/v1/chat/sessions` - 获取会话列表
- `GET /api/v1/chat/sessions/{id}/messages` - 获取消息历史
- `DELETE /api/v1/chat/sessions/{id}` - 删除会话

### 知识检索
- `POST /api/v1/rag/search` - 语义搜索
- `POST /api/v1/rag/documents` - 添加文档
- `DELETE /api/v1/rag/documents/{id}` - 删除文档
- `POST /api/v1/rag/init` - 初始化向量库

### 计算器
- `POST /api/v1/calculator/illegal-termination` - 违法解除赔偿
- `POST /api/v1/calculator/overtime` - 加班费
- `POST /api/v1/calculator/annual-leave` - 年休假工资
- `GET /api/v1/calculator/social-average-salary` - 社平工资

## 配置说明

```python
# .env文件

# 应用配置
APP_NAME=律师AI助手
APP_VERSION=1.0.0
DEBUG=True
API_PREFIX=/api/v1

# 数据库
DATABASE_URL=postgresql+asyncpg://postgres:postgres@localhost:5432/lawyer_ai

# Milvus
MILVUS_HOST=localhost
MILVUS_PORT=19530

# LLM配置
LLM_PROVIDER=mock  # openai, zhipu, mock
OPENAI_API_KEY=sk-xxx
OPENAI_MODEL=gpt-4
ZHIPU_API_KEY=xxx
ZHIPU_MODEL=glm-4

# Embedding配置
EMBEDDING_PROVIDER=local  # openai, local
EMBEDDING_MODEL=BAAI/bge-large-zh
EMBEDDING_DIMENSION=1024

# RAG配置
RAG_TOP_K=10
RAG_SIMILARITY_THRESHOLD=0.7
```

## 启动方式

```bash
# 安装依赖
pip install -r requirements.txt

# 开发模式
uvicorn app.main:app --reload --port 8000

# 生产模式
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## 依赖说明

核心依赖：
- FastAPI 0.109.0
- Pydantic 2.5.3
- SQLAlchemy 2.0.25
- pymilvus 2.3.6
- sentence-transformers 2.3.1
- httpx 0.26.0

可选依赖：
- openai: OpenAI SDK
- zhipuai: 智谱AI SDK
