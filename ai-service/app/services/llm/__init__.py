"""
LLM服务基类和工厂
"""
from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, AsyncGenerator
from dataclasses import dataclass
import logging

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class ChatMessage:
    """聊天消息"""
    role: str  # system, user, assistant
    content: str


@dataclass
class LLMResponse:
    """LLM响应"""
    content: str
    tokens_used: int
    model: str
    finish_reason: str = "stop"


class BaseLLMService(ABC):
    """LLM服务基类"""

    @abstractmethod
    async def chat(
            self,
            messages: List[ChatMessage],
            temperature: float = 0.7,
            max_tokens: int = 2000,
            **kwargs
    ) -> LLMResponse:
        """
        同步聊天

        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数

        Returns:
            LLM响应
        """
        pass

    @abstractmethod
    async def chat_stream(
            self,
            messages: List[ChatMessage],
            temperature: float = 0.7,
            max_tokens: int = 2000,
            **kwargs
    ) -> AsyncGenerator[str, None]:
        """
        流式聊天

        Args:
            messages: 消息列表
            temperature: 温度参数
            max_tokens: 最大token数
            **kwargs: 其他参数

        Yields:
            生成的文本片段
        """
        pass

    @abstractmethod
    async def embed(self, text: str) -> List[float]:
        """
        生成文本嵌入向量

        Args:
            text: 输入文本

        Returns:
            嵌入向量
        """
        pass

    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """
        批量生成文本嵌入向量

        Args:
            texts: 输入文本列表

        Returns:
            嵌入向量列表
        """
        pass


class LLMFactory:
    """LLM服务工厂"""

    _instances: Dict[str, BaseLLMService] = {}

    @classmethod
    def get_llm_service(cls, provider: str = None) -> BaseLLMService:
        """
        获取LLM服务实例

        Args:
            provider: 提供商名称，默认使用配置中的提供商

        Returns:
            LLM服务实例
        """
        if provider is None:
            provider = settings.LLM_PROVIDER

        if provider not in cls._instances:
            if provider == "openai":
                from app.services.llm.openai_service import OpenAILLMService
                cls._instances[provider] = OpenAILLMService()
            elif provider == "zhipu":
                from app.services.llm.zhipu_service import ZhipuLLMService
                cls._instances[provider] = ZhipuLLMService()
            elif provider == "mock":
                from app.services.llm.mock_service import MockLLMService
                cls._instances[provider] = MockLLMService()
            else:
                raise ValueError(f"不支持的LLM提供商: {provider}")

        return cls._instances[provider]

    @classmethod
    def get_embedding_service(cls, provider: str = None) -> BaseLLMService:
        """
        获取嵌入服务实例

        Args:
            provider: 提供商名称

        Returns:
            嵌入服务实例
        """
        embedding_provider = settings.EMBEDDING_PROVIDER
        if embedding_provider == "openai":
            from app.services.llm.openai_service import OpenAILLMService
            return OpenAILLMService()
        else:
            from app.services.llm.local_embedding import LocalEmbeddingService
            return LocalEmbeddingService()
