# 律师AI助手 - AI服务

FastAPI + Python 实现的AI服务模块

## 功能模块

- RAG检索服务
- 对话服务
- 文书生成服务
- 案件分析服务

## 技术栈

- Python 3.11+
- FastAPI
- LangChain
- Milvus
- PostgreSQL

## 启动方式

```bash
# 安装依赖
pip install -r requirements.txt

# 启动服务
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```
