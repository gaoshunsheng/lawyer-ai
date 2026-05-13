"""LangGraph 咨询Agent - 意图分类 → RAG检索 → LLM生成 → 流式输出"""

from __future__ import annotations

import json
import uuid
from dataclasses import dataclass, field
from typing import Any

import httpx
from langgraph.graph import END, StateGraph

from app.ai.chains.retrieval_chain import retrieve_context
from app.ai.prompts.legal_prompts import (
    INTENT_CLASSIFICATION_PROMPT,
    LEGAL_CONSULT_SYSTEM_PROMPT,
)
from app.core.config import settings


@dataclass
class AgentState:
    """咨询Agent状态"""
    question: str = ""
    intent: str = "general"  # law/case/both/general
    context: str = ""
    answer: str = ""
    tenant_id: uuid.UUID | None = None
    session_id: uuid.UUID | None = None
    user_id: uuid.UUID | None = None
    messages: list[dict[str, Any]] = field(default_factory=list)


async def classify_intent(state: AgentState) -> dict:
    """使用 GLM-4-Flash 进行意图分类"""
    prompt = INTENT_CLASSIFICATION_PROMPT.format(question=state.question)

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.ZHIPU_API_BASE}/chat/completions",
                headers={"Authorization": f"Bearer {settings.ZHIPU_API_KEY}"},
                json={
                    "model": "glm-4-flash",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.1,
                    "max_tokens": 10,
                },
                timeout=10.0,
            )
            response.raise_for_status()
            result = response.json()
            intent_text = result["choices"][0]["message"]["content"].strip().lower()

            if intent_text in ("law", "case", "both", "general"):
                return {"intent": intent_text}
    except Exception:
        pass

    return {"intent": "both"}


async def rag_retrieve(state: AgentState) -> dict:
    """RAG检索相关法律条文和案例"""
    if state.intent == "general":
        return {"context": ""}

    try:
        context = await retrieve_context(
            state.question,
            tenant_id=state.tenant_id,
            search_type=state.intent,
        )
        return {"context": context}
    except Exception as e:
        return {"context": f"检索时出错: {str(e)}"}


async def generate_answer(state: AgentState) -> dict:
    """使用 GLM-5.1 生成回答"""
    system_prompt = LEGAL_CONSULT_SYSTEM_PROMPT.format(
        context=state.context or "无相关检索结果",
        question=state.question,
    )

    messages = [{"role": "system", "content": system_prompt}]
    # 添加历史消息（最近10轮）
    for msg in state.messages[-10:]:
        messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
    messages.append({"role": "user", "content": state.question})

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{settings.ZHIPU_API_BASE}/chat/completions",
                headers={"Authorization": f"Bearer {settings.ZHIPU_API_KEY}"},
                json={
                    "model": "glm-5-turbo",
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 2048,
                },
                timeout=60.0,
            )
            response.raise_for_status()
            result = response.json()
            answer = result["choices"][0]["message"]["content"]
            return {"answer": answer}
    except Exception as e:
        return {"answer": f"生成回答时出错: {str(e)}"}


async def stream_answer(state: AgentState):
    """SSE流式生成回答"""
    system_prompt = LEGAL_CONSULT_SYSTEM_PROMPT.format(
        context=state.context or "无相关检索结果",
        question=state.question,
    )

    messages = [{"role": "system", "content": system_prompt}]
    for msg in state.messages[-10:]:
        messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
    messages.append({"role": "user", "content": state.question})

    try:
        async with httpx.AsyncClient() as client:
            async with client.stream(
                "POST",
                f"{settings.ZHIPU_API_BASE}/chat/completions",
                headers={"Authorization": f"Bearer {settings.ZHIPU_API_KEY}"},
                json={
                    "model": "glm-5-turbo",
                    "messages": messages,
                    "temperature": 0.7,
                    "max_tokens": 2048,
                    "stream": True,
                },
                timeout=60.0,
            ) as response:
                response.raise_for_status()
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]
                        if data == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data)
                            delta = chunk.get("choices", [{}])[0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue
    except Exception as e:
        yield f"\n\n[错误] {str(e)}"


def route_by_intent(state: AgentState) -> str:
    """根据意图路由"""
    if state.intent == "general":
        return "generate"
    return "retrieve"


def build_consult_graph() -> StateGraph:
    """构建咨询Agent的StateGraph"""
    graph = StateGraph(AgentState)

    # 添加节点
    graph.add_node("classify", classify_intent)
    graph.add_node("retrieve", rag_retrieve)
    graph.add_node("generate", generate_answer)

    # 设置入口
    graph.set_entry_point("classify")

    # 条件路由
    graph.add_conditional_edges("classify", route_by_intent, {
        "retrieve": "retrieve",
        "generate": "generate",
    })

    # 边
    graph.add_edge("retrieve", "generate")
    graph.add_edge("generate", END)

    return graph


# 编译graph
consult_graph = build_consult_graph().compile()


async def run_consultation(
    question: str,
    *,
    tenant_id: uuid.UUID | None = None,
    session_id: uuid.UUID | None = None,
    user_id: uuid.UUID | None = None,
    messages: list[dict] | None = None,
) -> str:
    """运行完整的咨询流程，返回最终回答"""
    state = AgentState(
        question=question,
        tenant_id=tenant_id,
        session_id=session_id,
        user_id=user_id,
        messages=messages or [],
    )

    result = await consult_graph.ainvoke(state)
    return result.get("answer", "")


async def run_consultation_stream(
    question: str,
    *,
    tenant_id: uuid.UUID | None = None,
    session_id: uuid.UUID | None = None,
    user_id: uuid.UUID | None = None,
    messages: list[dict] | None = None,
):
    """运行咨询流程，SSE流式输出"""
    # 先执行意图分类和检索
    state = AgentState(
        question=question,
        tenant_id=tenant_id,
        session_id=session_id,
        user_id=user_id,
        messages=messages or [],
    )

    # 1. 意图分类
    intent_result = await classify_intent(state)
    state.intent = intent_result["intent"]

    # 2. RAG检索
    retrieve_result = await rag_retrieve(state)
    state.context = retrieve_result["context"]

    # 3. 流式生成
    async for chunk in stream_answer(state):
        yield chunk
