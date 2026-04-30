"""
RAG检索路由
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from typing import Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from app.core.database import get_session
from app.schemas.common import ResponseModel
from app.services.rag_service import RAGService
from app.services.vector_store import VectorStoreService

router = APIRouter()

# 全局服务实例
_rag_service = None
_vector_store = None


def get_rag_service() -> RAGService:
    """获取RAG服务实例"""
    global _rag_service
    if _rag_service is None:
        _rag_service = RAGService()
    return _rag_service


def get_user_id(x_user_id: Optional[str] = Header(None)) -> int:
    """从请求头获取用户ID"""
    if x_user_id:
        return int(x_user_id)
    return 1


def get_tenant_id(x_tenant_id: Optional[str] = Header(None)) -> Optional[int]:
    """从请求头获取租户ID"""
    if x_tenant_id:
        return int(x_tenant_id)
    return None


class SearchRequest(BaseModel):
    """搜索请求"""
    query: str = Field(..., description="搜索查询", min_length=1, max_length=500)
    doc_type: Optional[str] = Field(None, description="文档类型: law, case, document")
    top_k: int = Field(10, description="返回数量", ge=1, le=50)


class AddDocumentRequest(BaseModel):
    """添加文档请求"""
    content: str = Field(..., description="文档内容", min_length=1)
    doc_type: str = Field(..., description="文档类型: law, case, document")
    source_name: str = Field(..., description="来源名称", max_length=200)
    metadata: Optional[dict] = Field(None, description="元数据")


@router.post("/search", response_model=ResponseModel)
async def search_knowledge(
        request: SearchRequest,
        rag_service: RAGService = Depends(get_rag_service),
        tenant_id: Optional[int] = Depends(get_tenant_id)
):
    """
    知识检索

    根据查询文本检索相关的法律条文、案例等知识
    """
    try:
        results = await rag_service.search(
            query=request.query,
            top_k=request.top_k,
            doc_type=request.doc_type
        )

        return ResponseModel(data={
            "query": request.query,
            "results": [
                {
                    "id": r.id,
                    "content": r.content,
                    "score": r.score,
                    "source_type": r.source_type,
                    "source_name": r.source_name,
                    "metadata": r.metadata
                }
                for r in results
            ],
            "total": len(results)
        })
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"检索失败: {str(e)}"
        )


@router.post("/documents", response_model=ResponseModel)
async def add_document(
        request: AddDocumentRequest,
        rag_service: RAGService = Depends(get_rag_service),
        user_id: int = Depends(get_user_id),
        tenant_id: Optional[int] = Depends(get_tenant_id)
):
    """
    添加文档到知识库

    将文档向量化后存储到向量数据库
    """
    try:
        # 添加元数据
        metadata = request.metadata or {}
        if tenant_id:
            metadata["tenant_id"] = tenant_id
        metadata["created_by"] = user_id

        doc_id = await rag_service.add_document(
            content=request.content,
            doc_type=request.doc_type,
            source_name=request.source_name,
            metadata=metadata
        )

        return ResponseModel(data={
            "id": doc_id,
            "message": "文档添加成功"
        })
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"添加文档失败: {str(e)}"
        )


@router.get("/documents/{doc_id}", response_model=ResponseModel)
async def get_document(
        doc_id: int,
        doc_type: Optional[str] = None
):
    """获取文档详情"""
    # TODO: 从数据库或向量存储获取文档详情
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="功能开发中"
    )


@router.delete("/documents/{doc_id}", response_model=ResponseModel)
async def delete_document(
        doc_id: int,
        doc_type: Optional[str] = None,
        rag_service: RAGService = Depends(get_rag_service)
):
    """删除文档"""
    try:
        success = await rag_service.delete_document(doc_id, doc_type)
        if success:
            return ResponseModel(message="文档删除成功")
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="文档不存在"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除文档失败: {str(e)}"
        )


@router.post("/init", response_model=ResponseModel)
async def init_vector_store():
    """初始化向量数据库集合"""
    try:
        vector_store = VectorStoreService()
        await vector_store.create_collections()
        return ResponseModel(message="向量数据库初始化成功")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"初始化失败: {str(e)}"
        )
