"""
知识库同步服务
将数据库中的知识同步到向量数据库
"""
import logging
import asyncio
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.vector_store import VectorStoreService
from app.services.llm import LLMFactory

logger = logging.getLogger(__name__)


class KnowledgeSyncService:
    """知识库同步服务"""

    def __init__(self):
        self.vector_store = VectorStoreService()
        self._embedding_service = None

    def _get_embedding_service(self):
        """获取嵌入服务"""
        if self._embedding_service is None:
            self._embedding_service = LLMFactory.get_embedding_service()
        return self._embedding_service

    async def sync_law(
            self,
            db: AsyncSession,
            law_id: int,
            law_name: str,
            article_number: str,
            content: str,
            metadata: Dict[str, Any] = None
    ) -> bool:
        """
        同步单条法规到向量数据库

        Args:
            db: 数据库会话
            law_id: 法条ID
            law_name: 法律名称
            article_number: 条款号
            content: 条款内容
            metadata: 元数据

        Returns:
            是否成功
        """
        try:
            # 生成嵌入向量
            embedding_service = self._get_embedding_service()
            # 组合文本用于生成向量
            text_for_embedding = f"{law_name} 第{article_number}条 {content}"
            embedding = await embedding_service.embed(text_for_embedding)

            # 插入向量数据库
            vector_id = await self.vector_store.insert_law(
                law_id=law_id,
                law_name=law_name,
                article_number=article_number,
                content=content,
                embedding=embedding,
                metadata=metadata or {}
            )

            logger.info(f"法规同步成功: {law_name} 第{article_number}条, vector_id={vector_id}")
            return True

        except Exception as e:
            logger.error(f"法规同步失败: {e}")
            return False

    async def sync_case(
            self,
            db: AsyncSession,
            case_id: int,
            case_number: str,
            case_type: str,
            court: str,
            judgment_date: str,
            summary: str,
            result: str,
            full_content: str = None,
            metadata: Dict[str, Any] = None
    ) -> bool:
        """
        同步单个案例到向量数据库

        Args:
            db: 数据库会话
            case_id: 案例ID
            case_number: 案号
            case_type: 案件类型
            court: 法院
            judgment_date: 判决日期
            summary: 摘要
            result: 判决结果
            full_content: 完整内容
            metadata: 元数据

        Returns:
            是否成功
        """
        try:
            # 生成嵌入向量
            embedding_service = self._get_embedding_service()
            # 组合文本用于生成向量
            text_for_embedding = f"{case_number} {case_type} {court} {summary}"
            if full_content:
                text_for_embedding += f" {full_content[:1000]}"
            embedding = await embedding_service.embed(text_for_embedding)

            # 插入向量数据库
            vector_id = await self.vector_store.insert_case(
                case_id=case_id,
                case_number=case_number,
                case_type=case_type,
                court=court,
                judgment_date=judgment_date,
                summary=summary,
                result=result,
                embedding=embedding,
                metadata=metadata or {}
            )

            logger.info(f"案例同步成功: {case_number}, vector_id={vector_id}")
            return True

        except Exception as e:
            logger.error(f"案例同步失败: {e}")
            return False

    async def sync_document(
            self,
            db: AsyncSession,
            doc_id: int,
            doc_type: str,
            title: str,
            content: str,
            source: str = "",
            metadata: Dict[str, Any] = None
    ) -> bool:
        """
        同步文档到向量数据库

        Args:
            db: 数据库会话
            doc_id: 文档ID
            doc_type: 文档类型
            title: 标题
            content: 内容
            source: 来源
            metadata: 元数据

        Returns:
            是否成功
        """
        try:
            # 生成嵌入向量
            embedding_service = self._get_embedding_service()
            # 组合文本用于生成向量
            text_for_embedding = f"{title} {content}"
            embedding = await embedding_service.embed(text_for_embedding)

            # 插入向量数据库
            vector_id = await self.vector_store.insert_document(
                doc_id=doc_id,
                doc_type=doc_type,
                title=title,
                content=content,
                source=source,
                embedding=embedding,
                metadata=metadata or {}
            )

            logger.info(f"文档同步成功: {title[:50]}, vector_id={vector_id}")
            return True

        except Exception as e:
            logger.error(f"文档同步失败: {e}")
            return False

    async def batch_sync_laws(
            self,
            db: AsyncSession,
            laws: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        批量同步法规

        Args:
            db: 数据库会话
            laws: 法规列表

        Returns:
            同步结果统计
        """
        success_count = 0
        fail_count = 0
        errors = []

        for law in laws:
            success = await self.sync_law(
                db=db,
                law_id=law["id"],
                law_name=law["law_name"],
                article_number=law["article_number"],
                content=law["content"],
                metadata=law.get("metadata")
            )
            if success:
                success_count += 1
            else:
                fail_count += 1
                errors.append(f"法规ID {law['id']} 同步失败")

        return {
            "total": len(laws),
            "success": success_count,
            "fail": fail_count,
            "errors": errors[:10]  # 只返回前10个错误
        }

    async def batch_sync_cases(
            self,
            db: AsyncSession,
            cases: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        批量同步案例

        Args:
            db: 数据库会话
            cases: 案例列表

        Returns:
            同步结果统计
        """
        success_count = 0
        fail_count = 0
        errors = []

        for case in cases:
            success = await self.sync_case(
                db=db,
                case_id=case["id"],
                case_number=case["case_number"],
                case_type=case["case_type"],
                court=case["court"],
                judgment_date=case["judgment_date"],
                summary=case["summary"],
                result=case["result"],
                full_content=case.get("full_content"),
                metadata=case.get("metadata")
            )
            if success:
                success_count += 1
            else:
                fail_count += 1
                errors.append(f"案例ID {case['id']} 同步失败")

        return {
            "total": len(cases),
            "success": success_count,
            "fail": fail_count,
            "errors": errors[:10]
        }

    async def batch_sync_documents(
            self,
            db: AsyncSession,
            documents: List[Dict[str, Any]],
            doc_type: str = "document"
    ) -> Dict[str, Any]:
        """
        批量同步文档

        Args:
            db: 数据库会话
            documents: 文档列表
            doc_type: 文档类型

        Returns:
            同步结果统计
        """
        success_count = 0
        fail_count = 0
        errors = []

        for doc in documents:
            success = await self.sync_document(
                db=db,
                doc_id=doc["id"],
                doc_type=doc.get("doc_type", doc_type),
                title=doc["title"],
                content=doc["content"],
                source=doc.get("source", ""),
                metadata=doc.get("metadata")
            )
            if success:
                success_count += 1
            else:
                fail_count += 1
                errors.append(f"文档ID {doc['id']} 同步失败")

        return {
            "total": len(documents),
            "success": success_count,
            "fail": fail_count,
            "errors": errors[:10]
        }

    async def delete_from_vector_db(self, source_id: int, doc_type: str) -> bool:
        """
        从向量数据库删除

        Args:
            source_id: 源数据ID
            doc_type: 文档类型

        Returns:
            是否成功
        """
        return await self.vector_store.delete_by_source_id(source_id, doc_type)

    async def get_sync_stats(self) -> Dict[str, Any]:
        """获取向量数据库统计"""
        return await self.vector_store.get_collection_stats()

    async def clear_all(self, doc_type: str) -> bool:
        """
        清空指定类型的向量数据

        Args:
            doc_type: 文档类型

        Returns:
            是否成功
        """
        return await self.vector_store.clear_collection(doc_type)