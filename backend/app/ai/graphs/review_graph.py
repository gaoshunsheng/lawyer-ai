# backend/app/ai/graphs/review_graph.py
from __future__ import annotations

import json
from typing import TypedDict

from langgraph.graph import END, StateGraph

from app.ai.prompts.review_prompts import REVIEW_SYSTEM_PROMPT, REVIEW_TEMPLATE
from app.core.config import settings


class ReviewState(TypedDict):
    contract_text: str
    user_concerns: str
    result: dict
    error: str


async def review_node(state: ReviewState) -> ReviewState:
    """Call GLM-5.1 for comprehensive contract review."""
    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(
            api_key=settings.ZHIPU_API_KEY,
            base_url=settings.ZHIPU_BASE_URL,
        )

        prompt = REVIEW_TEMPLATE.format(
            contract_text=state["contract_text"],
            user_concerns=state.get("user_concerns", "无特殊关注问题"),
        )

        response = await client.chat.completions.create(
            model="glm-5.1",
            messages=[
                {"role": "system", "content": REVIEW_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.2,
            max_tokens=8192,
            response_format={"type": "json_object"},
        )

        state["result"] = json.loads(response.choices[0].message.content or "{}")
    except Exception as e:
        state["error"] = str(e)

    return state


def build_review_graph() -> StateGraph:
    workflow = StateGraph(ReviewState)
    workflow.add_node("review", review_node)
    workflow.set_entry_point("review")
    workflow.add_edge("review", END)
    return workflow.compile()
