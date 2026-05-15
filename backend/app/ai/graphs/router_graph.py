"""Router Agent - 根据请求类型路由到不同的AI处理图"""

from __future__ import annotations

from langgraph.graph import StateGraph

from app.ai.graphs.analysis_graph import build_analysis_graph
from app.ai.graphs.consult_graph import build_consult_graph
from app.ai.graphs.document_graph import build_document_graph
from app.ai.graphs.review_graph import build_review_graph

# 路由映射: route_name -> graph_builder
ROUTE_MAP: dict[str, callable] = {
    "consult": build_consult_graph,
    "document": build_document_graph,
    "analysis": build_analysis_graph,
    "review": build_review_graph,
}


def get_graph(route: str) -> StateGraph:
    """根据路由名称获取对应的已编译图

    Args:
        route: 路由名称 (consult, document, analysis, review)

    Returns:
        已编译的StateGraph

    Raises:
        ValueError: 未知路由名称
    """
    builder = ROUTE_MAP.get(route)
    if builder is None:
        raise ValueError(
            f"未知路由: {route!r}, 可用路由: {list(ROUTE_MAP.keys())}"
        )
    return builder()
