"""
知识导入路由
支持批量导入法规、案例和文档到向量数据库
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header, BackgroundTasks
from typing import Optional, List
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_session
from app.schemas.common import ResponseModel
from app.services.knowledge_sync_service import KnowledgeSyncService
from app.services.vector_store import VectorStoreService
from app.services.rag_service import RAGService

router = APIRouter()

# 全局服务实例
_sync_service = None
_rag_service = None


def get_sync_service() -> KnowledgeSyncService:
    """获取同步服务实例"""
    global _sync_service
    if _sync_service is None:
        _sync_service = KnowledgeSyncService()
    return _sync_service


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


# ==================== 请求模型 ====================

class LawItem(BaseModel):
    """法条条目"""
    id: int = Field(..., description="法条ID")
    law_name: str = Field(..., description="法律名称", max_length=200)
    article_number: str = Field(..., description="条款号", max_length=50)
    content: str = Field(..., description="条款内容")
    metadata: Optional[dict] = Field(None, description="元数据")


class CaseItem(BaseModel):
    """案例条目"""
    id: int = Field(..., description="案例ID")
    case_number: str = Field(..., description="案号", max_length=100)
    case_type: str = Field(..., description="案件类型", max_length=50)
    court: str = Field(..., description="法院", max_length=100)
    judgment_date: str = Field(..., description="判决日期", max_length=20)
    summary: str = Field(..., description="案例摘要")
    result: str = Field(..., description="判决结果", max_length=100)
    full_content: Optional[str] = Field(None, description="完整内容")
    metadata: Optional[dict] = Field(None, description="元数据")


class DocumentItem(BaseModel):
    """文档条目"""
    id: int = Field(..., description="文档ID")
    title: str = Field(..., description="标题", max_length=500)
    content: str = Field(..., description="内容")
    doc_type: str = Field(default="document", description="文档类型")
    source: Optional[str] = Field(None, description="来源", max_length=200)
    metadata: Optional[dict] = Field(None, description="元数据")


class BatchLawsRequest(BaseModel):
    """批量导入法规请求"""
    laws: List[LawItem] = Field(..., description="法条列表")


class BatchCasesRequest(BaseModel):
    """批量导入案例请求"""
    cases: List[CaseItem] = Field(..., description="案例列表")


class BatchDocumentsRequest(BaseModel):
    """批量导入文档请求"""
    documents: List[DocumentItem] = Field(..., description="文档列表")


# ==================== 法规导入 ====================

@router.post("/laws", response_model=ResponseModel)
async def import_law(
        law: LawItem,
        db: AsyncSession = Depends(get_session),
        sync_service: KnowledgeSyncService = Depends(get_sync_service),
        user_id: int = Depends(get_user_id)
):
    """
    导入单条法规到向量数据库

    将法规内容向量化后存储到Milvus，用于后续的语义检索
    """
    try:
        success = await sync_service.sync_law(
            db=db,
            law_id=law.id,
            law_name=law.law_name,
            article_number=law.article_number,
            content=law.content,
            metadata=law.metadata
        )

        if success:
            return ResponseModel(data={
                "id": law.id,
                "message": "法规导入成功"
            })
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="法规导入失败"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导入失败: {str(e)}"
        )


@router.post("/laws/batch", response_model=ResponseModel)
async def batch_import_laws(
        request: BatchLawsRequest,
        background_tasks: BackgroundTasks,
        db: AsyncSession = Depends(get_session),
        sync_service: KnowledgeSyncService = Depends(get_sync_service),
        user_id: int = Depends(get_user_id)
):
    """
    批量导入法规

    将多条法规批量导入向量数据库
    """
    try:
        laws_data = [law.model_dump() for law in request.laws]
        result = await sync_service.batch_sync_laws(db, laws_data)

        return ResponseModel(data=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量导入失败: {str(e)}"
        )


# ==================== 案例导入 ====================

@router.post("/cases", response_model=ResponseModel)
async def import_case(
        case: CaseItem,
        db: AsyncSession = Depends(get_session),
        sync_service: KnowledgeSyncService = Depends(get_sync_service),
        user_id: int = Depends(get_user_id)
):
    """
    导入单个案例到向量数据库

    将案例摘要向量化后存储到Milvus
    """
    try:
        success = await sync_service.sync_case(
            db=db,
            case_id=case.id,
            case_number=case.case_number,
            case_type=case.case_type,
            court=case.court,
            judgment_date=case.judgment_date,
            summary=case.summary,
            result=case.result,
            full_content=case.full_content,
            metadata=case.metadata
        )

        if success:
            return ResponseModel(data={
                "id": case.id,
                "message": "案例导入成功"
            })
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="案例导入失败"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导入失败: {str(e)}"
        )


@router.post("/cases/batch", response_model=ResponseModel)
async def batch_import_cases(
        request: BatchCasesRequest,
        db: AsyncSession = Depends(get_session),
        sync_service: KnowledgeSyncService = Depends(get_sync_service),
        user_id: int = Depends(get_user_id)
):
    """
    批量导入案例

    将多个案例批量导入向量数据库
    """
    try:
        cases_data = [case.model_dump() for case in request.cases]
        result = await sync_service.batch_sync_cases(db, cases_data)

        return ResponseModel(data=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量导入失败: {str(e)}"
        )


# ==================== 文档导入 ====================

@router.post("/documents", response_model=ResponseModel)
async def import_document(
        doc: DocumentItem,
        db: AsyncSession = Depends(get_session),
        rag_service: RAGService = Depends(get_rag_service),
        user_id: int = Depends(get_user_id),
        tenant_id: Optional[int] = Depends(get_tenant_id)
):
    """
    导入单个文档到向量数据库

    支持长文本自动分块，将文档向量化后存储
    """
    try:
        # 添加租户信息
        metadata = doc.metadata or {}
        if tenant_id:
            metadata["tenant_id"] = tenant_id
        metadata["created_by"] = user_id

        doc_id = await rag_service.add_document(
            content=doc.content,
            doc_type=doc.doc_type,
            source_name=doc.title,
            doc_id=doc.id,
            metadata=metadata
        )

        return ResponseModel(data={
            "id": doc.id,
            "vector_id": doc_id,
            "message": "文档导入成功"
        })
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"导入失败: {str(e)}"
        )


@router.post("/documents/batch", response_model=ResponseModel)
async def batch_import_documents(
        request: BatchDocumentsRequest,
        db: AsyncSession = Depends(get_session),
        sync_service: KnowledgeSyncService = Depends(get_sync_service),
        user_id: int = Depends(get_user_id),
        tenant_id: Optional[int] = Depends(get_tenant_id)
):
    """
    批量导入文档

    将多个文档批量导入向量数据库
    """
    try:
        docs_data = []
        for doc in request.documents:
            metadata = doc.metadata or {}
            if tenant_id:
                metadata["tenant_id"] = tenant_id
            metadata["created_by"] = user_id
            docs_data.append({
                **doc.model_dump(),
                "metadata": metadata
            })

        result = await sync_service.batch_sync_documents(db, docs_data)

        return ResponseModel(data=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"批量导入失败: {str(e)}"
        )


# ==================== 管理接口 ====================

@router.delete("/{doc_type}/{doc_id}", response_model=ResponseModel)
async def delete_knowledge(
        doc_type: str,
        doc_id: int,
        sync_service: KnowledgeSyncService = Depends(get_sync_service),
        user_id: int = Depends(get_user_id)
):
    """
    从向量数据库删除知识

    根据文档类型和ID删除对应的向量数据
    """
    if doc_type not in ["law", "case", "document"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="doc_type must be one of: law, case, document"
        )

    try:
        success = await sync_service.delete_from_vector_db(doc_id, doc_type)
        if success:
            return ResponseModel(message="删除成功")
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="删除失败"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除失败: {str(e)}"
        )


@router.delete("/clear/{doc_type}", response_model=ResponseModel)
async def clear_knowledge(
        doc_type: str,
        sync_service: KnowledgeSyncService = Depends(get_sync_service),
        user_id: int = Depends(get_user_id)
):
    """
    清空指定类型的知识库

    危险操作：将删除该类型的所有向量数据
    """
    if doc_type not in ["law", "case", "document"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="doc_type must be one of: law, case, document"
        )

    try:
        success = await sync_service.clear_all(doc_type)
        if success:
            return ResponseModel(message=f"已清空 {doc_type} 类型知识库")
        else:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="清空失败"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"清空失败: {str(e)}"
        )


@router.get("/stats", response_model=ResponseModel)
async def get_knowledge_stats(
        sync_service: KnowledgeSyncService = Depends(get_sync_service)
):
    """
    获取知识库统计信息

    返回各类型知识库的向量数量
    """
    try:
        stats = await sync_service.get_sync_stats()
        return ResponseModel(data=stats)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取统计失败: {str(e)}"
        )


@router.post("/init", response_model=ResponseModel)
async def init_vector_database():
    """
    初始化向量数据库

    创建所有必要的集合（如果不存在）
    """
    try:
        vector_store = VectorStoreService()
        await vector_store.create_collections()
        return ResponseModel(message="向量数据库初始化成功")
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"初始化失败: {str(e)}"
        )
