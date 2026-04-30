"""
本地嵌入服务 - 使用sentence-transformers
"""
import logging
from typing import List
import asyncio

from app.services.llm import BaseLLMService, ChatMessage, LLMResponse
from app.core.config import settings

logger = logging.getLogger(__name__)


class LocalEmbeddingService(BaseLLMService):
    """本地嵌入服务"""

    def __init__(self):
        self._model = None
        self._model_name = settings.EMBEDDING_MODEL

    def _load_model(self):
        """延迟加载模型"""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                logger.info(f"正在加载嵌入模型: {self._model_name}")
                self._model = SentenceTransformer(self._model_name)
                logger.info("嵌入模型加载完成")
            except ImportError:
                logger.warning("sentence-transformers未安装，使用模拟向量")
                self._model = None
            except Exception as e:
                logger.error(f"加载嵌入模型失败: {e}")
                self._model = None

    async def chat(
            self,
            messages: List[ChatMessage],
            temperature: float = 0.7,
            max_tokens: int = 2000,
            **kwargs
    ) -> LLMResponse:
        """本地嵌入服务不支持聊天"""
        raise NotImplementedError("本地嵌入服务不支持聊天功能")

    async def chat_stream(
            self,
            messages: List[ChatMessage],
            temperature: float = 0.7,
            max_tokens: int = 2000,
            **kwargs
    ):
        """本地嵌入服务不支持聊天"""
        raise NotImplementedError("本地嵌入服务不支持聊天功能")

    async def embed(self, text: str) -> List[float]:
        """生成文本嵌入向量"""
        self._load_model()

        if self._model is not None:
            # 使用sentence-transformers生成向量
            loop = asyncio.get_event_loop()
            embedding = await loop.run_in_executor(
                None,
                lambda: self._model.encode(text, convert_to_numpy=True).tolist()
            )
            return embedding
        else:
            # 使用模拟向量
            import hashlib
            import random
            text_hash = hashlib.md5(text.encode()).hexdigest()
            random.seed(int(text_hash[:8], 16))
            embedding = [random.uniform(-1, 1) for _ in range(settings.EMBEDDING_DIMENSION)]
            # 归一化
            norm = sum(x * x for x in embedding) ** 0.5
            return [x / norm for x in embedding]

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """批量生成文本嵌入向量"""
        self._load_model()

        if self._model is not None:
            # 使用sentence-transformers批量生成向量
            loop = asyncio.get_event_loop()
            embeddings = await loop.run_in_executor(
                None,
                lambda: self._model.encode(texts, convert_to_numpy=True).tolist()
            )
            return embeddings
        else:
            # 逐个生成模拟向量
            return [await self.embed(text) for text in texts]
