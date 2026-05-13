"""RAG检索链 - 生成embedding → 混合检索 → 组装context"""

from app.ai.tools.search_cases import search_cases_vector
from app.ai.tools.search_laws import search_laws_hybrid


async def generate_embedding(text: str) -> list[float]:
    """调用智谱AI Embedding API生成向量"""
    import httpx

    from app.core.config import settings

    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{settings.ZHIPU_API_BASE}/embeddings",
            headers={"Authorization": f"Bearer {settings.ZHIPU_API_KEY}"},
            json={"model": "embedding-3", "input": text},
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()
        return data["data"][0]["embedding"]


async def retrieve_context(
    query: str,
    *,
    tenant_id=None,
    search_type: str = "both",
    law_limit: int = 5,
    case_limit: int = 3,
) -> str:
    """检索相关法律条文和案例，组装成context字符串"""
    query_embedding = await generate_embedding(query)
    parts = []

    if search_type in ("law", "both"):
        law_results = await search_laws_hybrid(
            query_embedding, query, tenant_id=tenant_id, limit=law_limit
        )
        if law_results:
            parts.append("【相关法律法规】")
            for i, item in enumerate(law_results, 1):
                parts.append(f"{i}. {item.get('law_title', '未知法规')}")
                if item.get("chunk_text"):
                    parts.append(f"   条文内容: {item['chunk_text'][:500]}")
                parts.append(f"   相似度: {item.get('similarity', 0):.2%}")

    if search_type in ("case", "both"):
        case_results = await search_cases_vector(
            query_embedding, tenant_id=tenant_id, limit=case_limit
        )
        if case_results:
            parts.append("\n【相关案例】")
            for i, item in enumerate(case_results, 1):
                parts.append(f"{i}. {item.get('case_name', '未知案例')}")
                parts.append(f"   法院: {item.get('court', '未知')}")
                if item.get("chunk_text"):
                    parts.append(f"   裁判要点: {item['chunk_text'][:300]}")

    return "\n".join(parts) if parts else "未找到相关法律资料。"
