"""法规检索工具 - 向量检索 + 全文检索混合"""

import uuid

from sqlalchemy import and_, func, or_, select, text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models import Law, LawArticle, LawEmbedding


async def search_laws_vector(
    query_embedding: list[float],
    *,
    tenant_id: uuid.UUID | None = None,
    limit: int = 10,
    similarity_threshold: float = 0.5,
) -> list[dict]:
    """向量相似度检索法规"""
    async with AsyncSessionLocal() as session:
        stmt = (
            select(
                LawEmbedding,
                LawEmbedding.embedding.cosine_distance(query_embedding).label("distance"),
            )
            .where(LawEmbedding.embedding.cosine_distance(query_embedding) < (1 - similarity_threshold))
            .order_by(LawEmbedding.embedding.cosine_distance(query_embedding))
            .limit(limit)
        )

        result = await session.execute(stmt)
        rows = result.all()

        results = []
        seen_law_ids = set()
        for embedding, distance in rows:
            if embedding.law_id in seen_law_ids and embedding.chunk_type == "article":
                continue
            seen_law_ids.add(embedding.law_id)

            law_stmt = select(Law).where(Law.id == embedding.law_id)
            law_result = await session.execute(law_stmt)
            law = law_result.scalar_one_or_none()

            results.append({
                "law_id": str(embedding.law_id),
                "article_number": embedding.article_number,
                "chunk_text": embedding.chunk_text,
                "chunk_type": embedding.chunk_type,
                "similarity": round(1 - distance, 4),
                "law_title": law.title if law else None,
                "law_type": law.law_type if law else None,
            })

        return results


async def search_laws_fulltext(
    query: str,
    *,
    tenant_id: uuid.UUID | None = None,
    limit: int = 10,
) -> list[dict]:
    """全文检索法规 (PostgreSQL tsvector)"""
    async with AsyncSessionLocal() as session:
        stmt = (
            select(
                Law,
                func.ts_rank_cd(
                    func.to_tsvector("simple", Law.title + " " + Law.full_text),
                    func.plainto_tsquery("simple", query),
                ).label("rank"),
            )
            .where(
                func.to_tsvector("simple", Law.title + " " + Law.full_text).op("@@")(
                    func.plainto_tsquery("simple", query)
                )
            )
            .order_by(text("rank DESC"))
            .limit(limit)
        )

        if tenant_id:
            stmt = stmt.where(or_(Law.tenant_id == tenant_id, Law.tenant_id.is_(None)))

        result = await session.execute(stmt)
        rows = result.all()

        return [
            {
                "law_id": str(law.id),
                "law_title": law.title,
                "law_type": law.law_type,
                "effective_date": str(law.effective_date) if law.effective_date else None,
                "rank": float(rank),
            }
            for law, rank in rows
        ]


async def search_laws_hybrid(
    query_embedding: list[float],
    query_text: str,
    *,
    tenant_id: uuid.UUID | None = None,
    limit: int = 10,
    vector_weight: float = 0.7,
    text_weight: float = 0.3,
) -> list[dict]:
    """混合检索: 向量 + 全文 → RRF (Reciprocal Rank Fusion)"""
    vector_results = await search_laws_vector(query_embedding, tenant_id=tenant_id, limit=limit * 2)
    text_results = await search_laws_fulltext(query_text, tenant_id=tenant_id, limit=limit * 2)

    # RRF fusion
    k = 60
    scores: dict[str, dict] = {}

    for rank, item in enumerate(vector_results):
        law_id = item["law_id"]
        scores[law_id] = {**item, "rrf_score": 0.0}
        scores[law_id]["rrf_score"] += vector_weight / (k + rank + 1)

    for rank, item in enumerate(text_results):
        law_id = item["law_id"]
        if law_id in scores:
            scores[law_id]["rrf_score"] += text_weight / (k + rank + 1)
            if "law_title" not in scores[law_id] or not scores[law_id]["law_title"]:
                scores[law_id]["law_title"] = item.get("law_title")
        else:
            scores[law_id] = {**item, "rrf_score": text_weight / (k + rank + 1)}

    sorted_results = sorted(scores.values(), key=lambda x: x["rrf_score"], reverse=True)
    return sorted_results[:limit]
