"""
RAG检索增强生成服务 - 完善版
支持知识库同步和高效检索
"""
import logging
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import asyncio

from app.core.config import settings
from app.services.llm import LLMFactory, BaseLLMService, ChatMessage, LLMResponse
from app.services.vector_store import VectorStoreService

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """检索结果"""
    id: int
    source_id: int
    content: str
    score: float
    source_type: str
    source_name: str
    metadata: Dict[str, Any]
    extra: Dict[str, Any] = None


@dataclass
class RAGContext:
    """RAG上下文"""
    query: str
    search_results: List[SearchResult]
    context_text: str
    total_tokens: int


class RAGService:
    """RAG检索增强生成服务"""

    # 法律咨询系统提示
    LEGAL_SYSTEM_PROMPT = """你是一位专业的劳动法律师助手，具有丰富的劳动法律知识和实践经验。
你的职责是为用户提供专业、准确、实用的法律建议。

回答问题时请遵循以下原则：
1. 准确引用法律条文，注明法律名称和具体条款号
2. 提供清晰的逻辑分析和法律适用
3. 结合案件事实给出具体建议
4. 如有相关案例，可以适当引用参考
5. 对可能的法律风险进行提示
6. 语言专业但不晦涩，便于用户理解

当前日期：2024年

请基于以下参考信息回答用户问题：

{context}

如果参考信息与用户问题不相关，请根据你的专业知识回答。如果问题超出你的专业范围，请如实告知用户。"""

    # 分块大小
    CHUNK_SIZE = 500
    CHUNK_OVERLAP = 50

    def __init__(self):
        self.llm_service: BaseLLMService = None
        self.embedding_service: BaseLLMService = None
        self.vector_store: VectorStoreService = None

    def _get_llm_service(self) -> BaseLLMService:
        """获取LLM服务"""
        if self.llm_service is None:
            self.llm_service = LLMFactory.get_llm_service()
        return self.llm_service

    def _get_embedding_service(self) -> BaseLLMService:
        """获取嵌入服务"""
        if self.embedding_service is None:
            self.embedding_service = LLMFactory.get_embedding_service()
        return self.embedding_service

    def _get_vector_store(self) -> VectorStoreService:
        """获取向量存储服务"""
        if self.vector_store is None:
            self.vector_store = VectorStoreService()
        return self.vector_store

    async def search(
            self,
            query: str,
            top_k: int = None,
            doc_type: str = None,
            min_score: float = None,
            filters: Dict[str, Any] = None
    ) -> List[SearchResult]:
        """
        检索相关文档

        Args:
            query: 查询文本
            top_k: 返回数量
            doc_type: 文档类型过滤 (law, case, document)
            min_score: 最小相似度
            filters: 额外过滤条件

        Returns:
            检索结果列表
        """
        if top_k is None:
            top_k = settings.RAG_TOP_K
        if min_score is None:
            min_score = settings.RAG_SIMILARITY_THRESHOLD

        try:
            # 生成查询向量
            embedding_service = self._get_embedding_service()
            query_embedding = await embedding_service.embed(query)

            # 向量检索
            vector_store = self._get_vector_store()
            results = await vector_store.search(
                query_embedding=query_embedding,
                top_k=top_k,
                doc_type=doc_type,
                min_score=min_score,
                filters=filters
            )

            # 转换为SearchResult
            search_results = []
            for result in results:
                search_results.append(SearchResult(
                    id=result.get("id", 0),
                    source_id=result.get("source_id", 0),
                    content=result.get("content", ""),
                    score=result.get("score", 0.0),
                    source_type=result.get("source_type", "unknown"),
                    source_name=result.get("source_name", ""),
                    metadata=result.get("metadata", {}),
                    extra=result.get("extra", {})
                ))

            logger.info(f"检索完成: query={query[:50]}..., results={len(search_results)}")
            return search_results

        except Exception as e:
            logger.error(f"检索失败: {e}")
            return []

    async def search_with_rerank(
            self,
            query: str,
            top_k: int = 10,
            doc_type: str = None,
            min_score: float = 0.5,
            rerank: bool = True
    ) -> List[SearchResult]:
        """
        检索并重排序

        Args:
            query: 查询文本
            top_k: 返回数量
            doc_type: 文档类型
            min_score: 最小相似度
            rerank: 是否重排序

        Returns:
            检索结果列表
        """
        # 先检索更多结果
        results = await self.search(
            query=query,
            top_k=top_k * 2 if rerank else top_k,
            doc_type=doc_type,
            min_score=min_score
        )

        if not rerank or not results:
            return results[:top_k]

        # 简单重排序：优先法条，然后案例
        def sort_key(r):
            type_priority = {"law": 0, "case": 1, "document": 2}
            return (type_priority.get(r.source_type, 3), -r.score)

        results.sort(key=sort_key)
        return results[:top_k]

    async def build_context(
            self,
            query: str,
            search_results: List[SearchResult],
            max_length: int = None
    ) -> RAGContext:
        """
        构建RAG上下文

        Args:
            query: 用户问题
            search_results: 检索结果
            max_length: 最大上下文长度

        Returns:
            RAG上下文
        """
        if max_length is None:
            max_length = settings.RAG_MAX_CONTEXT_LENGTH

        context_parts = []
        total_length = 0

        for i, result in enumerate(search_results, 1):
            source_type_name = {
                "law": "【法律法规】",
                "case": "【参考案例】",
                "document": "【相关文档】"
            }.get(result.source_type, "【参考资料】")

            context_part = f"""
{source_type_name}
来源：{result.source_name}
相关度：{result.score:.1%}
内容：
{result.content[:500]}
"""

            part_length = len(context_part)
            if total_length + part_length > max_length:
                break

            context_parts.append(context_part)
            total_length += part_length

        context_text = "\n".join(context_parts)
        if not context_text:
            context_text = "暂未找到相关参考资料。"

        return RAGContext(
            query=query,
            search_results=search_results,
            context_text=context_text,
            total_tokens=total_length // 2  # 估算token数
        )

    async def chat_with_rag(
            self,
            query: str,
            history: List[ChatMessage] = None,
            doc_type: str = None,
            stream: bool = False,
            top_k: int = 5
    ) -> Dict[str, Any]:
        """
        基于RAG的聊天

        Args:
            query: 用户问题
            history: 对话历史
            doc_type: 文档类型过滤
            stream: 是否流式输出
            top_k: 检索数量

        Returns:
            响应结果
        """
        # 1. 检索相关文档（带重排序）
        search_results = await self.search_with_rerank(
            query=query,
            top_k=top_k,
            doc_type=doc_type
        )

        # 2. 构建上下文
        rag_context = await self.build_context(query, search_results)

        # 3. 构建系统提示
        system_prompt = self.LEGAL_SYSTEM_PROMPT.format(context=rag_context.context_text)

        # 4. 构建消息列表
        messages = [ChatMessage(role="system", content=system_prompt)]

        # 添加对话历史
        if history:
            # 限制历史长度
            max_history = 10
            messages.extend(history[-max_history:])

        # 添加当前问题
        messages.append(ChatMessage(role="user", content=query))

        # 5. 调用LLM
        llm_service = self._get_llm_service()

        if stream:
            # 流式响应
            return {
                "stream": llm_service.chat_stream(messages),
                "search_results": search_results,
                "context": rag_context
            }
        else:
            # 同步响应
            response = await llm_service.chat(messages)

            return {
                "content": response.content,
                "tokens_used": response.tokens_used,
                "search_results": search_results,
                "context": rag_context,
                "model": response.model
            }

    async def multi_query_search(
            self,
            query: str,
            top_k: int = 5,
            doc_type: str = None
    ) -> List[SearchResult]:
        """
        多查询检索

        Args:
            query: 原始查询
            top_k: 每个查询返回数量
            doc_type: 文档类型

        Returns:
            合并去重后的结果
        """
        # 扩展查询
        queries = [query]

        # 根据查询内容生成扩展查询
        if "违法解除" in query:
            queries.extend([
                "劳动合同法 违法解除 赔偿金",
                "用人单位 单方解除 程序违法"
            ])
        elif "加班" in query:
            queries.extend([
                "加班费 计算标准 工资",
                "劳动法 延长工作时间 报酬"
            ])
        elif "工伤" in query:
            queries.extend([
                "工伤保险条例 工伤认定",
                "工伤赔偿标准"
            ])

        # 合并结果
        all_results = {}
        for q in queries:
            results = await self.search(q, top_k=top_k, doc_type=doc_type)
            for r in results:
                # 使用source_id去重
                key = f"{r.source_type}_{r.source_id}"
                if key not in all_results or r.score > all_results[key].score:
                    all_results[key] = r

        # 按相似度排序
        sorted_results = sorted(all_results.values(), key=lambda x: x.score, reverse=True)
        return sorted_results[:top_k * 2]

    async def add_document(
            self,
            content: str,
            doc_type: str,
            source_name: str,
            doc_id: int,
            metadata: Dict[str, Any] = None
    ) -> int:
        """
        添加文档到知识库

        Args:
            content: 文档内容
            doc_type: 文档类型
            source_name: 来源名称
            doc_id: 文档ID
            metadata: 元数据

        Returns:
            向量ID
        """
        # 分块处理长文本
        if len(content) > 1000:
            chunks = self._split_text(content)
            vector_ids = []
            for i, chunk in enumerate(chunks):
                chunk_metadata = {
                    **(metadata or {}),
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
                vid = await self.add_document(
                    content=chunk,
                    doc_type=doc_type,
                    source_name=f"{source_name} (第{i+1}部分)",
                    doc_id=doc_id * 1000 + i,  # 生成唯一ID
                    metadata=chunk_metadata
                )
                vector_ids.append(vid)
            return vector_ids[0] if vector_ids else 0

        # 生成嵌入向量
        embedding_service = self._get_embedding_service()
        embedding = await embedding_service.embed(content)

        # 存储到向量数据库
        vector_store = self._get_vector_store()
        doc_id = await vector_store.insert_document(
            doc_id=doc_id,
            doc_type=doc_type,
            title=source_name,
            content=content,
            source=metadata.get("source", "") if metadata else "",
            embedding=embedding,
            metadata=metadata or {}
        )

        return doc_id

    def _split_text(self, text: str) -> List[str]:
        """
        分割长文本

        Args:
            text: 原始文本

        Returns:
            文本块列表
        """
        chunks = []
        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + self.CHUNK_SIZE
            if end >= text_length:
                chunks.append(text[start:])
                break

            # 尝试在句子边界分割
            last_period = text.rfind("。", start, end)
            last_newline = text.rfind("\n", start, end)
            split_pos = max(last_period, last_newline)

            if split_pos > start:
                chunks.append(text[start:split_pos + 1])
                start = split_pos + 1
            else:
                chunks.append(text[start:end])
                start = end - self.CHUNK_OVERLAP

        return chunks

    async def delete_document(self, doc_id: int, doc_type: str = None) -> bool:
        """
        删除文档

        Args:
            doc_id: 文档ID
            doc_type: 文档类型

        Returns:
            是否成功
        """
        vector_store = self._get_vector_store()
        return await vector_store.delete_by_source_id(doc_id, doc_type)

    async def get_stats(self) -> Dict[str, Any]:
        """获取RAG统计信息"""
        vector_store = self._get_vector_store()
        return await vector_store.get_collection_stats()