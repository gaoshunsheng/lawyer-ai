# backend/app/ai/graphs/document_graph.py
from __future__ import annotations

import json
from typing import TypedDict

from langgraph.graph import END, StateGraph

from app.ai.graphs._client import get_openai_client
from app.ai.prompts.document_prompts import DOCUMENT_GENERATION_TEMPLATE, DOCUMENT_SYSTEM_PROMPT


class DocumentState(TypedDict):
    template_name: str
    doc_type: str
    template_content: str
    variables: dict
    instructions: str
    case_info: str
    generated_content: str
    error: str


async def generate_document_node(state: DocumentState) -> DocumentState:
    """Call glm-5.1 to generate structured legal document."""
    try:
        client = get_openai_client()

        prompt = DOCUMENT_GENERATION_TEMPLATE.format(
            template_name=state["template_name"],
            doc_type=state["doc_type"],
            template_content=state["template_content"],
            variables=json.dumps(state.get("variables", {}), ensure_ascii=False, indent=2),
            instructions=state.get("instructions", "无特殊指令"),
            case_info=state.get("case_info", "未提供案件信息"),
        )

        response = await client.chat.completions.create(
            model="glm-5.1",
            messages=[
                {"role": "system", "content": DOCUMENT_SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=4096,
        )

        state["generated_content"] = response.choices[0].message.content or ""
    except Exception as e:
        state["error"] = str(e)

    return state


def build_document_graph() -> StateGraph:
    workflow = StateGraph(DocumentState)
    workflow.add_node("generate", generate_document_node)
    workflow.set_entry_point("generate")
    workflow.add_edge("generate", END)
    return workflow.compile()
