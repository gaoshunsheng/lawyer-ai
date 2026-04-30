"""
OpenAI LLM服务实现
"""
import logging
from typing import List, Optional, Dict, Any, AsyncGenerator
import httpx

from app.services.llm import BaseLLMService, ChatMessage, LLMResponse
from app.core.config import settings

logger = logging.getLogger(__name__)


class OpenAILLMService(BaseLLMService):
    """OpenAI LLM服务"""

    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.api_base = settings.OPENAI_API_BASE or "https://api.openai.com/v1"
        self.model = settings.OPENAI_MODEL
        self.embedding_model = "text-embedding-3-small"

    async def _call_api(
            self,
            endpoint: str,
            data: Dict[str, Any],
            stream: bool = False
    ) -> Dict[str, Any]:
        """调用OpenAI API"""
        headers = {
            "Authorization": f"Bearer {self.api_key}",
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
            logger.error(f"OpenAI API调用失败: {e}")
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

        headers = {
            "Authorization": f"Bearer {self.api_key}",
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
                            import json
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
            logger.error(f"OpenAI Embedding API调用失败: {e}")
            raise

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """批量生成文本嵌入向量"""
        data = {
            "model": self.embedding_model,
            "input": texts
        }

        try:
            result = await self._call_api("embeddings", data)
            # 按原始顺序返回
            embeddings = {item["index"]: item["embedding"] for item in result["data"]}
            return [embeddings[i] for i in range(len(texts))]
        except Exception as e:
            logger.error(f"OpenAI Embedding API批量调用失败: {e}")
            raise
