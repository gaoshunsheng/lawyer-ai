"""
智谱AI LLM服务实现
"""
import logging
from typing import List, Optional, Dict, Any, AsyncGenerator
import httpx
import json

from app.services.llm import BaseLLMService, ChatMessage, LLMResponse
from app.core.config import settings

logger = logging.getLogger(__name__)


class ZhipuLLMService(BaseLLMService):
    """智谱AI LLM服务"""

    def __init__(self):
        self.api_key = settings.ZHIPU_API_KEY
        self.api_base = "https://open.bigmodel.cn/api/paas/v4"
        self.model = settings.ZHIPU_MODEL
        self.embedding_model = "embedding-2"

    async def _get_token(self) -> str:
        """获取访问令牌"""
        # 智谱AI使用JWT认证，这里简化处理
        # 实际应该使用官方SDK或实现JWT认证
        return self.api_key

    async def _call_api(
            self,
            endpoint: str,
            data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """调用智谱AI API"""
        token = await self._get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            url = f"{self.api_base}/{endpoint}"
            response = await client.post(url, json=data, headers=headers)
            response.raise_for_status()
            return response.json()

    async def chat(
            self,
            messages: List[ChatMessage],
            temperature: float = 0.7,
            max_tokens: int = 2000,
            **kwargs
    ) -> LLMResponse:
        """同步聊天"""
        formatted_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        data = {
            "model": self.model,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **kwargs
        }

        try:
            result = await self._call_api("chat/completions", data)

            return LLMResponse(
                content=result["choices"][0]["message"]["content"],
                tokens_used=result.get("usage", {}).get("total_tokens", 0),
                model=result.get("model", self.model),
                finish_reason=result["choices"][0].get("finish_reason", "stop")
            )
        except Exception as e:
            logger.error(f"智谱AI API调用失败: {e}")
            raise

    async def chat_stream(
            self,
            messages: List[ChatMessage],
            temperature: float = 0.7,
            max_tokens: int = 2000,
            **kwargs
    ) -> AsyncGenerator[str, None]:
        """流式聊天"""
        formatted_messages = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]

        data = {
            "model": self.model,
            "messages": formatted_messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": True,
            **kwargs
        }

        token = await self._get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            url = f"{self.api_base}/chat/completions"
            async with client.stream("POST", url, json=data, headers=headers) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        line = line[6:]
                        if line == "[DONE]":
                            break
                        try:
                            chunk = json.loads(line)
                            if chunk["choices"][0].get("delta", {}).get("content"):
                                yield chunk["choices"][0]["delta"]["content"]
                        except Exception:
                            continue

    async def embed(self, text: str) -> List[float]:
        """生成文本嵌入向量"""
        data = {
            "model": self.embedding_model,
            "input": text
        }

        try:
            result = await self._call_api("embeddings", data)
            return result["data"][0]["embedding"]
        except Exception as e:
            logger.error(f"智谱AI Embedding API调用失败: {e}")
            raise

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """批量生成文本嵌入向量"""
        # 智谱AI可能不支持批量，逐个处理
        embeddings = []
        for text in texts:
            embedding = await self.embed(text)
            embeddings.append(embedding)
        return embeddings
