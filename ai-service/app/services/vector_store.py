"""
向量存储服务 - 完善版
支持知识库数据的向量化和检索
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
import asyncio
import json

from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
from app.core.config import settings

logger = logging.getLogger(__name__)


class VectorStoreService:
    """向量存储服务 - 基于Milvus"""

    # 集合名称
    LAW_COLLECTION = "law_articles"
    CASE_COLLECTION = "precedent_cases"
    DOCUMENT_COLLECTION = "knowledge_docs"

    # 集合字段定义
    LAW_FIELDS = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=False),
        FieldSchema(name="law_id", dtype=DataType.INT64),
        FieldSchema(name="law_name", dtype=DataType.VARCHAR, max_length=200),
        FieldSchema(name="article_number", dtype=DataType.VARCHAR, max_length=50),
        FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=5000),
        FieldSchema(name="metadata", dtype=DataType.VARCHAR, max_length=2000),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1024)
    ]

    CASE_FIELDS = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=False),
        FieldSchema(name="case_id", dtype=DataType.INT64),
        FieldSchema(name="case_number", dtype=DataType.VARCHAR, max_length=100),
        FieldSchema(name="case_type", dtype=DataType.VARCHAR, max_length=50),
        FieldSchema(name="court", dtype=DataType.VARCHAR, max_length=100),
        FieldSchema(name="judgment_date", dtype=DataType.VARCHAR, max_length=20),
        FieldSchema(name="summary", dtype=DataType.VARCHAR, max_length=2000),
        FieldSchema(name="result", dtype=DataType.VARCHAR, max_length=100),
        FieldSchema(name="metadata", dtype=DataType.VARCHAR, max_length=2000),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1024)
    ]

    DOCUMENT_FIELDS = [
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=False),
        FieldSchema(name="doc_id", dtype=DataType.INT64),
        FieldSchema(name="doc_type", dtype=DataType.VARCHAR, max_length=50),
        FieldSchema(name="title", dtype=DataType.VARCHAR, max_length=500),
        FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=5000),
        FieldSchema(name="source", dtype=DataType.VARCHAR, max_length=200),
        FieldSchema(name="metadata", dtype=DataType.VARCHAR, max_length=2000),
        FieldSchema(name="created_at", dtype=DataType.INT64),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=1024)
    ]

    def __init__(self):
        self._connected = False
        self._collections = {}
        self._embedding_dim = settings.EMBEDDING_DIMENSION

    def _connect(self):
        """连接Milvus"""
        if not self._connected:
            try:
                connections.connect(
                    alias="default",
                    host=settings.MILVUS_HOST,
                    port=settings.MILVUS_PORT,
                    timeout=10
                )
                self._connected = True
                logger.info(f"Milvus连接成功: {settings.MILVUS_HOST}:{settings.MILVUS_PORT}")
            except Exception as e:
                logger.error(f"Milvus连接失败: {e}")
                raise

    def disconnect(self):
        """断开Milvus连接"""
        if self._connected:
            try:
                connections.disconnect("default")
                self._connected = False
                logger.info("Milvus连接已断开")
            except Exception as e:
                logger.error(f"断开Milvus连接失败: {e}")

    def _get_collection(self, name: str) -> Optional[Collection]:
        """获取集合"""
        self._connect()

        if name in self._collections:
            return self._collections[name]

        if utility.has_collection(name):
            collection = Collection(name=name)
            collection.load()
            self._collections[name] = collection
            return collection

        return None

    async def create_collections(self):
        """创建向量集合"""
        self._connect()

        # 创建法条向量集合
        if not utility.has_collection(self.LAW_COLLECTION):
            schema = CollectionSchema(fields=self.LAW_FIELDS, description="法条向量集合")
            collection = Collection(name=self.LAW_COLLECTION, schema=schema)
            index_params = {
                "metric_type": "COSINE",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 1024}
            }
            collection.create_index(field_name="embedding", index_params=index_params)
            logger.info(f"集合 {self.LAW_COLLECTION} 创建成功")

        # 创建案例向量集合
        if not utility.has_collection(self.CASE_COLLECTION):
            schema = CollectionSchema(fields=self.CASE_FIELDS, description="案例向量集合")
            collection = Collection(name=self.CASE_COLLECTION, schema=schema)
            index_params = {
                "metric_type": "COSINE",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 1024}
            }
            collection.create_index(field_name="embedding", index_params=index_params)
            logger.info(f"集合 {self.CASE_COLLECTION} 创建成功")

        # 创建通用知识文档集合
        if not utility.has_collection(self.DOCUMENT_COLLECTION):
            schema = CollectionSchema(fields=self.DOCUMENT_FIELDS, description="知识文档向量集合")
            collection = Collection(name=self.DOCUMENT_COLLECTION, schema=schema)
            index_params = {
                "metric_type": "COSINE",
                "index_type": "IVF_FLAT",
                "params": {"nlist": 1024}
            }
            collection.create_index(field_name="embedding", index_params=index_params)
            logger.info(f"集合 {self.DOCUMENT_COLLECTION} 创建成功")

    def _get_collection_name(self, doc_type: str) -> str:
        """根据文档类型获取集合名称"""
        type_mapping = {
            "law": self.LAW_COLLECTION,
            "case": self.CASE_COLLECTION,
            "document": self.DOCUMENT_COLLECTION,
            "internal": self.DOCUMENT_COLLECTION,
            "article": self.DOCUMENT_COLLECTION
        }
        return type_mapping.get(doc_type, self.DOCUMENT_COLLECTION)

    async def insert_law(
            self,
            law_id: int,
            law_name: str,
            article_number: str,
            content: str,
            embedding: List[float],
            metadata: Dict[str, Any] = None
    ) -> int:
        """
        插入法条向量

        Args:
            law_id: 法条ID（数据库主键）
            law_name: 法律名称
            article_number: 条款号
            content: 条款内容
            embedding: 嵌入向量
            metadata: 元数据

        Returns:
            向量ID
        """
        self._connect()
        collection_name = self.LAW_COLLECTION

        # 确保集合存在
        await self.create_collections()
        collection = self._get_collection(collection_name)

        # 生成向量ID
        vector_id = law_id

        # 准备数据
        metadata_str = json.dumps(metadata or {}, ensure_ascii=False)[:2000]
        data = [
            [vector_id],           # id
            [law_id],              # law_id
            [law_name[:200]],      # law_name
            [article_number[:50]], # article_number
            [content[:5000]],      # content
            [metadata_str],        # metadata
            [embedding]            # embedding
        ]

        # 插入数据
        collection.insert(data)
        collection.flush()

        logger.info(f"法条向量插入成功: {law_name} 第{article_number}条")
        return vector_id

    async def insert_case(
            self,
            case_id: int,
            case_number: str,
            case_type: str,
            court: str,
            judgment_date: str,
            summary: str,
            result: str,
            embedding: List[float],
            metadata: Dict[str, Any] = None
    ) -> int:
        """
        插入案例向量

        Args:
            case_id: 案例ID（数据库主键）
            case_number: 案号
            case_type: 案件类型
            court: 法院
            judgment_date: 判决日期
            summary: 摘要
            result: 判决结果
            embedding: 嵌入向量
            metadata: 元数据

        Returns:
            向量ID
        """
        self._connect()
        collection_name = self.CASE_COLLECTION

        # 确保集合存在
        await self.create_collections()
        collection = self._get_collection(collection_name)

        # 生成向量ID
        vector_id = case_id

        # 准备数据
        metadata_str = json.dumps(metadata or {}, ensure_ascii=False)[:2000]
        data = [
            [vector_id],           # id
            [case_id],             # case_id
            [case_number[:100]],   # case_number
            [case_type[:50]],      # case_type
            [court[:100]],         # court
            [judgment_date[:20]],  # judgment_date
            [summary[:2000]],      # summary
            [result[:100]],        # result
            [metadata_str],        # metadata
            [embedding]            # embedding
        ]

        # 插入数据
        collection.insert(data)
        collection.flush()

        logger.info(f"案例向量插入成功: {case_number}")
        return vector_id

    async def insert_document(
            self,
            doc_id: int,
            doc_type: str,
            title: str,
            content: str,
            source: str,
            embedding: List[float],
            metadata: Dict[str, Any] = None
    ) -> int:
        """
        插入通用文档向量

        Args:
            doc_id: 文档ID（数据库主键）
            doc_type: 文档类型
            title: 标题
            content: 内容
            source: 来源
            embedding: 嵌入向量
            metadata: 元数据

        Returns:
            向量ID
        """
        self._connect()
        collection_name = self.DOCUMENT_COLLECTION

        # 确保集合存在
        await self.create_collections()
        collection = self._get_collection(collection_name)

        # 生成向量ID
        vector_id = doc_id

        # 准备数据
        metadata_str = json.dumps(metadata or {}, ensure_ascii=False)[:2000]
        created_at = int(datetime.now().timestamp())
        data = [
            [vector_id],          # id
            [doc_id],             # doc_id
            [doc_type[:50]],      # doc_type
            [title[:500]],        # title
            [content[:5000]],     # content
            [source[:200]],       # source
            [metadata_str],       # metadata
            [created_at],         # created_at
            [embedding]           # embedding
        ]

        # 插入数据
        collection.insert(data)
        collection.flush()

        logger.info(f"文档向量插入成功: {title[:50]}")
        return vector_id

    async def batch_insert(
            self,
            items: List[Dict[str, Any]],
            doc_type: str
    ) -> List[int]:
        """
        批量插入向量

        Args:
            items: 数据列表
            doc_type: 文档类型

        Returns:
            向量ID列表
        """
        vector_ids = []
        for item in items:
            if doc_type == "law":
                vid = await self.insert_law(
                    law_id=item["law_id"],
                    law_name=item["law_name"],
                    article_number=item["article_number"],
                    content=item["content"],
                    embedding=item["embedding"],
                    metadata=item.get("metadata")
                )
            elif doc_type == "case":
                vid = await self.insert_case(
                    case_id=item["case_id"],
                    case_number=item["case_number"],
                    case_type=item["case_type"],
                    court=item["court"],
                    judgment_date=item["judgment_date"],
                    summary=item["summary"],
                    result=item["result"],
                    embedding=item["embedding"],
                    metadata=item.get("metadata")
                )
            else:
                vid = await self.insert_document(
                    doc_id=item["doc_id"],
                    doc_type=doc_type,
                    title=item.get("title", ""),
                    content=item["content"],
                    source=item.get("source", ""),
                    embedding=item["embedding"],
                    metadata=item.get("metadata")
                )
            vector_ids.append(vid)

        logger.info(f"批量插入 {len(vector_ids)} 条向量数据")
        return vector_ids

    async def search(
            self,
            query_embedding: List[float],
            top_k: int = 10,
            doc_type: str = None,
            min_score: float = 0.0,
            filters: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        向量检索

        Args:
            query_embedding: 查询向量
            top_k: 返回数量
            doc_type: 文档类型过滤 (law, case, document, None表示所有)
            min_score: 最小相似度
            filters: 额外过滤条件

        Returns:
            检索结果列表
        """
        self._connect()
        results = []

        # 确定向量维度
        if len(query_embedding) != self._embedding_dim:
            logger.warning(f"向量维度不匹配: 期望{self._embedding_dim}, 实际{len(query_embedding)}")
            # 尝试调整维度
            if len(query_embedding) < self._embedding_dim:
                query_embedding = query_embedding + [0.0] * (self._embedding_dim - len(query_embedding))
            else:
                query_embedding = query_embedding[:self._embedding_dim]

        # 确定要搜索的集合
        if doc_type:
            collection_names = [self._get_collection_name(doc_type)]
        else:
            collection_names = [self.LAW_COLLECTION, self.CASE_COLLECTION, self.DOCUMENT_COLLECTION]

        for collection_name in collection_names:
            collection = self._get_collection(collection_name)
            if collection is None:
                logger.warning(f"集合 {collection_name} 不存在")
                continue

            try:
                # 执行检索
                search_params = {"metric_type": "COSINE", "params": {"nprobe": 10}}

                # 根据集合类型确定输出字段
                if collection_name == self.LAW_COLLECTION:
                    output_fields = ["law_id", "law_name", "article_number", "content", "metadata"]
                elif collection_name == self.CASE_COLLECTION:
                    output_fields = ["case_id", "case_number", "case_type", "court",
                                    "judgment_date", "summary", "result", "metadata"]
                else:
                    output_fields = ["doc_id", "doc_type", "title", "content", "source", "metadata"]

                search_results = collection.search(
                    data=[query_embedding],
                    anns_field="embedding",
                    param=search_params,
                    limit=top_k,
                    output_fields=output_fields
                )

                # 处理结果
                for hits in search_results:
                    for hit in hits:
                        score = hit.score
                        if score >= min_score:
                            entity = hit.entity

                            if collection_name == self.LAW_COLLECTION:
                                result = {
                                    "id": hit.id,
                                    "score": score,
                                    "source_type": "law",
                                    "source_id": entity.get("law_id"),
                                    "source_name": entity.get("law_name", ""),
                                    "content": entity.get("content", ""),
                                    "metadata": self._parse_metadata(entity.get("metadata")),
                                    "extra": {
                                        "article_number": entity.get("article_number", "")
                                    }
                                }
                            elif collection_name == self.CASE_COLLECTION:
                                result = {
                                    "id": hit.id,
                                    "score": score,
                                    "source_type": "case",
                                    "source_id": entity.get("case_id"),
                                    "source_name": entity.get("case_number", ""),
                                    "content": entity.get("summary", ""),
                                    "metadata": self._parse_metadata(entity.get("metadata")),
                                    "extra": {
                                        "case_type": entity.get("case_type", ""),
                                        "court": entity.get("court", ""),
                                        "judgment_date": entity.get("judgment_date", ""),
                                        "result": entity.get("result", "")
                                    }
                                }
                            else:
                                result = {
                                    "id": hit.id,
                                    "score": score,
                                    "source_type": entity.get("doc_type", "document"),
                                    "source_id": entity.get("doc_id"),
                                    "source_name": entity.get("title", ""),
                                    "content": entity.get("content", ""),
                                    "metadata": self._parse_metadata(entity.get("metadata")),
                                    "extra": {
                                        "source": entity.get("source", "")
                                    }
                                }
                            results.append(result)

            except Exception as e:
                logger.error(f"检索集合 {collection_name} 失败: {e}")
                continue

        # 按相似度排序并返回top_k
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    async def delete_by_id(self, id: int, doc_type: str = None) -> bool:
        """
        根据ID删除向量

        Args:
            id: 向量ID
            doc_type: 文档类型

        Returns:
            是否成功
        """
        self._connect()

        try:
            if doc_type:
                collection_names = [self._get_collection_name(doc_type)]
            else:
                collection_names = [self.LAW_COLLECTION, self.CASE_COLLECTION, self.DOCUMENT_COLLECTION]

            for collection_name in collection_names:
                collection = self._get_collection(collection_name)
                if collection:
                    expr = f"id == {id}"
                    collection.delete(expr)
                    collection.flush()
                    logger.info(f"从集合 {collection_name} 删除向量ID: {id}")

            return True
        except Exception as e:
            logger.error(f"删除向量失败: {e}")
            return False

    async def delete_by_source_id(self, source_id: int, doc_type: str) -> bool:
        """
        根据源ID删除向量

        Args:
            source_id: 源数据ID（数据库主键）
            doc_type: 文档类型

        Returns:
            是否成功
        """
        self._connect()

        try:
            collection_name = self._get_collection_name(doc_type)
            collection = self._get_collection(collection_name)

            if collection:
                if doc_type == "law":
                    expr = f"law_id == {source_id}"
                elif doc_type == "case":
                    expr = f"case_id == {source_id}"
                else:
                    expr = f"doc_id == {source_id}"

                collection.delete(expr)
                collection.flush()
                logger.info(f"删除源ID {source_id} 的向量数据")

            return True
        except Exception as e:
            logger.error(f"删除向量失败: {e}")
            return False

    async def get_collection_stats(self) -> Dict[str, Any]:
        """获取集合统计信息"""
        self._connect()

        stats = {}
        for collection_name in [self.LAW_COLLECTION, self.CASE_COLLECTION, self.DOCUMENT_COLLECTION]:
            if utility.has_collection(collection_name):
                collection = Collection(name=collection_name)
                stats[collection_name] = {
                    "count": collection.num_entities,
                    "exists": True
                }
            else:
                stats[collection_name] = {
                    "count": 0,
                    "exists": False
                }

        return stats

    def _parse_metadata(self, metadata_str: str) -> Dict[str, Any]:
        """解析元数据JSON"""
        if not metadata_str:
            return {}
        try:
            return json.loads(metadata_str)
        except:
            return {}

    async def clear_collection(self, doc_type: str) -> bool:
        """
        清空指定类型的集合

        Args:
            doc_type: 文档类型

        Returns:
            是否成功
        """
        self._connect()

        try:
            collection_name = self._get_collection_name(doc_type)

            if utility.has_collection(collection_name):
                utility.drop_collection(collection_name)
                logger.info(f"已删除集合: {collection_name}")
                # 重新创建
                await self.create_collections()

            return True
        except Exception as e:
            logger.error(f"清空集合失败: {e}")
            return False
