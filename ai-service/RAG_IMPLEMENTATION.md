# AI服务 - RAG检索实现完成

## 概述

AI服务已完成向量数据库的RAG检索实现，支持知识导入、向量化存储和语义检索。

## 架构

```
用户提问 → 向量化 → Milvus检索 → 构建上下文 → LLM生成 → 返回回答
                ↓
          知识库(法规/案例/文档)
```

## 核心服务

### 1. VectorStoreService (向量存储服务)
位置: `app/services/vector_store.py`

功能:
- 连接Milvus向量数据库
- 创建向量集合（法条、案例、文档）
- 向量插入、检索、删除
- 相似度搜索

支持的集合:
- `law_articles` - 法条向量
- `precedent_cases` - 案例向量  
- `knowledge_docs` - 通用文档向量

### 2. RAGService (RAG检索服务)
位置: `app/services/rag_service.py`

功能:
- 语义检索相关文档
- 构建RAG上下文
- 多查询扩展
- 文本分块
- LLM增强生成

### 3. KnowledgeSyncService (知识同步服务)
位置: `app/services/knowledge_sync_service.py`

功能:
- 同步法规到向量库
- 同步案例到向量库
- 同步文档到向量库
- 批量导入
- 删除向量

## API端点

### 知识导入 (`/api/v1/knowledge`)

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | /laws | 导入单条法规 |
| POST | /laws/batch | 批量导入法规 |
| POST | /cases | 导入单个案例 |
| POST | /cases/batch | 批量导入案例 |
| POST | /documents | 导入单个文档 |
| POST | /documents/batch | 批量导入文档 |
| DELETE | /{doc_type}/{doc_id} | 删除知识 |
| DELETE | /clear/{doc_type} | 清空知识库 |
| GET | /stats | 获取统计 |
| POST | /init | 初始化向量库 |

### 知识检索 (`/api/v1/rag`)

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | /search | 语义搜索 |
| POST | /documents | 添加文档 |
| DELETE | /documents/{id} | 删除文档 |
| POST | /init | 初始化向量库 |

### 智能咨询 (`/api/v1/chat`)

| 方法 | 端点 | 说明 |
|------|------|------|
| POST | /message | 发送消息(RAG增强) |
| POST | /sessions | 创建会话 |
| GET | /sessions | 会话列表 |
| GET | /sessions/{id}/messages | 消息历史 |
| DELETE | /sessions/{id} | 删除会话 |

## 使用示例

### 1. 初始化向量数据库

```bash
curl -X POST http://localhost:8000/api/v1/knowledge/init
```

### 2. 导入法规

```bash
curl -X POST http://localhost:8000/api/v1/knowledge/laws \
  -H "Content-Type: application/json" \
  -d '{
    "id": 1,
    "law_name": "中华人民共和国劳动合同法",
    "article_number": "第39条",
    "content": "劳动者有下列情形之一的，用人单位可以解除劳动合同...",
    "metadata": {"effective_date": "2008-01-01"}
  }'
```

### 3. 批量导入法规

```bash
curl -X POST http://localhost:8000/api/v1/knowledge/laws/batch \
  -H "Content-Type: application/json" \
  -d '{
    "laws": [
      {
        "id": 1,
        "law_name": "劳动合同法",
        "article_number": "第39条",
        "content": "劳动者严重违纪..."
      },
      {
        "id": 2,
        "law_name": "劳动合同法",
        "article_number": "第47条",
        "content": "经济补偿按劳动者..."
      }
    ]
  }'
```

### 4. 导入案例

```bash
curl -X POST http://localhost:8000/api/v1/knowledge/cases \
  -H "Content-Type: application/json" \
  -d '{
    "id": 1,
    "case_number": "(2023)沪01民终12345号",
    "case_type": "劳动争议",
    "court": "上海市第一中级人民法院",
    "judgment_date": "2023-08-15",
    "summary": "用人单位以劳动者严重违纪为由解除...",
    "result": "劳动者胜诉",
    "metadata": {"similarity": 0.85}
  }'
```

### 5. 语义检索

```bash
curl -X POST http://localhost:8000/api/v1/rag/search \
  -H "Content-Type: application/json" \
  -d '{
    "query": "违法解除劳动合同怎么赔偿",
    "top_k": 5,
    "doc_type": "law"
  }'
```

### 6. RAG对话

```bash
curl -X POST http://localhost:8000/api/v1/chat/message \
  -H "Content-Type: application/json" \
  -H "X-User-Id: 1" \
  -d '{
    "content": "公司违法解除劳动合同，我应该如何维权？"
  }'
```

## 配置说明

```bash
# .env文件

# Milvus配置
MILVUS_HOST=localhost
MILVUS_PORT=19530

# Embedding配置
EMBEDDING_PROVIDER=local  # openai 或 local
EMBEDDING_MODEL=BAAI/bge-large-zh
EMBEDDING_DIMENSION=1024

# RAG配置
RAG_TOP_K=10
RAG_SIMILARITY_THRESHOLD=0.5
RAG_MAX_CONTEXT_LENGTH=8000

# LLM配置
LLM_PROVIDER=mock  # openai, zhipu, mock
```

## 数据流程

### 法规导入流程

```
法规数据 → 生成向量(Embedding) → 存储到Milvus
         ↓
   文本: "劳动合同法 第39条 ..."
         ↓
   向量: [0.123, -0.456, ...]
```

### 检索流程

```
用户问题 → 向量化 → Milvus检索 → 获取相关文档
         ↓
   "违法解除赔偿" → [0.234, ...] → Top-5相似文档
         ↓
   构建Prompt → LLM生成 → 返回回答
```

## 性能优化

1. **向量维度**: 默认1024维，可根据模型调整
2. **索引类型**: IVF_FLAT，平衡精度和速度
3. **相似度度量**: COSINE余弦相似度
4. **分块策略**: 长文本自动分块(500字/块)
5. **多查询扩展**: 自动扩展相关查询

## 注意事项

1. Milvus需要预先部署
2. 首次使用需调用 `/init` 初始化向量库
3. 建议先导入基础法规和案例数据
4. 批量导入建议控制在100条以内/次
5. 删除操作不可恢复，请谨慎使用

## 测试

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --reload --port 8000

# 测试API
curl http://localhost:8000/health
```
