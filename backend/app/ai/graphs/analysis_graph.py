# backend/app/ai/graphs/analysis_graph.py
from __future__ import annotations

import json
from typing import TypedDict

from langgraph.graph import END, StateGraph

from app.ai.prompts.analysis_prompts import ANALYSIS_SYSTEM_PROMPT, ANALYSIS_TEMPLATE
from app.core.config import settings


class AnalysisState(TypedDict):
    case_data: dict
    result: dict
    error: str


async def analyze_node(state: AnalysisState) -> AnalysisState:
    """Call GLM-5-Turbo for fast case analysis."""
    try:
        from openai import AsyncOpenAI

        client = AsyncOpenAI(
            api_key=settings.ZHIPU_API_KEY,
            base_url=settings.ZHIPU_BASE_URL,
        )

        case = state["case_data"]
        prompt = ANALYSIS_TEMPLATE.format(
            title=case.get("title", ""),
            case_type=case.get("case_type", ""),
            plaintiff=json.dumps(case.get("plaintiff", {}), ensure_ascii=False),
            defendant=json.dumps(case.get("defendant", {}), ensure_ascii=False),
            claim_amount=case.get("claim_amount", "未填写"),
            dispute_focus=", ".join(case.get("dispute_focus", [])) or "未填写",
            evidences=json.dumps(case.get("evidences", []), ensure_ascii=False),
            timeline=json.dumps(case.get("timeline", []), ensure_ascii=False),
        )

        response = await client.chat.completions.create(
            model="glm-5-turbo",
            messages=[
                {"role": "system", "content": ANALYSIS_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=4096,
            response_format={"type": "json_object"},
        )

        state["result"] = json.loads(response.choices[0].message.content or "{}")
    except Exception as e:
        state["error"] = str(e)

    return state


def build_analysis_graph() -> StateGraph:
    workflow = StateGraph(AnalysisState)
    workflow.add_node("analyze", analyze_node)
    workflow.set_entry_point("analyze")
    workflow.add_edge("analyze", END)
    return workflow.compile()
