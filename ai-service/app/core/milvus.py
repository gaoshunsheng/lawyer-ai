from pymilvus import connections, Collection, FieldSchema, CollectionSchema, DataType, utility
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# 集合名称
LAW_COLLECTION = "law_articles"
CASE_COLLECTION = "precedent_cases"
DOCUMENT_COLLECTION = "documents"


async def init_milvus():
    """初始化Milvus"""
    try:
        # 连接Milvus
        connections.connect(
            alias="default",
            host=settings.MILVUS_HOST,
            port=settings.MILVUS_PORT
        )
        logger.info("Milvus连接成功")

        # 创建集合（如果不存在）
        await create_collections()

    except Exception as e:
        logger.error(f"Milvus初始化失败: {e}")
        raise


async def create_collections():
    """创建向量集合"""
    # 法条向量集合
    if not utility.has_collection(LAW_COLLECTION):
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=False),
            FieldSchema(name="law_id", dtype=DataType.INT64),
            FieldSchema(name="article_number", dtype=DataType.VARCHAR, max_length=50),
            FieldSchema(name="content", dtype=DataType.VARCHAR, max_length=5000),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=settings.EMBEDDING_DIMENSION)
        ]
        schema = CollectionSchema(fields=fields, description="法条向量集合")
        collection = Collection(name=LAW_COLLECTION, schema=schema)
        # 创建索引
        index_params = {
            "metric_type": "COSINE",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 1024}
        }
        collection.create_index(field_name="embedding", index_params=index_params)
        logger.info(f"集合 {LAW_COLLECTION} 创建成功")

    # 案例向量集合
    if not utility.has_collection(CASE_COLLECTION):
        fields = [
            FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=False),
            FieldSchema(name="case_id", dtype=DataType.INT64),
            FieldSchema(name="case_number", dtype=DataType.VARCHAR, max_length=100),
            FieldSchema(name="case_type", dtype=DataType.VARCHAR, max_length=50),
            FieldSchema(name="summary", dtype=DataType.VARCHAR, max_length=2000),
            FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=settings.EMBEDDING_DIMENSION)
        ]
        schema = CollectionSchema(fields=fields, description="案例向量集合")
        collection = Collection(name=CASE_COLLECTION, schema=schema)
        index_params = {
            "metric_type": "COSINE",
            "index_type": "IVF_FLAT",
            "params": {"nlist": 1024}
        }
        collection.create_index(field_name="embedding", index_params=index_params)
        logger.info(f"集合 {CASE_COLLECTION} 创建成功")


def get_collection(name: str) -> Collection:
    """获取集合"""
    return Collection(name=name)
