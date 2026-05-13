"""将已导入的法条向量化并存入 law_embeddings 表"""

import asyncio
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import httpx
from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.ai.chains.retrieval_chain import generate_embedding
from app.core.config import settings
from app.models import Law, LawArticle
from app.models.embedding import LawEmbedding


async def vectorize():
    engine = create_async_engine(settings.DATABASE_URL)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as db:
        # 检查是否已有向量
        result = await db.execute(select(LawEmbedding).limit(1))
        if result.scalar_one_or_none():
            print("法条向量已存在，跳过")
            await engine.dispose()
            return

        # 查询所有法条
        result = await db.execute(
            select(LawArticle, Law)
            .join(Law, LawArticle.law_id == Law.id)
            .order_by(Law.id, LawArticle.article_number)
        )
        rows = result.all()
        print(f"共 {len(rows)} 条法条需要向量化")

        for i, (article, law) in enumerate(rows):
            text = f"{law.title} {article.article_number}\n{article.content}"
            try:
                embedding = await generate_embedding(text)
            except httpx.HTTPStatusError as e:
                print(f"  [{i+1}/{len(rows)}] 失败: {article.article_number} - {e.response.text}")
                continue

            row = LawEmbedding(
                law_id=law.id,
                article_id=article.id,
                article_number=article.article_number,
                chunk_text=text,
                chunk_type="article",
                embedding=embedding,
                metadata_={"law_title": law.title, "article_number": article.article_number},
            )
            db.add(row)
            print(f"  [{i+1}/{len(rows)}] {law.title} {article.article_number} (dim={len(embedding)})")

            # 每条都flush，避免长事务
            if (i + 1) % 5 == 0:
                await db.flush()

            # 限速：智谱API有QPS限制
            time.sleep(0.3)

        await db.commit()
        print("向量化完成！")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(vectorize())
