"""案例检索工具 - 向量检索"""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.models import CaseEmbedding, PrecedentCase


async def search_cases_vector(
    query_embedding: list[float],
    *,
    tenant_id: uuid.UUID | None = None,
    limit: int = 5,
    similarity_threshold: float = 0.5,
) -> list[dict]:
    """向量相似度检索案例"""
    async with AsyncSessionLocal() as session:
        stmt = (
            select(
                CaseEmbedding,
                CaseEmbedding.embedding.cosine_distance(query_embedding).label("distance"),
            )
            .where(CaseEmbedding.embedding.cosine_distance(query_embedding) < (1 - similarity_threshold))
            .order_by(CaseEmbedding.embedding.cosine_distance(query_embedding))
            .limit(limit)
        )

        result = await session.execute(stmt)
        rows = result.all()

        results = []
        for embedding, distance in rows:
            case_stmt = select(PrecedentCase).where(PrecedentCase.id == embedding.case_id)
            case_result = await session.execute(case_stmt)
            case = case_result.scalar_one_or_none()

            results.append({
                "case_id": str(embedding.case_id),
                "chunk_text": embedding.chunk_text,
                "chunk_type": embedding.chunk_type,
                "similarity": round(1 - distance, 4),
                "case_name": case.case_name if case else None,
                "court": case.court if case else None,
                "judgment_date": str(case.judgment_date) if case and case.judgment_date else None,
                "result": case.result if case else None,
            })

        return results
